import { freeFallTrajectory, projectileTrajectory } from './trajectories.mjs';
import { contactAwareTrajectory } from './contacts.mjs';

/** Build the accepted RK4 trajectory, then attach real Rapier contact samples. */
export async function runContactAwareTrajectory(input) {
  if (!input || typeof input !== 'object') throw new TypeError('INVALID_CONTACT_RUN: input is required');
  const trajectory = input.template === 'projectile' ? projectileTrajectory(input) : input.template === 'free_fall' ? freeFallTrajectory(input) : input.trajectory;
  return contactAwareTrajectory({ ...input, trajectory });
}
