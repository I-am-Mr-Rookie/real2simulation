// Synthetic noncredential-only SDK probe, not a verified session or application HTTP test.
const { createRequire } = require('node:module');
const path = require('node:path');
process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = 'pk_test_' + Buffer.from('example.clerk.accounts.dev$').toString('base64');
process.env.CLERK_SECRET_KEY = 'sk_test_S04C_SYNTHETIC_SERVER_SENTINEL';
process.env.CLERK_TELEMETRY_DISABLED = '1';
const requireWeb = createRequire(path.resolve('Build/web/package.json'));
const { clerkMiddleware } = requireWeb('@clerk/nextjs/server');
const { NextRequest } = requireWeb('next/server');
const timer = setTimeout(() => { console.error('SDK probe timed out'); process.exit(1); }, 3000);
clerkMiddleware()(new NextRequest('http://localhost:3000/workspace'), { waitUntil() {} }).then((response) => {
  clearTimeout(timer);
  console.log(JSON.stringify({ status: response.status,
    next: response.headers.get('x-middleware-next'),
    rewrite: response.headers.has('x-middleware-rewrite'),
    redirect: response.headers.has('location') }));
}, (error) => { clearTimeout(timer); console.error(error.name); process.exitCode = 1; });
