# Voice-over edit brief (owner notes, Nov 1 2026)

Applies to S24i (cut video and align captions) and any later audio pass.
Takes: media/narration/takes/ (gitignored, private owner audio; never commit or upload).
Script: media/narration/READ_SCRIPT.md. 25 takes, b01-01 .. b09-02, all present.

## What Koushik told us

- Leading silence in each take is intentional (1.8 to 5.3 s); trim it.
- Trailing silence on some takes is a mistake; trim it too.
- Some takes are loud, some quiet (b09-02 is the quietest, mean about -40 dB). Even them out.
- Played raw, the takes sound like a textbook read. The final video must feel like a
  real product walkthrough, not a script read over screenshots.

## Edit direction (act as a senior video editor and product marketer)

Audio
- Trim each take to speech with about 0.15 s head and 0.25 s tail; keep natural breaths inside sentences.
- Clean chain per take: high-pass about 80 Hz, gentle de-ess, light compression (about 3:1), then
  loudness-normalize the whole voice track to about -16 LUFS integrated, true peak <= -1.5 dBTP.
- Background music: one calm, modern, instrumental bed with clear licence (Pixabay Music,
  CC0 or CC BY with credit; no NC/ND, nothing ripped from YouTube). Record title, author,
  URL and licence in ATTRIBUTION.md. If none is clearly licensed, synthesize a simple pad
  with ffmpeg instead. Duck music about 12 to 15 dB under the voice (sidechain), bring it
  up in gaps and on the opening and closing shots; fade in 1 s, fade out 2 s.
- Optional subtle UI sound accents on key reveals (result card, prediction vs actual) only
  if licensed or synthesized; keep them quiet.

Picture and pacing
- Cut picture to the voice, not the other way round. Use J and L cuts so the screen
  action starts slightly before or after the line.
- No dead air: tighten pauses between takes to 0.3 to 0.6 s; let a key result hold 1 to 1.5 s.
- Smooth zooms or crops onto the part of the UI being described (cursor, result card,
  g with its uncertainty). Avoid jumpy cuts and fast flashes.
- Beat 5b takes run about 59 s raw against a 20 s slot; rebalance the whole timeline so the
  final cut is <= 3:00. Shorten picture holds first; drop or trim whole takes only if needed,
  and never cut a caveat or label line.
- Burned-in captions that match the spoken words; keep them short and readable.

Truth rules (unchanged)
- Labels verbatim: RECORDED, SIMULATED, MEASURED, what-if, scale unverified, ABSTAINED,
  held-out caveats. Numbers only from code or API output. No em dashes in any on-screen text.
- Only OWN07 owner footage snippets are approved for the public video (face-free trims).
- Third-party clips keep creator credit on screen and in ATTRIBUTION.md.
- Export locally only. Public upload needs Koushik's written go-ahead (S24j).

Deliver: final MP4 (1080p, H.264, AAC), a short EDIT_LOG with the ffmpeg commands, the music
licence, measured loudness (ffmpeg loudnorm or ebur128 readout) and total duration.
