# SAM 3D Objects access — owner-reported receipt (Oct29)

**STATUS (Oct29 ~19:11 Dhaka): OWNER-SCREENSHOT CONFIRMED — ACCESS GRANTED.**
Owner screenshot of https://huggingface.co/facebook/sam-3d-objects (in-app browser) shows
"Paper for facebook/sam-3d-objects" (SAM 3D: 3Dfy Anything in Images, 2511.16624) and the
badge "Gated model — You have been granted access to this model".
Saved: SAM3D-ACCESS-granted-20261029.png, SHA256
BA75A887131C3644EAA608E64B658340DAE631D27C6B64B41FDA3AADAABF3737.
This supersedes the "not yet verified"/"read-only look" notes below: no further access
check is needed. Not yet verified: checkpoint bytes/config, revision pin, runtime or output;
the first worker pins the revision and records the checkpoint SHA256 at download.
GPU: Modal L40S 48 GB / A100 / H100 under standing GPU authorization (A10 too small).

Koushik, direct chat reply Oct29 ~19:10 Dhaka: on the night of Oct28 he accepted the
SAM License on Hugging Face and applied for SAM 3D access; Meta approved it within
one to two hours. He says the approval is visible in the in-app ChatGPT browser.
Status: OWNER-REPORTED. Not yet agent-verified (no HF page/checkpoint read in this
session). Controller missed this earlier because no receipt existed in project files.
Before first use: verify gated access on HF in the in-app browser (read-only), pin the
revision and record the checkpoint SHA256. Agents accept no terms themselves.
Separate safeguard still applies: S06c gate needs a >=32 GB GPU (A10 23 GB too small).
Modal already offers this (L40S 48 GB, A100 40/80 GB, H100 80 GB): use one of those
under the standing GPU authorization; no new account/provider needed.
Note Oct29: owner screenshot shows "granted access" on facebook/sam3.1 (SAM 3.1
tracking, already verified in S07b), not the SAM 3D Objects repo. A one-time read-only
look at the SAM 3D Objects page confirms that repo; the checkpoint SHA256 is recorded
automatically at download for reproducibility (no owner action).
