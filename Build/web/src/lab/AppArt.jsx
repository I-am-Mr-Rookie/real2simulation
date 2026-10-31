// S15ao: B-series app art, one <picture> per theme family; global .art-light/.art-dark pick by html[data-tone]. Decorative.
export default function AppArt({ id, width, height }) {
  const base = '/images/app/' + id;
  return ['light', 'dark'].map((fam) => <picture key={fam} className={'art art-' + fam}>
    <source type="image/webp" srcSet={base + '-' + fam + '@1x.webp 1x, ' + base + '-' + fam + '@2x.webp 2x'} />
    <img src={base + '-' + fam + '@1x.png'} srcSet={base + '-' + fam + '@2x.png 2x'} width={width} height={height} alt="" loading="lazy" decoding="async" />
  </picture>);
}
