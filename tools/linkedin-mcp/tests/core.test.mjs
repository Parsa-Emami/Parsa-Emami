import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { randomBytes } from 'node:crypto';
import { constantTimeEqual, peopleSearchLink, profileLink, readState, startAuthorization, validatePostUrn, writeState } from '../src/core.mjs';

test('safe public URLs and URNs', () => {
  assert.equal(profileLink('parsa-emami'), 'https://www.linkedin.com/in/parsa-emami/');
  assert.match(peopleSearchLink('software engineer'), /keywords=software\+engineer/);
  assert.equal(validatePostUrn('urn:li:ugcPost:123456789'), 'urn:li:ugcPost:123456789');
  assert.throws(() => profileLink('../oauth'));
  assert.throws(() => validatePostUrn('http://example.com'));
  assert.throws(() => peopleSearchLink('a'));
});

test('constant time equality', () => {
  assert.equal(constantTimeEqual('secret', 'secret'), true);
  assert.equal(constantTimeEqual('secret', 'notsecret'), false);
});

test('encrypted token store and one-time state creation', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'linkedin-mcp-test-'));
  const old = { ...process.env };
  try {
    process.env.MCP_STORE_FILE = join(dir, 'encrypted.enc');
    process.env.MCP_ENCRYPTION_KEY_HEX = randomBytes(32).toString('hex');
    process.env.LINKEDIN_CLIENT_ID = 'test-id';
    process.env.LINKEDIN_CLIENT_SECRET = 'test-secret';
    process.env.LINKEDIN_REDIRECT_URI = 'https://mcp.example.com/oauth/callback';
    await writeState({ version: 1, auth: null, pending: null });
    assert.deepEqual(await readState(), { version: 1, auth: null, pending: null });
    const url = new URL(await startAuthorization());
    assert.equal(url.origin, 'https://www.linkedin.com');
    assert.equal(url.searchParams.get('redirect_uri'), process.env.LINKEDIN_REDIRECT_URI);
    assert.equal(url.searchParams.get('scope'), 'openid profile w_member_social');
    assert.equal(url.searchParams.get('state')?.length, 64);
    const stored = await readState();
    assert.equal(stored.pending.state, url.searchParams.get('state'));
    assert.equal(stored.auth, null);
  } finally {
    process.env = old;
    await rm(dir, { recursive: true, force: true });
  }
});
