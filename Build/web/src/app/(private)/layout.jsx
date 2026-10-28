import { notFound } from 'next/navigation';

// Fail closed until a private repository is connected and integration-reviewed.
// The leaf independently uses requirePrivateScene; this layout is defense in depth.
// A route group is composition only, never an authorization boundary.
export const dynamic = 'force-dynamic';
export default function PrivateLayout() {
  notFound();
}
