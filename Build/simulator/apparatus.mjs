// S10a consumes the exact artifact emitted only after Python validate_setup.
const fail = (m) => { throw new TypeError(`INVALID_VALIDATED_SETUP: ${m}`); };
const finite = (n) => typeof n === 'number' && Number.isFinite(n);
const vec3 = (v) => Array.isArray(v) && v.length === 3 && Object.keys(v).length === 3 && v.every(finite);
const validated = new WeakSet();
const freeze = (value) => {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.values(value).forEach(freeze); Object.freeze(value);
  }
  return value;
};

export function consumeValidatedSetupArtifact(raw) {
  // TRUSTED TRANSPORT precondition: producer/validation labels describe the controlled adapter path;
  // they are not authentication and this function is not a security boundary for public JSON.
  if (!raw || raw.artifact_version !== 's10-validated-setup-v1' || raw.validation !== 'validate_setup' || raw.producer !== 'contracts/experiment/validate_experiment.py') fail('invalid trusted-transport envelope');
  const { spec, scene } = raw;
  const c = spec?.scene?.constraints, placement = spec?.placement, origin = placement?.origin?.value;
  if (!spec || !scene || scene.schema_version !== '1.0.0' || typeof scene.id !== 'string' || spec.scene.scene_id !== scene.id || spec.scene.schema_version !== scene.schema_version || !c || !placement || !vec3(origin) || placement.surface_id !== null) fail('S08 scene/placement mismatch');
  if (JSON.stringify(c.bounds_m) !== JSON.stringify(scene.bounds_m) || !Array.isArray(scene.surfaces) || !Array.isArray(scene.colliders) || !vec3(scene.bounds_m?.min) || !vec3(scene.bounds_m?.max)) fail('scene geometry or bounds mismatch');
  const copy = freeze(structuredClone(raw)); validated.add(copy); return copy;
}

export function placeApparatus(artifact) {
  if (!validated.has(artifact)) fail('artifact must be returned by consumeValidatedSetupArtifact');
  const { spec, scene } = artifact, origin = [...spec.placement.origin.value], radius = spec.body.radius.value, bounds = scene.bounds_m;
  if (!finite(radius) || radius <= 0 || origin.some((x, i) => x - radius < bounds.min[i] || x + radius > bounds.max[i])) fail('body outside validated scene bounds');
  return Object.freeze({ id: `${scene.id}-apparatus`, shape: 'sphere', synthetic: Boolean(scene.synthetic), pose: Object.freeze({ position_m: Object.freeze(origin) }), radius_m: radius, colliders: Object.freeze(scene.colliders.map((c) => structuredClone(c))), scene_id: scene.id, validation: artifact.validation });
}
