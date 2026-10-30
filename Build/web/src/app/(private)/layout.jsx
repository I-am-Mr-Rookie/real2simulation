import '../../workspace/workspace.css';

// Authorization belongs to each leaf's server data boundary, not a route group.
export const dynamic = 'force-dynamic';
export default function PrivateLayout({ children }) {
  return children;
}
