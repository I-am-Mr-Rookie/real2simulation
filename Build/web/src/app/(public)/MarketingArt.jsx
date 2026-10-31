// S15ai: one responsive <picture> per theme family (WebP 1x/2x, PNG fallback); CSS shows the family matching html[data-theme]. Never CSS-inverted.
export default function MarketingArt({ id, alt, width, height, eager = false }) {
  const base = '/images/marketing/' + id;
  const one = (fam) => <picture key={fam} className={'art art-' + fam}>
    <source type="image/webp" srcSet={base + '-' + fam + '-line@1x.webp 1x, ' + base + '-' + fam + '-line@2x.webp 2x'} />
    <img src={base + '-' + fam + '-line@1x.png'} srcSet={base + '-' + fam + '-line@2x.png 2x'} width={width} height={height} alt={alt} loading={eager ? 'eager' : 'lazy'} decoding="async" />
  </picture>;
  return <>{one('light')}{one('dark')}</>;
}
