import { guessProxy } from '../proxy.mjs';
export const dynamic = 'force-dynamic';
export const GET = async (request, { params }) => guessProxy(request, (await params).token, false);
