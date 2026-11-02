# In-app browser checks, 2026-11-02

The initially unavailable in-app browser recovered after Koushik requested another attempt. Human-like checks used the ChatGPT in-app browser, not Chrome. Headed Playwright Chromium was used separately for automated assertions.

- Isolated loopback API and proxy expose only public RM04/ST03 and generated template data. Paid routes are blocked. A temporary public workspace harness renders the real PrivateWorkspace without Clerk, and is removed before the final production build. Authentication was not bypassed in shipping code.
- At 375 x 900 dark: opened measured replay, observed its API fit/uncertainty and RECORDED/scale/clock labels; changed trace slider from index 18 to 4 and observed time 0.17 s. The graph fits its own wrapped row.
- At 375 x 900 dark and light: Add shows all three tile columns within the viewport, scrolls through Probes to Template trials, closes on Escape and restores Add focus. It is above the Room sheet.
- Workspace light 375 and 1366: palette is in the workspace bar, site header is hidden, prompt Send and picker stay within the card, Saved lab cards show their actual saved template images. Dark phone workspace also inspected.
- Public classroom, light 1366: Room view PNG is visible; armed A4, placed one marker, switched Objects then Room. Pressed A4 and first marker survived. No second calibration point was submitted. Scale remains unverified.
- Final production build: room panel image fits its available content width after fixing the newly wrapped panel's min-content sizing. At 375, its sheet scrolls independently and Add stays above it.
- Screenshot PNGs remain local-only in this directory, not committed. Browser matrix assertions and network statuses are in browser-receipts.json.

Skipped: real sign-in/sign-out, microphone permission, real transcription, paid agent/segmentation/shell calls, physical calibration and DEV deployment. These local checks do not prove those paths.
