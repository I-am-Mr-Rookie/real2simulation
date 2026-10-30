import { artifactResponse } from '../../guest.mjs';
export const dynamic = 'force-dynamic';
export async function GET(_request, { params }) { return artifactResponse((await params).id); }
