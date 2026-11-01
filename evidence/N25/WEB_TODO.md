# N25 -> web (Build/web/src, owned by N24 now). Exact changes the backend fixes need

1. F8 errors never show the server message. `Build/web/src/workspace/live-view.mjs:15` errText reads
   `body.error.message` and `body.detail.error.message`, but the API body is `{"detail": {"code", "message", ...}}`.
   Add `r?.body?.detail?.message ||` before the fallback. The 429 upload body now has `detail.message`
   ("Daily upload limit reached: 20 uploads per day. It resets at <UTC time> (midnight Dhaka time). ..."),
   `detail.reason = "daily_upload_limit"` and `detail.reset_at` (ISO UTC). Optionally format reset_at in local time.
2. F1 Result card (`live-view.mjs` Result, ~line 319): when `result.quantity` is absent, show `result.reason`
   (abstain now carries `label` = "<scale label>. No fit: <reason>", `reason`, and a pixel `trajectory`, so
   the chart already draws dots). Results with a fit now also carry `result.curve` =
   `{axis: "y", unit, t_s[49], value[49], band_1sigma[49] or null, label}` from the fitter (coefficients + covariance).
   chartGeom may draw that instead of its own JS refit (same polynomial; band uses the full covariance).
   Pixel value case: quantity `{value, unit: "px/s^2", uncertainty, label: "scale unverified: ..."}` already renders.
3. F4 tag: a typed size now gives quantity.label "scale assumed (user size)" (not MEASURED), result.label
   "scale assumed (user size): <typed text>", scale.size_relative_sigma (default 0.10 or the typed "+/- x cm").
   The tag code `/MEASURED/.test(...)` then shows "scale unverified"; better: show the tag text
   "scale assumed (user size)" when `q.label` starts with it. `shareable()` (unit m/s^2) still allows sharing.
4. F2 experiments list rows now have `sample`: null, or `{title: "SAMPLE (RECORDED): falling apple", label, source}`
   for the seeded row (file_id "sample"). In the Processing list (`live-view.mjs` ~line 255) show `it.sample.title`
   plus a SAMPLE tag instead of the bare id. Open still works (GET returns the recorded result).
5. F6 room scale: `room.scale.reference_rejected` = `{source: "scale from A4 clicks", metres_per_model_unit, reason}`
   when two clicks cannot be one A4 edge (implied rescale outside 0.5x to 2x). The scale is not applied; status stays
   MODEL-ESTIMATED or scale unverified. Show `reference_rejected.reason` in `Build/web/src/lab-editor/LabEditor.jsx:95`
   and in the A4 click result text.
