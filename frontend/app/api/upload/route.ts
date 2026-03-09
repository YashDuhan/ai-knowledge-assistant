export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function backendBaseUrl() {
  return process.env.BACKEND_URL || 'http://localhost:8000';
}

export async function POST(req: Request) {
  const fd = await req.formData();
  const forward = new FormData();

  for (const [key, value] of fd.entries()) {
    forward.append(key, value);
  }

  const upstream = await fetch(`${backendBaseUrl()}/upload`, {
    method: 'POST',
    body: forward,
    cache: 'no-store',
  });

  const headers = new Headers(upstream.headers);
  return new Response(upstream.body, { status: upstream.status, headers });
}

