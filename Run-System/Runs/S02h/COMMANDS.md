# Reproduction / exceptions

Run from this worktree root; all source media reads are read-only.

```powershell
$media='C:/Users/HP/.codex/worktrees/s02f-research/2026-10-26 - Meta Global AI Developer Hackathon/evidence/clips/calibration-recovery/S02f/media/RP03-impact-240p.webm'
python evidence/clips/calibration-recovery/S02h/audit_clock.py $media
python evidence/clips/calibration-recovery/S02h/audit_clock.py
# Exact sheet example; zero-based decoded indices, row-major ordering.
ffmpeg -v error -i $media -vf "select='between(n,1320,1349)',scale=426:240,tile=6x5" -frames:v 1 replay-check.jpg
```

All retained sheets were generated with ffmpeg select/scale/tile; exact index
sets are in filenames or FINDINGS. Origin1145..1174, realtime690..719;
clock-anchor indices1144,1145,1146,1150,1319,1325,1439,1445;
comparison714,720,726,1324,1325,1427,1547,1667;
slates0,4320,5760. Overview uses `-ss 10 -t 48 -vf fps=1,scale=426:240,tile=6x8`;
fps sampling can select centred frames, so overview is NOT an exact index map.
All substantive sheets were viewed, not only generated; origin and consecutive
clock sheets provide actual label reads. Overview aids navigation only.

## Source tool operations

- Firecrawl creator article, Commons file page and DJI specs:3 successful scrapes,
  each reports1 credit. Creator/Commons live-request cache miss; DJI cache hit.
  Relevant metadata and paraphrases saved in evidence. No creator contact.
- Initial Firecrawl scrape omitted required `objective`: schema error, no data;
  corrected contract on next call. One scrape-feedback call returned400
  INVALID_BODY / retryable=false; stopped, no refund/success claimed.
- Independent web opened Commons/DJI and searched creator/DJI plus OpenCV primary
  camera model. Creator direct web access failed429; no retries/bypass. Successful
  Firecrawl creator retrieval preceded that failure. Coverage not exhaustive.
- Initial reference filenames search.md/scrape.md were absent; selected installed
  site-collection.md and feedback.md instead. No install/config changes.
- Python source-text inspection first failed on Windows cp1252. Corrected to
  explicit UTF-8/PYTHONUTF8; source receipt retained paraphrases, not full prose.
- S07a Build/measurement files absent in this older base; read actual contract
  from retained s07a worktree, not fabricated or imported. No product edits.
- One combined delete/add patch of creator-source failed duplicate-target
  validation; repaired with separate scoped delete/add. No evidence lost:
  returned source was still in session store, replaced with metadata/paraphrase.

OpenCV/numpy/Pillow were already installed. No dependency installation, new
media retrieval, model call, fitter, GPU, quota poll or public upload.
