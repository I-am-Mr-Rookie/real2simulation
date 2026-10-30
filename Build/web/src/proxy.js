import { clerkMiddleware } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';
import { clerkConfiguration } from './auth/config.mjs';

const sessionContext = clerkMiddleware();

export default async function proxy(request, event) {
  if (!clerkConfiguration(process.env).available) return NextResponse.next();
  try { return await sessionContext(request, event); }
  catch { return new NextResponse(null, { status: 404, headers: { 'Cache-Control': 'private, no-store' } }); }
}

// Session context only; every leaf still checks ownership. Guests/library/health bypass this entirely.
export const config = { matcher: ['/workspace/:path*', '/api/workspace/:path*'] };
