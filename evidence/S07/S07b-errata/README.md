# S07b errata (S07b-param-orch40)
- ST03-orch14-frame_map.json: corrects evidence/S07/S07b/orch14 frame_map f76 2.569233 -> 2.535867 s (f58-75 unchanged). Source test-data/public/ST03.mp4 sha256 7239da80...df051 verified.
- RM04-orch40-frame_map.json: corrects evidence/S07/S07b-param/RM04-chair-orch40 f11 0.48 -> 0.44 s.
- Root cause: modal_track._frames used ffprobe -read_intervals %+#(last+1); #N counts packets in DECODE order, so with B-frames (has_b_frames=2) the trailing presentation frames were never decoded and later frames shifted in. Buggy output reproduced exactly; fixed by Build/measurement/runtime/modal_track.py _pts (margin 32 packets, first last+1 frames, monotonic assert); regression test tests/measurement/test_modal_track.py::test_pts_presentation_order_st03 (fails before, passes after).
- Timestamps only; centroids unaffected. Accepted originals not edited. Downstream consumers (S12a boundary) should use these maps.

