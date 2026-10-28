# Sources and Research Log

Checked October 16, 2026, in Chrome. Official sources outrank search snippets and this summary. No hidden APIs, account creation, consent, CAPTCHA bypass, or form submission were used.

| ID | Source | What was verified |
|---|---|---|
| S1 | [Meta official event](https://dev.meta.ai/events/global-hackathon) | Identity, tracks, themes, schedule, equal-weight selection, cap, final-rules-pending notice |
| S2 | [Cerebral Valley event](https://cerebralvalley.ai/e/meta-ai-developer-hackathon) | Same event; advertised model/partner support; application and waiver links |
| S3 | [Application entry](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/apply) | Navigation redirected to `/auth/login`; sign-in required to inspect actual questions |
| S4 | [Application overview and waiver](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/waiver) | Age threshold; exclusions; ownership, license, privacy, media, and liability provisions |
| S5 | [Muse Spark model](https://dev.meta.ai/models/muse-spark/) | Current page identifies Spark 1.3 and describes coding/tool-oriented capability |
| S6 | [Meta Model API overview](https://dev.meta.ai/docs/overview) | Capability and protocol documentation; linked structured-output support |
| S7 | [Structured output documentation](https://dev.meta.ai/docs/structured-output) | Schema-constrained output; endpoint-specific parameter differences; no recursive schemas |
| S8 | [AgriSense repository](https://github.com/I-am-Mr-Rookie/rookieCoders_AgriSense) | Historical October 16 research only; replaced by AutoShop as the application experience example on October 18 |
| S9 | [Rookie Coach repository](https://github.com/I-am-Mr-Rookie/rookie-coach) | Public visibility and README; prior exporter direction; not proof of a completed AI tutor |
| S10 | [AutoShop repository](https://github.com/I-am-Mr-Rookie/autoshop-webmcp) | October 18: canonical URL from original checkout's origin; local source/contracts/tests inspected and documentation polished. Public remote and live browser/database behavior not freshly checked. |

## Research sequence

1. Inspected the event tab already open in the user's Chrome profile.
2. Opened its Apply link and observed the authentication redirect. Stopped before login or account creation.
3. Read the event overview/waiver and cross-checked Meta's official event page.
4. Searched Google in Chrome for the event and public application prompts. Search surfaced the official Meta page; no usable public copy of the actual question list or field limits was found in the inspected results. This was a targeted search, not an exhaustive web audit.
5. Checked relevant Meta model/API documentation, not third-party pricing or capability claims.
6. Read the two public portfolio READMEs and matched them to selected local profile/project records. That October 16 version used AgriSense; the October 18 application revision replaces it with AutoShop based on Koushik's instruction and local source/test evidence.
7. Computed Dhaka conversions locally with timezone data. Wrote and verified the local pack.

## October 18 follow-up

Koushik requested AutoShop WebMCP instead of AgriSense, and explicitly authorized changing the original repository after the WebMCP event. The original checkout is `WebMCP Hackathon/Phase 3 Building/Git`. Its application logic was left unchanged; README, architecture, setup, demo, security, and verification documentation were polished. Main and short experience answers, evidence notes, review HTML, and counts were synchronized. Original October 16 event facts were not re-researched by this documentation-only follow-up.

## Authentication observation

Destination after opening S3: `https://cerebralvalley.ai/auth/login`. Rendered UI: Welcome to CV; Continue with Google; Email; Continue; Sign up. No application fields or limits were available. No contact information was typed. A user-held account/session may enable later access; its existence is unknown.

## Source handling

- This folder contains paraphrased research, not a full mirror of the waiver or website.
- No private browser account details, identity images, student exports, or secrets were copied into the deliverables.
- Dates, availability, quotas, documentation, and rules can change. Reopen S1–S4 before submission and again before building.
- Marketing descriptions of model capability are not independent performance evidence. The proposed application claims no benchmark win, measured learning gain, or existing Meta integration.
