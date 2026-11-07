import { createCipheriv, createDecipheriv, randomBytes, timingSafeEqual } from 'node:crypto';
import { promises as fs } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';

const DEFAULT_SCOPES = ['openid', 'profile', 'w_member_social'];
const STATE_LIFETIME = 10 * 60 * 1000;

export function config() {
  return {
    clientId: process.env.LINKEDIN_CLIENT_ID || '',
    clientSecret: process.env.LINKEDIN_CLIENT_SECRET || '',
    redirectUri: process.env.LINKEDIN_REDIRECT_URI || '',
    scopes: (process.env.LINKEDIN_SCOPES || DEFAULT_SCOPES.join(' ')).trim().split(/\s+/).filter(Boolean),
    version: process.env.LINKEDIN_API_VERSION || '202610',
    storeFile: resolve(process.env.MCP_STORE_FILE || join(homedir(), '.linkedin-mcp', 'auth.enc'))
  };
}

function getKey() {
  const value = process.env.MCP_ENCRYPTION_KEY_HEX || '';
  if (!/^[0-9a-fA-F]{64}$/.test(value)) {
    throw new Error('Set MCP_ENCRYPTION_KEY_HEX to 64 hexadecimal characters (openssl rand -hex 32).');
  }
  return Buffer.from(value, 'hex');
}

export function constantTimeEqual(left, right) {
  const a = Buffer.from(String(left));
  const b = Buffer.from(String(right));
  return a.length === b.length && timingSafeEqual(a, b);
}

export function validatePostUrn(urn) {
  if (typeof urn !== 'string' || !/^urn:li:(ugcPost|share|activity):[0-9]{6,30}$/.test(urn)) {
    throw new Error('Post URN must be a LinkedIn share, activity, or ugcPost URN.');
  }
  return urn;
}

export function profileLink(vanity) {
  if (typeof vanity !== 'string' || !/^[a-zA-Z0-9-]{2,100}$/.test(vanity)) {
    throw new Error('Invalid LinkedIn public profile slug.');
  }
  return 'https://www.linkedin.com/in/' + encodeURIComponent(vanity) + '/';
}

export function peopleSearchLink(query) {
  if (typeof query !== 'string' || query.trim().length < 2 || query.length > 200) {
    throw new Error('Search term must contain between 2 and 200 characters.');
  }
  const url = new URL('https://www.linkedin.com/search/results/people/');
  url.searchParams.set('keywords', query.trim());
  return url.toString();
}

export async function readState() {
  const { storeFile } = config();
  try {
    const payload = JSON.parse(await fs.readFile(storeFile, 'utf8'));
    const key = getKey();
    const decipher = createDecipheriv('aes-256-gcm', key, Buffer.from(payload.iv, 'base64'));
    decipher.setAuthTag(Buffer.from(payload.tag, 'base64'));
    const body = Buffer.concat([decipher.update(Buffer.from(payload.data, 'base64')), decipher.final()]);
    const state = JSON.parse(body.toString('utf8'));
    if (state.version !== 1) throw new Error('Unsupported token store version');
    return state;
  } catch (error) {
    if (error.code === 'ENOENT') return { version: 1, auth: null, pending: null };
    throw error;
  }
}

export async function writeState(state) {
  const key = getKey();
  const { storeFile } = config();
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  const data = Buffer.concat([cipher.update(JSON.stringify(state), 'utf8'), cipher.final()]);
  const payload = JSON.stringify({ iv: iv.toString('base64'), tag: cipher.getAuthTag().toString('base64'), data: data.toString('base64') });
  await fs.mkdir(dirname(storeFile), { recursive: true, mode: 0o700 });
  const temp = storeFile + '.' + process.pid + '.' + randomBytes(6).toString('hex') + '.tmp';
  try {
    await fs.writeFile(temp, payload, { mode: 0o600, flag: 'wx' });
    await fs.rename(temp, storeFile);
    await fs.chmod(storeFile, 0o600);
  } finally {
    await fs.rm(temp, { force: true });
  }
}

