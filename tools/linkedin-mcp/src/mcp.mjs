import { McpServer } from '@modelcontextprotocol/server';
import * as z from 'zod/v4';
import { disconnect, peopleSearchLink, profileLink, startAuthorization, status, validatePostUrn } from './core.mjs';
import { getMe, postAnalytics, postComment, publishText } from './linkedin.mjs';

function answer(value) {
  return { content: [{ type: 'text', text: JSON.stringify(value, null, 2) }] };
}

function protect(action) {
  return async (args) => {
    try {
      return answer(await action(args || {}));
    } catch (error) {
      return { isError: true, content: [{ type: 'text', text: error instanceof Error ? error.message : 'Unknown error' }] };
    }
  };
}

export function makeMcp() {
  const server = new McpServer({ name: 'parsa-linkedin-mcp', version: '0.1.0' });

  server.registerTool('linkedin_capabilities', {
    description: 'Check OAuth connection, expiration, approved scope assumptions and tool limitations; never exposes credentials.',
    inputSchema: z.object({})
  }, protect(status));

  server.registerTool('linkedin_authorize_url', {
    description: 'Create a one-time LinkedIn OAuth login URL. Open it yourself; the registered HTTPS callback completes authentication.',
    inputSchema: z.object({})
  }, protect(async () => ({
    url: await startAuthorization(),
    instruction: 'Open URL in your browser. Never paste client secret or access token into chat.'
  })));

  server.registerTool('linkedin_me', {
    description: 'Get your own LinkedIn OpenID profile fields after connecting.',
    inputSchema: z.object({})
  }, protect(getMe));

  server.registerTool('linkedin_find_people', {
    description: 'Build an official LinkedIn People search link. This does not scrape or enumerate profiles.',
    inputSchema: z.object({ query: z.string().min(2).max(200) })
  }, protect(({ query }) => ({ url: peopleSearchLink(query), automatedSearch: false })));

  server.registerTool('linkedin_profile_for_invitation', {
    description: 'Return a LinkedIn profile URL where you can manually request a connection. Automated invitations require partner access.',
    inputSchema: z.object({ vanity: z.string().min(2).max(100) })
  }, protect(({ vanity }) => ({
    url: profileLink(vanity),
    automaticInvitation: false,
    reason: 'LinkedIn Invitations API is restricted to approved partners.'
  })));

  server.registerTool('linkedin_publish_text', {
    description: 'Publish a public text post on your own LinkedIn account. Mutating action; require explicit confirm PUBLISH and MCP_ALLOW_WRITES=true.',
    inputSchema: z.object({ text: z.string().trim().min(1).max(3000), confirm: z.literal('PUBLISH') })
  }, protect(async ({ text }) => publishText(text)));

  server.registerTool('linkedin_comment_on_post', {
    description: 'Comment as the authenticated member on a specified LinkedIn post where approved API scopes allow. Mutating action.',
    inputSchema: z.object({
      postUrn: z.string().refine((v) => { try { validatePostUrn(v); return true; } catch { return false; } }),
      text: z.string().trim().min(1).max(1200),
      confirm: z.literal('COMMENT')
    })
  }, protect(async ({ postUrn, text }) => postComment(postUrn, text)));

  server.registerTool('linkedin_post_analytics', {
    description: 'Get the authorized member post statistics. Requires additional r_member_postAnalytics permission.',
    inputSchema: z.object({
      postUrn: z.string(),
      metric: z.enum(['IMPRESSION', 'MEMBERS_REACHED', 'RESHARE', 'REACTION', 'COMMENT', 'POST_SAVE', 'POST_SEND', 'LINK_CLICKS', 'PREMIUM_CTA_CLICKS', 'FOLLOWER_GAINED_FROM_CONTENT', 'PROFILE_VIEW_FROM_CONTENT']),
      aggregation: z.enum(['TOTAL', 'DAILY']).default('TOTAL')
    })
  }, protect(({ postUrn, metric, aggregation }) => postAnalytics(postUrn, metric, aggregation)));

  server.registerTool('linkedin_disconnect', {
    description: 'Delete the locally encrypted LinkedIn token and any pending OAuth state. Destructive action.',
    inputSchema: z.object({ confirm: z.literal('DISCONNECT') })
  }, protect(disconnect));

  return server;
}
