import { guessProxy } from '../../proxy.mjs';
export const dynamic = 'force-dynamic';
export const POST = async (request, { params }) => guessProxy(request, (await params).token, true);
