import 'server-only';
import { clerkConfiguration } from './config.mjs';

export function getClerkConfiguration() {
  return clerkConfiguration(process.env);
}
