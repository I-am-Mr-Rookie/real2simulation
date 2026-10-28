# Direct HF-to-Modal readiness — no execution

## Fresh normal in-app inspection

- Inventory identified ChatGPT in-app browser, ID2. Initial HF tab creation failed:
  `Timed out waiting for the Browser webview to attach for this browser-use page`.
  No fallback to Chrome/native/CLI credentials. A normal Modal tab subsequently
  attached, then one HF inspection succeeded. This was browser bootstrap recovery,
  not repeated account/access hunting. AX checkpoint click failed with
  `Could not check the click target's shadow root`; documented Playwright locator
  opened the same metadata link successfully. No download clicked.
- Modal Apps dashboard authenticated in selected workspace/environment `main`:
  displayed credits **$129.99**. Settled Apps view showed **Live Apps0**, Stopped6.
  Initial partial rendering showed Stopped0; do not use it as final evidence.
- Modal Secrets list in that same environment showed **Create your first secret**,
  no existing listed secrets. No secret detail/value opened or new secret created.
  This establishes no reusable named HF secret in that inspected environment,
  NOT absence of credentials in all workspaces, local stores or other routes.
- No Containers/billing settings inspection; no paid-overage cap/remaining project
  authority verification. Dashboard credit is aggregate credit, not permission to
  exceed project$30, not exact billing, not current GPU capacity. Existing$2.85
  reservations retained; no new reservation or reserve release.

## Supported route and present gap

[HF download guide](https://huggingface.co/docs/huggingface_hub/guides/download)
supports file-specific `hf_hub_download` with a pinned revision. Execute it only
**inside a later authorized Modal runtime**, not on the laptop, for
`facebook/sam3.1@daa63191845a41281374e725f4c9e51c7a824460`, exact checkpoint and
config. Restrict filenames; do not snapshot unrelated assets or use floating main.

[Modal model-weights guide](https://modal.com/docs/guide/model-weights) documents
remote HF retrieval and revision pinning. Its example creates a Volume; that
creation is NOT authorized by this recovery and should not be copied blindly.
For a single bounded later probe, ephemeral runtime storage is the smallest
candidate, provided3,502,755,717-byte model plus libraries/cache/working memory
fit a checked bound. Do not bake gated weights/credentials into an image layer or
return them to the client. A persistent Volume needs separate scoped resource
authority, not an invented necessity for the one-shot probe.

[Modal Secrets](https://modal.com/docs/guide/secrets) documents injection from an
existing named secret. None was available in the inspected `main` list. Browser
HF cookies do not automatically authenticate a remote Modal process; Modal client
authentication is also not an HF token. Thus **no existing supported authenticated
HF-to-Modal path was established under this run's no-token-transfer/no-secret-
creation boundary**. Never extract browser cookies, read/copy local tokens, use
Secret.from_dict/from_dotenv or call a private API as a workaround. Public web
reader's401 on model blob is anonymous-tool behavior, not rejection of owner access.

## Smallest next steps and exact safeguards

1. Controller records current metadata gain; keep Q11 ANSWERED. No renewed terms,
   access, GPU-consent or credit-redemption question. Route only the genuinely new
   credential-delivery boundary through controller Reviews: supported HF authentication
   in the intended Modal environment (existing approved path if independently known,
   or a separately scoped secure setup). Do not demand manual babysitting merely
   because the browser initially failed; both requested signed-in services worked.
   No credential values in
   chat, report, source, command line or logs. This run makes no such changes.
2. Before any remote retrieval/paid admission: fresh headroom/no-paid-overage,
   project-budget/reservation reconciliation, no duplicate active work, licensed
   inputs and precise permitted transfer scope. Local-only ST03 approval is not
   new remote-media permission. No footage is needed for metadata/import checks.
3. Prepare isolated SAM Python3.12/NumPy<2 dependency specification, pinned SAM
   software revision above, and kernel/GPU compatibility checks. Reuse S05b's
   single-shot isolation/stop pattern, not its Python3.11/NumPy2 lock or assumed
   L4 adequacy. Read fresh S05b deadline-guard diagnostic before reuse; current
   recovery runs concurrently and its unverified changes are not assumed present.
4. First later run should be a bounded no-media admission/import/auth/identity
   probe, not271-frame tracking. Resolve model identity/authorized remote path
   before GPU allocation where possible. Download only inside Modal when that
   transfer/runtime is explicitly in its run contract; verify exact size/SHA256
   against pointer, preserve config revision/digest, log imports/driver/VRAM,
   stop on401/403, identity mismatch, unsupported runtime or missing safeguard.
5. Proposed conservative total wallclock **<=10min from local admission**, covering
   queue, startup, install, transfer and verification, with queue admission
   cutoff **<=90s** and no automatic retry. These are future guard requirements,
   NOT implemented/verified guarantees or a cost reservation. Separate Modal
   function timeouts do not bound pending RPC wait; external watchdog must cancel
   pending RPC and stop identified app, including on failure/deadline. Set exact
   absolute UTC stop, price-based worst-case reservation within remaining$30,
   one container/no retries, storage/egress caps and cleanup before launching.
   If stop/headroom/auth cannot be demonstrated, do not admit paid work.
6. Independently verify resource stop (app stopped/tasks0/containers[]) and retain
   actual elapsed/billed evidence; never treat successful local cancellation as
   proof all remote resources stopped. No automatic GPU retry on queue failure.

No runner implemented, model downloaded, job executed, media moved, resource or
secret created, terms accepted, billing changed or paid spend initiated here.
