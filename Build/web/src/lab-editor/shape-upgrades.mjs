// Apply optional shapes and failure reasons without replacing edits or resurrecting deleted objects.
export function mergeShapeUpdates(scene, incoming) {
  const shapes = new Map(incoming.objects.filter((o) => o.shape?.type === 'box' || (o.shape?.type === 'mesh' && o.shape.collider === 'box')).map((o) => [o.id, o.shape]));
  let changed = false;
  const objects = scene.objects.map((o) => {
    const shape = shapes.get(o.id);
    if (!shape || (shape.type === 'box' && o.shape?.type !== 'box') || JSON.stringify(o.shape) === JSON.stringify(shape)) return o;
    changed = true;
    return { ...o, shape };
  });
  return changed ? { ...scene, objects } : scene;
}
