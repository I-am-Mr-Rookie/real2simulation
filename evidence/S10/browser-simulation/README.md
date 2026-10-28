# R11 browser simulation child

## Parent integration contract (not wired here)

```jsx
import BrowserSimulation from './BrowserSimulation.jsx';
// NORMAL only, supplied through the parent's trusted, validated server transport:
<BrowserSimulation payload={{ mode: 'normal', validatedSetup: artifact }} />
```

`runBrowserSimulation({mode: 'normal', validatedSetup: artifact})` returns the
unchanged frozen output of the existing four RK4 engines. `artifact` is the real
`Build/simulator/export_validated_setup.py` export, after authoritative Python
`validate_setup`. Browser envelope checks are **not producer authentication** or
a replacement for full S08 validation. Parent must never send Mystery setup,
hidden g or seed to this component/client; rejection cannot undo a data leak in
transport. Missing mode is not NORMAL. Mystery is rejected before artifact access.

The maximum requested horizon is 1999 steps / 2000 samples including time zero;
larger inputs are rejected before engine execution, not truncated or downsampled.
The static chart uses every actual sample's time and world Y position. The short
table alone is sampled and displayed at six significant digits. No animation,
frame callbacks, timers, network calls, contact response, or free dragging.

## Reproduce

```powershell
python evidence/S10/browser-simulation/generate_fixtures.py
node --test tests/lab/browser-simulator.test.mjs
node --test tests/simulator/trajectories.test.mjs tests/simulator/extended-templates.test.mjs tests/lab/browser-simulator.test.mjs
node --check Build/web/src/lab/browser-simulator.mjs
node evidence/S10/browser-simulation/check-component.mjs '<existing Build/web/node_modules>'
```

Fixtures are generated using actual existing `regression_case -> export`, and
server traces with actual `Build/lab/simulate.mjs`. All four are checked against
fresh current server output and direct current engines; repeat traces match.
Direct engine comparison preserves signed zero; JSON transport comparison is
exact serialized equality (JSON normalizes `-0` to `0`). The initial test failure
was that JSON signed-zero distinction; the product engines were not changed.

`check-component.mjs` reuses existing Next Babel for fresh JSX parsing and an
explicit element/hook harness. It checks user-triggered computation, actual
polyline points, stale DTO reset and generic Mystery errors. It is **not** a real
DOM, browser, viewport, accessibility, full Next build, or end-to-end check.
The parent owns integration, trusted NORMAL DTO production, required reviews,
and signed-in IAB verification at 375px. No product/physical gate is claimed.
