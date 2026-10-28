"""Research integrity checks, not metric/gate qualification."""
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from PIL import Image

B = Path(__file__).resolve().parent
pts = [float(x) for x in (B/'pts-480p.csv').read_text().splitlines() if x.strip()]
assert len(pts) > 15000
steps = Counter(round(b-a, 6) for a,b in zip(pts, pts[1:]))
assert set(steps) == {0.04}, steps
assert abs(pts[0] - 0.004) < 1e-8
frames = 0
for mapping in B.glob('mapping-*.json'):
    for page in json.loads(mapping.read_text()):
        with Image.open(B/page['sheet']) as im:
            im.verify()
        for m in page['frames']:
            assert abs(pts[m['frame_index_0']] - m['pts_s']) < 0.0006
            frames += 1
assert frames > 500
source = B/'media/RP01-480p.webm'
h = hashlib.sha256(source.read_bytes()).hexdigest()
assert source.stat().st_size == 50013019
decode = subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(source),
                         '-map','0:v:0','-f','null','-'], capture_output=True,text=True)
(B/'decode-480p.txt').write_text(decode.stderr)
assert decode.returncode == 0, decode.stderr
receipt = {'integrity_pass':True,'bytes':source.stat().st_size,'sha256':h,
           'delivered_frame_count':len(pts),'first_pts_s':pts[0],'last_pts_s':pts[-1],
           'delivered_interval_counts_s':dict(steps),'mapped_sheet_frames':frames,
           'full_video_decode_exit':decode.returncode,
           'camera_capture_fps':None,'metric_qualified':False,
           'scope':'Frame/PTS integrity ONLY; not acquisition timing or metric success'}
(B/'verification.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
