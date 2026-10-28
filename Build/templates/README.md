# Experiment template tools

## Free fall (S08d)

Python: `from Build.templates.free_fall import make_free_fall, analytic_free_fall`.
Run from repository root; use `contracts/experiment/requirements.txt` dependencies.
No network, numeric defaults, model calls, fixture imports or integrations.

`make_free_fall` takes keyword-only `experiment_id, scene, scene_root, origin,
gravity, mass, radius, drop_height, initial_vertical_velocity, duration, time_step,
clearance, seed=0`. Physical quantities use the existing sourced-quantity
contract; origin uses the sourced-position contract. All must be explicitly
supplied, including gravity matching the authoritative scene. Scene bounds,
scale status, surface IDs and collider IDs are copied, never guessed. The return
is a fresh experiment v1.0.0 spec after `validate_setup`; bad scale, source units,
bundle assets, scene geometry or timestep fail closed. No support attachment.
Factory dictionaries are deep-copied, with no caller mutation.

`analytic_free_fall(spec, scene, scene_root, times=...)` (times keyword-only,
default empty tuple) revalidates the full setup and returns deterministic JSON
data: `method`, `experiment_id`, `input_sources`, `impact_time`,
`impact_vertical_velocity`, `impact_position`, and `samples`. Each sample has
`time`, `position`, `vertical_velocity`. Every numeric output uses value/unit/
source/uncertainty; label `simulated`, evidence `analytic-free-fall-v1:experiment/ID`.
This is a code-computed **analytic reference**, not an integrated trajectory or
a measured result. Input source labels are preserved separately (including
synthetic inputs); source strings are not authenticated scientific evidence.
Uncertainty is null: neither propagated error bars nor exact physical certainty
are implied. Consumers must not strip method/input provenance for user claims.

For positive height h, positive gravity magnitude g, signed upward v and initial
centre (x0,y0,z0): y(t)=y0+v*t-g*t²/2; vy(t)=v-g*t. Stop plane is y0-h,
not floor contact (body radius affects validation, not the point-mass oracle).
Impact speed magnitude w=sqrt(v²+2*g*h). Positive impact time is (v+w)/g
for v>=0, or 2*h/(w-v) for v<0 to avoid cancellation. Impact vy=-w.
Uniform world -Y gravity, vacuum, no drag/contact/rebound; upward launches
are supported including the apex. S08c's conservative envelope applies.

Sample times are a list/tuple of at most 100001 finite non-bool numbers in
[0,min(duration,impact_time)] seconds. Order/duplicates are preserved. No
automatic timestep allocation, clipping, extrapolation or post-impact samples.
Impact metrics always describe the full ideal flight, even when configured
duration is shorter; this does not assert the integrator reached impact.
Floating-point equality at impact uses the exact stop-plane endpoint.

Checks: `python -m unittest discover -s tests/spec -p 'test_*.py' -q`.
Synthetic tests establish formula/API behavior only. Gate P requires the later
independent S10 engine comparison; it is NOT RUN here.

## Horizontal projectile (S08e)

Python: `from Build.templates.projectile import make_projectile, analytic_projectile`.
`make_projectile` uses the same keyword-only sourced inputs as free fall, replacing
`drop_height, initial_vertical_velocity` with `launch_height, horizontal_speed`.
All physical inputs remain explicit. Scene snapshots include every authoritative
surface/collider; factory and oracle both call `validate_setup`. No geometry,
scale, asset-integrity or timestep checks are bypassed; inputs are deep-copied.

Conventions: horizontal +X launch with zero initial Y/Z velocity, uniform -Y
gravity, vacuum, no drag, spin, bounce or contact. For start centre (x0,y0,z0),
positive centre travel h, gravity g>0, speed u>=0:
`x=x0+u*t`, `y=y0-g*t²/2`, `z=z0`, `velocity=[u,-g*t,0]`.
Stop plane is y0-h, not a floor/contact surface. Let w=sqrt(2*g*h):
impact time T=w/g, horizontal range u*T, impact velocity [u,-w,0]. Zero
horizontal speed is supported. Arbitrary launch angles are not this variant.

