// S15ai: one responsive <picture> per theme family (WebP 1x/2x, PNG fallback); CSS shows the family matching html[data-theme]. Never CSS-inverted.
// S15aq: set="app" reuses the existing /images/app/<id>-<fam>@Nx art (B1-B6).
export default function MarketingArt({ id, alt, width, height, eager = false, set = 'marketing' }) {
  const stem = (fam) => set === 'app' ? '/images/app/' + id + '-' + fam : '/images/marketing/' + id + '-' + fam + '-line';
  const one = (fam) => <picture key={fam} className={'art art-' + fam}>
    <source type="image/webp" srcSet={stem(fam) + '@1x.webp 1x, ' + stem(fam) + '@2x.webp 2x'} />
    <img src={stem(fam) + '@1x.png'} srcSet={stem(fam) + '@2x.png 2x'} width={width} height={height} alt={alt} loading={eager ? 'eager' : 'lazy'} decoding="async" />
  </picture>;
  return <>{one('light')}{one('dark')}</>;
}
