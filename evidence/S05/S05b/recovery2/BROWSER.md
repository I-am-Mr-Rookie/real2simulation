# Supported Chrome recovery2 receipt

Session 2026-10-28, approximately 07:48–07:50 UTC. Read-only operation; no billing changes.

1. `cua.getState()` succeeded (24.3265s). Chrome extension browser `3`, profile The Main Character, was exposed. Inventory contained Modal usage tab `660515237`, title `Usage & billing - koushiksadhakjeet | Modal`, URL `https://modal.com/settings/koushiksadhakjeet/usage`. This proves inventory availability, NOT current credit/headroom contents.
2. `cua.getTab('660515237', {browser:'3'})` returned: `Tab 660515237 is already part of browser session 01a1816d-b0a5-76d2-8a22-620ade458881` (11.2339s). No tab state or billing contents returned; no ownership override attempted.
3. One normal `cua.createBrowserTab('3', 'https://modal.com/settings/koushiksadhakjeet/usage', {sessionName:'🔎 S05b runtime'})` returned `js execution timed out; kernel reset, rerun your request` (30.2813s). No known resulting tab ID or AX state.
4. One `cua.listTabs({browser:'3'})` to inspect the outcome, NOT another creation, returned the same exact timeout/kernel-reset message (30.3421s).

Stopped UI operations after recurring provider timeouts. No further retries, native app, shell, CDP, extension/config/credential/policy changes or alternative browser route. These were provider timeouts, NOT a newly reported URL safety denial. Underlying provider cause is unproved; do not label Chrome absent or claim the controller's prior restoration false.

The controller's recent authenticated $130 credits/$0 rounded spend/$155 gross limit receipt remains historical independent evidence. This session did not retrieve billing AX, actual applicable credits/remaining usage or no-paid-overage coverage. No account-wide net-spend cap is established; no cap change requested.

Consequence: no remote CPU preparation, GPU job or new reservation. Standing consent remains valid; the failed prerequisite is current verifiable execution bookkeeping. A fresh job must not use this timeout receipt as credit proof.
