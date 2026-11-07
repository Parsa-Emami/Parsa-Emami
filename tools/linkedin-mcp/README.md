# LinkedIn MCP Server

A self-hosted, open-source LinkedIn MCP integration for a single personal account, using the official LinkedIn APIs. It does not use browser scraping, password automation, or paid social schedulers.

This folder is independent of the GitHub profile README. Install it independently or move it to its own repository.

## What works, and what needs permission

| MCP tool | Operation | Requirements |
|---|---|---|
| `linkedin_capabilities` | Show connection status, scopes and expiry | Local encrypted store |
| `linkedin_authorize_url` | Start consent-based LinkedIn OAuth | LinkedIn Developer application |
| `linkedin_me` | Read own basic profile | `openid profile` |
| `linkedin_find_people` | Return official People search URL | No profile scraping |
| `linkedin_profile_for_invitation` | Return profile URL for manual invitation | Automated invitations NOT implemented |
| `linkedin_publish_text` | Publish public text post | `w_member_social`; writes enabled; confirmation |
| `linkedin_comment_on_post` | Comment on a specified post | LinkedIn Community Management permission may be required; writes enabled; confirmation |
| `linkedin_post_analytics` | Read impressions, reactions, comments, and other metrics for own post | `r_member_postAnalytics`; developer product access |
| `linkedin_disconnect` | Wipe local OAuth token | Explicit confirmation |

The LinkedIn Invitations API is restricted to approved partners. General people-search enumeration and invitation automation are intentionally absent. API errors and permissions will be reported, not bypassed.

## Requirements

- Node.js 22 or newer.
- A LinkedIn Developer application at https://www.linkedin.com/developers/apps.
- Enable `Sign In with LinkedIn using OpenID Connect` and `Share on LinkedIn` products.
- Configure the app's exact HTTPS redirect URI `https://YOUR-HOST/oauth/callback` in the LinkedIn Developer Portal.
- For analytics, obtain `r_member_postAnalytics` if LinkedIn makes it available to your application.
- A server able to run Node.js, with HTTPS reverse proxy, for OAuth callback and remote ChatGPT-compatible MCP. GitHub hosting of this source code alone does NOT run a server.

## Setup

```bash
cd tools/linkedin-mcp
npm install
cp .env.example .env
openssl rand -hex 32
openssl rand -hex 32
```

Fill `.env` with the client ID, client secret, registered HTTPS callback, first randomly generated 64-character value as `MCP_ENCRYPTION_KEY_HEX`, and second value as `MCP_BEARER_TOKEN`. Keep `.env` outside Git. Keep the encryption key backed up securely: losing it makes the stored OAuth token unreadable.

Default scopes: `openid profile w_member_social`. Add `r_member_postAnalytics` to `LINKEDIN_SCOPES` only after the permission is granted to your LinkedIn developer app. `LINKEDIN_API_VERSION` should be updated as LinkedIn deprecates API versions.

```bash
chmod 600 .env
npm test
npm run serve
```

`npm run serve` binds to `127.0.0.1:8787`. Configure an HTTPS reverse proxy for `https://YOUR-HOST` forwarding both `/oauth/callback` and `/mcp` to this loopback port. The proxy must forward the original `Host` header. The server rejects unexpected hosts, unknown browser Origins, missing/invalid MCP bearer tokens, and oversized requests.

Connect your MCP client to `https://YOUR-HOST/mcp` with the header `Authorization: Bearer <MCP_BEARER_TOKEN>` (if supported by your MCP client). Run `linkedin_authorize_url` and open the returned link yourself. After LinkedIn redirects to the HTTPS callback, the token is saved encrypted at `~/.linkedin-mcp/auth.enc`, or at `MCP_STORE_FILE` if configured.

A ChatGPT connector can only use this server after you deploy it on a reachable HTTPS endpoint and configure a compatible authentication method. Raw bearer-header support varies by client; ChatGPT may require a separate OAuth-enabled MCP gateway. Code on GitHub is not itself a connected ChatGPT plugin.

## Local stdio MCP

After the HTTP callback is running and LinkedIn OAuth is complete, a local MCP host (Claude Desktop, Cursor, VS Code, etc.) can launch:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": ["--env-file=/ABSOLUTE/PATH/.env", "/ABSOLUTE/PATH/src/main.mjs", "stdio"]
    }
  }
}
```

The HTTP server and stdio process must use the same `MCP_STORE_FILE` and `MCP_ENCRYPTION_KEY_HEX`.

## Safety and limitations

- No passwords or access tokens are accepted through MCP tools or logged to stdout. OAuth credentials are stored AES-256-GCM encrypted with a local key not checked into Git.
- The server is designed for one trusted operator. For multi-user or public deployment, add a real MCP OAuth 2.1 authorization server, user isolation, audit logs, quotas, persistence and key management.
- Write calls are disabled by default. Set `MCP_ALLOW_WRITES=true` and provide the explicit `confirm` argument `PUBLISH` or `COMMENT` for each write. Confirm the text and recipient before execution.
- Do not expose raw HTTP port 8787 to the internet; terminate TLS at the reverse proxy.
- LinkedIn tokens expire. Re-authorize when needed. No automated credential harvesting, proxy bypass, mass invitations or scraping is provided.
- The self-serve `w_member_social` scope can publish; comment endpoints and analytics may be restricted by LinkedIn. The API returns 403 if your developer app lacks permission.
- The server has not been tested against a real LinkedIn account in this repository; integration needs your own LinkedIn OAuth app.

## API documentation

- OAuth: https://learn.microsoft.com/linkedin/shared/authentication/authorization-code-flow
- Share: https://learn.microsoft.com/linkedin/consumer/integrations/self-serve/share-on-linkedin
- Posts API: https://learn.microsoft.com/linkedin/marketing/community-management/shares/posts-api
- Member analytics: https://learn.microsoft.com/linkedin/marketing/community-management/members/post-statistics
- Invitations restriction: https://learn.microsoft.com/linkedin/shared/integrations/communications/invitations
- MCP TypeScript SDK v2: https://ts.sdk.modelcontextprotocol.io/v2/

## Development

```bash
npm test
npm start
```

`npm start` uses stdio. Tool output is structured JSON text. API operations are not retried automatically to avoid duplicate posts and comments.
