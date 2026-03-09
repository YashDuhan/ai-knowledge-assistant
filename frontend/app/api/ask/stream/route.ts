export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function backendBaseUrl() {
  return process.env.BACKEND_URL || 'http://localhost:8000';
}

export async function POST(req: Request) {
  const upstream = await fetch(`${backendBaseUrl()}/ask/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: await req.text(),
    cache: 'no-store',
  });

  // Pass through SSE without buffering/compression hints.
  const headers = new Headers(upstream.headers);
  headers.set('Cache-Control', 'no-cache');
  headers.set('Connection', 'keep-alive');
  headers.set('X-Accel-Buffering', 'no');

  return new Response(upstream.body, {
    status: upstream.status,
    headers,
  });
}

