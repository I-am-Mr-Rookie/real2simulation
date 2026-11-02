# N64-orch317 REPORT
Status: DONE (PARTIAL on gaps below)
Changed: public /guide page (10 sections, 16 WebP screenshots, alt text, numbered steps), "Guide" link in SiteFrame header nav and footer.
Files: Build/web/src/app/(public)/guide/{page.jsx,guide-data.mjs,guide.css}, Build/web/public/guide/*.webp (3 to 120 KB), tests/web-guide/guide.test.mjs, SiteFrame.jsx.
Checks: node --test tests/web-guide/guide.test.mjs 2/2 pass; npm run build pass; in-app browser on local build at 1280 and 375 px, no overflow, header fits, no em dash.
Paid calls: none. No uploads, rooms, rebuilds, deploy or push.
Screenshots: fixture signed in via email code (signed out and in once for the sign-in shot); the sample classroom room, fixture QA measurement, public library only. Not captured: private room, owner clips, any email (code step not shot). Test-clip person thumbnails cropped out.
Side effects: New project clicked twice on fixture (1 empty project added); a ball added in the sample lab was not saved.
Gaps (left out or unverified): "3 new rooms a day" not shown in the UI; guide states "3 room rebuilds a day" from API code (MAX_REBUILDS), not seen live. Green GPU dot with countdown not seen live (only red); taken from live.mjs source. Build lab shell, Mark A4 click, Add real object click, scale entry, voice recording and Wonder/Open model chat not run (paid or state-changing). Redo-with-changes only shown as opened replay.
Owner note (Nov 3): the guide does not mention judging-day quota increases.
Risks: screenshots show the DEV dark UI; will date as UI changes. node --test needs the file path, not the directory, on Windows.

