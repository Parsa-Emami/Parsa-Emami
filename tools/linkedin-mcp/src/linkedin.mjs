import { config, credentials, requireScope, requireWrites, validatePostUrn } from './core.mjs';

function headers(auth) {
  return {
    Authorization: 'Bearer ' + auth.accessToken,
    'Content-Type': 'application/json',
    'X-Restli-Protocol-Version': '2.0.0',
    'Linkedin-Version': config().version
  };
}

export async function linkedinRequest(path, options = {}) {
  if (!/^\/(rest|v2)\/[a-zA-Z0-9/%:(),?&=._-]+$/.test(path)) throw new Error('Unsafe LinkedIn API path.');
  const auth = await credentials();
  const response = await fetch('https://api.linkedin.com' + path, {
    method: options.method || 'GET',
    headers: headers(auth),
    body: options.body ? JSON.stringify(options.body) : undefined,
    signal: AbortSignal.timeout(20000)
  });
  const raw = await response.text();
  let data = null;
  if (raw) {
    try { data = JSON.parse(raw); } catch { data = raw.slice(0, 400); }
  }
  if (!response.ok) {
    const safeCode = typeof data === 'object' && data !== null
      ? String(data.code || data.status || data.message || '').slice(0, 300)
      : '';
    throw new Error('LinkedIn HTTP ' + response.status + (safeCode ? ': ' + safeCode : '') + '. Check approved scopes, request format and rate limits.');
  }
  return { data, id: response.headers.get('x-restli-id') };
}

export async function getMe() {
  const response = await linkedinRequest('/v2/userinfo');
  const data = response.data;
  return {
    sub: data?.sub || null,
    name: data?.name || null,
    givenName: data?.given_name || null,
    familyName: data?.family_name || null,
    picture: data?.picture || null
  };
}

async function actor() {
  const auth = await credentials();
  requireScope(auth, 'w_member_social');
  const me = await getMe();
  if (!me.sub || !/^[A-Za-z0-9_-]+$/.test(me.sub)) {
    throw new Error('LinkedIn OpenID profile did not return a usable member ID.');
  }
  return 'urn:li:person:' + me.sub;
}

export async function publishText(text) {
  requireWrites();
  const author = await actor();
  const response = await linkedinRequest('/rest/posts', {
    method: 'POST',
    body: {
      author,
      commentary: text,
      visibility: 'PUBLIC',
      distribution: { feedDistribution: 'MAIN_FEED', targetEntities: [], thirdPartyDistributionChannels: [] },
      lifecycleState: 'PUBLISHED',
      isReshareDisabledByAuthor: false
    }
  });
  return { published: true, postUrn: response.id || null, note: 'Check LinkedIn for the published post.' };
}

export async function postComment(postUrn, text) {
  requireWrites();
  const urn = validatePostUrn(postUrn);
  const author = await actor();
  const response = await linkedinRequest('/rest/socialActions/' + encodeURIComponent(urn) + '/comments', {
    method: 'POST',
    body: { actor: author, message: { text } }
  });
  return { commented: true, commentUrn: response.id || null, note: 'This endpoint may require additional Community Management permissions.' };
}

export async function postAnalytics(postUrn, metric, aggregation) {
  const auth = await credentials();
  requireScope(auth, 'r_member_postAnalytics');
  const params = new URLSearchParams({ q: 'entity', entity: validatePostUrn(postUrn), queryType: metric, aggregation });
  const response = await linkedinRequest('/rest/memberCreatorPostAnalytics?' + params.toString());
  return response.data;
}
