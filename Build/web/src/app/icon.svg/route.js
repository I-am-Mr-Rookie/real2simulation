// S15ao: a route handler (not the app/icon.svg file convention) keeps /icon.svg serving for smoke/old links
// without Next emitting a second <link rel="icon">; layout metadata's /brand icons are the only icon links.
const SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#155a92"/><path d="M13 46H51M19 46V51M45 46V51M16 20H29V30H16ZM29 23L35 20V30L29 27M23 30V46" fill="none" stroke="#fff" stroke-width="3"/><circle cx="45" cy="25" r="6" fill="none" stroke="#fff" stroke-width="3"/><path d="M45 31V46" stroke="#fff" stroke-width="3"/></svg>';
export const GET = () => new Response(SVG, { headers: { 'content-type': 'image/svg+xml', 'cache-control': 'public, max-age=86400' } });
