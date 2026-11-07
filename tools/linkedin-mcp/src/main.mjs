import { createServer } from 'node:http';
import { createMcpHandler } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { toNodeHandler } from '@modelcontextprotocol/node';
import { config, constantTimeEqual, finishAuthorization } from './core.mjs';
import { makeMcp } from './mcp.mjs';

const mode = process.argv[2] || 'stdio';

if (mode === 'stdio') {
  await serveStdio(makeMcp);
} else if (mode === 'http') {
  const cfg = config();
  const bearer = process.env.MCP_BEARER_TOKEN || '';
  if (bearer.length < 32) throw new Error('MCP_BEARER_TOKEN must be at least 32 characters.');
  if (!cfg.redirectUri) throw new Error('LINKEDIN_REDIRECT_URI is required.');
  const redirect = new URL(cfg.redirectUri);
  if (redirect.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(redirect.hostname)) {
    throw new Error('Public OAuth redirect must use HTTPS.');
  }
  const handler = createMcpHandler(makeMcp, { responseMode: 'json' });
  const nodeHandler = toNodeHandler(handler);
  const allowedOrigins = (process.env.MCP_ALLOWED_ORIGINS || '').split(',').map((v) => v.trim()).filter(Boolean);
  const server = createServer(async (req, res) => {
    res.setHeader('Cache-Control', 'no-store');
    const send = (code, body) => {
      res.statusCode = code;
      res.setHeader('Content-Type', 'text/plain; charset=utf-8');
      res.end(body);
    };
    try {
      if (req.headers.host !== redirect.host) return send(403, 'Unexpected host');
      if (req.headers.origin && !allowedOrigins.includes(req.headers.origin)) return send(403, 'Origin denied');
      if (req.url === '/health' && req.method === 'GET') return send(200, 'ok');
      const url = new URL(req.url || '/', cfg.redirectUri);
      if (url.pathname === redirect.pathname && req.method === 'GET') {
        if (url.searchParams.has('error')) return send(400, 'LinkedIn denied authorization');
        const code = url.searchParams.get('code');
        const state = url.searchParams.get('state');
        if (!code || !state) return send(400, 'Missing OAuth parameters');
        await finishAuthorization(code, state);
        return send(200, 'LinkedIn connected. Return to your MCP client.');
      }
      if (url.pathname !== '/mcp') return send(404, 'Not found');
      if (!['GET', 'POST', 'DELETE'].includes(req.method || '')) return send(405, 'Method not allowed');
      if (!constantTimeEqual(req.headers.authorization || '', 'Bearer ' + bearer)) return send(401, 'Unauthorized');
      const size = Number(req.headers['content-length'] || 0);
      if (!Number.isFinite(size) || size > 1024 * 1024) return send(413, 'Request too large');
      await nodeHandler(req, res);
    } catch (error) {
      console.error('Request failed:', error instanceof Error ? error.message : String(error));
      if (!res.headersSent) send(400, 'Request failed. Check server logs.');
      else res.end();
    }
  });
  const port = Number(process.env.PORT || 8787);
  server.listen(port, '127.0.0.1', () => console.error('MCP HTTP listening on 127.0.0.1:' + port + ' (HTTPS proxy required for public access)'));
  process.once('SIGTERM', async () => { server.close(); await handler.close(); });
  process.once('SIGINT', async () => { server.close(); await handler.close(); });
} else {
  throw new Error('Use stdio or http');
}
