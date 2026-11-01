# N32-orch284 REPORT
Status: DONE
Changed: LICENSES/Stability-AI-Community-License.md (HF raw LICENSE.md, source+date header), NOTICE (receipt text, no trailing newline), README Credits line, SiteFrame footer "Powered by Stability AI", tests/web-private/notice.test.mjs (NOTICE == receipt; outside Owns, test only).
Checks: npm run build OK (BUILD_ID written; first run hit a stale lock from an earlier timed-out call, removed and rerun); node --test web-private + shell-workspace 59 pass; headed Playwright Chromium footer shots at 1280 and 375 in evidence/N32/ (text confirmed).
Paid calls: none. Deploy: none.
Skipped: /about page has no separate Stability text beyond the shared footer.
Risks: screenshots from local next start (/about), not DEV. Licence text fetched with HF_TOKEN (value not recorded).
