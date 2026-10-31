// S15ai: one responsive <picture> per theme family (WebP 1x/2x, PNG fallback); CSS shows the family matching html[data-theme]. Never CSS-inverted.
// S15aq: set="app" reuses the existing /images/app/<id>-<fam>@Nx art (B1-B6).
// S15au: repo link and official GitHub mark, shared by the home CTA and the header nav.
export const REPO_URL = 'https://github.com/I-am-Mr-Rookie/real2simulation';
export const GITHUB_MARK = <svg className="r2s-icon" width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true" focusable="false"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z" /></svg>;
export default function MarketingArt({ id, alt, width, height, eager = false, set = 'marketing' }) {
  const stem = (fam) => set === 'app' ? '/images/app/' + id + '-' + fam : '/images/marketing/' + id + '-' + fam + '-line';
  const one = (fam) => <picture key={fam} className={'art art-' + fam}>
    <source type="image/webp" srcSet={stem(fam) + '@1x.webp 1x, ' + stem(fam) + '@2x.webp 2x'} />
    <img src={stem(fam) + '@1x.png'} srcSet={stem(fam) + '@2x.png 2x'} width={width} height={height} alt={alt} loading={eager ? 'eager' : 'lazy'} decoding="async" />
  </picture>;
  return <>{one('light')}{one('dark')}</>;
}
