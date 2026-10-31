import './public.css';

export default function PublicLayout({ children }) {
  return <div data-audience="public">{children}</div>;
}
