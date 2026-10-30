'use client';

import { useEffect } from 'react';

// Registers the S19b worker; its cache-policy never stores private/authenticated responses.
export default function SwRegister() {
  useEffect(() => {
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/pwa/sw.js', { scope: '/' }).catch(() => {});
  }, []);
  return null;
}