export async function startAuthorization() {
  const cfg = config();
  if (!cfg.clientId || !cfg.clientSecret || !cfg.redirectUri) {
    throw new Error('Configure LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET and LINKEDIN_REDIRECT_URI.');
  }
  const redirect = new URL(cfg.redirectUri);
  if (redirect.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(redirect.hostname)) {
    throw new Error('LinkedIn OAuth callback must use HTTPS.');
  }
  if (!redirect.pathname.endsWith('/oauth/callback')) {
    throw new Error('LINKEDIN_REDIRECT_URI must end with /oauth/callback.');
  }
  const state = randomBytes(32).toString('hex');
  const current = await readState();
  current.pending = { state, expiresAt: Date.now() + STATE_LIFETIME, scopes: cfg.scopes };
  await writeState(current);
  const url = new URL('https://www.linkedin.com/oauth/v2/authorization');
  url.searchParams.set('response_type', 'code');
  url.searchParams.set('client_id', cfg.clientId);
  url.searchParams.set('redirect_uri', cfg.redirectUri);
  url.searchParams.set('state', state);
  url.searchParams.set('scope', cfg.scopes.join(' '));
  return url.toString();
}

export async function finishAuthorization(code, receivedState) {
  const state = await readState();
  const pending = state.pending;
  if (!pending || Date.now() >= pending.expiresAt || !constantTimeEqual(receivedState, pending.state)) {
    throw new Error('OAuth state mismatch or expired login. Restart authorization.');
  }
  state.pending = null;
  await writeState(state);
  const cfg = config();
  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    code,
    redirect_uri: cfg.redirectUri,
    client_id: cfg.clientId,
    client_secret: cfg.clientSecret
  });
  const response = await fetch('https://www.linkedin.com/oauth/v2/accessToken', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
    signal: AbortSignal.timeout(20000)
  });
  const json = await response.json();
  if (!response.ok || !json.access_token) {
    throw new Error('LinkedIn OAuth exchange failed (HTTP ' + response.status + '). Check app permissions and callback URL.');
  }
  state.auth = {
    accessToken: json.access_token,
    expiresAt: Date.now() + Math.max(0, Number(json.expires_in) || 0) * 1000,
    scopes: typeof json.scope === 'string' ? json.scope.split(/\s+/) : pending.scopes,
    connectedAt: new Date().toISOString()
  };
  await writeState(state);
  return { connected: true, expiresAt: new Date(state.auth.expiresAt).toISOString(), scopes: state.auth.scopes };
}

export async function credentials() {
  const state = await readState();
  if (!state.auth) throw new Error('LinkedIn not connected. Call linkedin_authorize_url and complete OAuth first.');
  if (state.auth.expiresAt <= Date.now() + 30000) throw new Error('LinkedIn token expired. Re-authorize the account.');
  return state.auth;
}

export async function status() {
  const state = await readState();
  return {
    connected: !!state.auth && state.auth.expiresAt > Date.now(),
    expiresAt: state.auth ? new Date(state.auth.expiresAt).toISOString() : null,
    requestedScopes: state.auth?.scopes || [],
    writeActionsEnabled: process.env.MCP_ALLOW_WRITES === 'true',
    publicProfileSearch: 'LinkedIn website link only',
    invitations: 'Partner-restricted API; manual profile link only',
    developerPermissions: 'Actual availability depends on approved LinkedIn application scopes'
  };
}

export async function disconnect() {
  await writeState({ version: 1, auth: null, pending: null });
  return { disconnected: true };
}

export function requireWrites() {
  if (process.env.MCP_ALLOW_WRITES !== 'true') {
    throw new Error('Writes disabled. Set MCP_ALLOW_WRITES=true only when you intend to allow publishing and comments.');
  }
}

export function requireScope(auth, name) {
  if (!auth.scopes.includes(name)) {
    throw new Error('Missing LinkedIn scope ' + name + '. Request and obtain this permission in the LinkedIn Developer Portal, then re-authorize.');
  }
}
