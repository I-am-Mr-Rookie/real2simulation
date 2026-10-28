# Local synthetic lab transport — current authoritative handoff

POST `/api/lab` is loopback development only. No auth, deployment or production
boundary is relaxed. Public requests never include file paths, gravity, seeds,
private setup or raw tool responses supplied by the client.

Start request:

```json
{"action":"start","template":"free_fall","mystery":true}
```

Templates: `free_fall`, `projectile`, `ramp`, `pendulum`. Mystery mode is supported
only for the two ballistic templates. The successful response has `status:ok`,
`sessionId`, `template`, `mode`, `observations:[{time_s,position_m}]`,
`observationHash`, `source:simulated`, `units:{time:s,position:m}`, `limitations`.
Normal mode may additionally include an explicit source-labelled `gravity`
quantity. Mystery mode MUST omit gravity, seed, private setup, instrument true
errors, and any truth-bearing metadata prior to a successful matching fit.

Fit request:

```json
{"action":"fit","sessionId":"opaque-server-created-id"}
```

Successful response:

```text
{ status: "ok", sessionId: SAME_ID,
  fit: ACTUAL_PYTHON_S11_HANDLE_RESPONSE,
  reveal: {gravity: FITTED_VALUE, unit: "m/s^2", uncertainty: STANDARD_UNCERTAINTY,
           source: "simulated", fitStatus: "ok"} }
```

`fit` itself has `status:ok`, `gravity:{value,unit,uncertainty,source:{label,evidence}}`,
`uncertainty:{model,assumptions}` and other actual S11 fields. The frontend reads
**`body.fit.gravity`**, **`body.fit.uncertainty`** and **`body.sessionId`**.
There is NO `actualS11response` wrapper, fake simplified fit, client-authored
quantity, or guessed fallback shape. A fit error remains `status:error` with
`error:{code}`; never reveal a configured/true gravity as a failed-fit fallback.

Server uses actual tool output bound to exactly the displayed observations.
Opaque in-process handoff markers and shape validation are not authentication.
All evidence is simulated, conditional on fixed clock/scale and iid fitter
assumptions; instrument uncertainties are carried but not propagated.
