import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

export default function middleware(req: NextRequest) {
  const url = req.nextUrl;
  
  // Get hostname of request (e.g. agency1.localhost:3000, vanguard-reserve.com)
  const hostname = req.headers.get('host') || 'vanguard-reserve.com';

  // Define allowed domains (including localhost for dev)
  const isLocalhost = hostname.includes('localhost');
  const mainDomain = isLocalhost ? 'localhost:3000' : 'vanguard-reserve.com';
  
  // Extract subdomain if it exists
  const subdomain = hostname.endsWith(`.${mainDomain}`) 
    ? hostname.replace(`.${mainDomain}`, '') 
    : null;

  // 1. If no subdomain, we are on the main platform (SuperAdmin or Marketing)
  if (!subdomain || hostname === mainDomain) {
    // If accessing root, let it render the main app layout
    return NextResponse.next();
  }

  // 2. If there is a subdomain, it's an agency tenant.
  // We rewrite the URL to /agency/[subdomain]/[...path]
  
  // For example: agency1.localhost:3000/clinic-alpha -> /agency/agency1/clinic-alpha
  
  const path = url.pathname;
  
  return NextResponse.rewrite(new URL(`/agency/${subdomain}${path}`, req.url));
}