`analytic_projectile(spec, scene, scene_root, times=...)` returns `method`,
`experiment_id`, `input_sources`, `impact_time`, `horizontal_range`,
`impact_position`, `impact_velocity`, `samples` (time/position/velocity).
Every numerical field uses the sourced value/unit/uncertainty envelope above;
method/evidence prefix is `analytic-projectile-v1`. Values are computed analytic
references labelled `simulated`, never measurements or an integrator result.
Input source labels are copied separately; uncertainty is null, not fabricated.
Sample limits/order/duplicates and short-duration semantics match free fall;
the exact impact endpoint is anchored to the stop plane. No automatic samples.
The same offline test command above covers both templates. Gate P remains NOT RUN.

## Ramp (S08f)

`make_ramp` takes explicit keyword arguments: experiment_id, scene, scene_root,
origin, gravity, mass, radius, length, incline_angle, friction_coefficient,
initial_speed, duration, time_step, clearance, optional seed=0. Quantity/source
envelopes and deep-copy/authoritative validation conventions match the other
factories. `analytic_ramp(spec, scene, scene_root, times=())` revalidates the bundle.

Ideal point-mass sliding, no rolling or air drag. Straight XY centre path has
unit downhill direction d=(cos(theta),-sin(theta),0), theta in radians. With
kinetic friction mu, a=g*(sin(theta)-mu*cos(theta)), distance s=u*t+a*t²/2,
speed v=u+a*t, position origin+s*d. End speed w=sqrt(u²+2*a*L),
end time T=L/((u+w)/2), avoiding subtraction cancellation. Mass cancels.
The oracle/factory require finite **a>0**; nonaccelerating, stalling, static
friction and uphill regimes are deliberately unsupported, even if a draft spec
passes baseline validation. Starting at rest means ideal incipient sliding,
not a prediction that static friction is overcome. No physical support is
attached: existing validator still rejects contact-mounted setups.

Returns method `analytic-ramp-v1`, experiment_id, input_sources, acceleration,
end_time, end_speed, end_position, end_velocity and samples. Samples contain
time, downhill distance, world position and world velocity. Numeric envelopes
use SI units, simulated source labels and null (unpropagated) uncertainty.
Full ramp-end metrics are independent of simulation duration; requested times
must lie in [0,min(duration,T)], same type/count/order rules as other templates.
No automatic sampling, post-end motion, integration, measured evidence or Gate P
claim. Radius affects validation, not the ideal centre-path solution.

## Pendulum (S08g)

`make_pendulum` takes explicit keyword arguments: experiment_id, scene,
scene_root, origin, gravity, mass, radius, length, release_angle,
initial_angular_velocity, duration, time_step, clearance, optional seed=0.
Both factory and `analytic_pendulum(spec, scene, scene_root, times=())` call
authoritative `validate_setup`, preserving asset, geometry and timestep checks.
The full-rotation safety envelope remains conservative even for small swings.
Sourced input envelopes are deep-copied; no inferred physical inputs.

Origin is the fixed pivot, length the pivot-to-bob-centre distance; motion
is in XY, positive angle towards +X from downward -Y. Ideal massless rigid
link/point bob, constant gravity, no drag, damping, support contact or rotation.
This reference explicitly solves the **linearized small-angle** equation,
not the finite-angle nonlinear pendulum. With w=sqrt(g/L), theta0=release_angle,
u=initial_angular_velocity:
`theta=theta0*cos(w*t)+(u/w)*sin(w*t)`,
`omega=-theta0*w*sin(w*t)+u*cos(w*t)`, `T=2*pi/w`.
Both APIs require amplitude `hypot(theta0,u/w)<=0.1 rad`; larger-amplitude
draft specs may validate against the general schema but have no oracle here.
Zero-amplitude equilibrium is allowed; T then denotes natural period, not an
observed oscillation. No claim of exact finite-amplitude period or measured g.

Circular geometry reconstructed from approximate angle:
`position=pivot+[L*sin(theta),-L*cos(theta),0]`,
`velocity=[L*cos(theta)*omega,L*sin(theta)*omega,0]`.
The approximate angular motion conserves linearized energy, not the full
nonlinear energy. Mass/radius affect validation, not this reference solution.

Returns method `analytic-pendulum-small-angle-v1`, model `linearized-small-angle`,
experiment_id, input_sources, angular_frequency (rad/s), period (s), amplitude
(rad), samples (time, angle, angular_velocity, position, velocity). All numeric
envelopes are labelled simulated with null unpropagated uncertainty. Input
provenance is copied separately. Samples must be finite seconds in [0,duration],
list/tuple of at most100001, preserving order/duplicates; none generated by default.
Period is independent of requested duration. Existing offline spec test command
covers all four references; no integrator/nonlinear accuracy or Gate P claim.
