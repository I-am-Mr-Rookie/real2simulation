"""Local read-only BFF fixture for IAB QA of the real public RM04 output, never authenticated E2E.
Run alongside Next start (production build) on 3098; 3163 serves ONLY this run's public room artifacts.
The 64... room is a SIMULATED interruption response, zero model calls, no changes to live output.
"""
import http.client
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

OUT = Path(__file__).resolve().parent
JOB = OUT / 'live-data/rooms/n63_public_rm04' / ('63' * 16)


class Preview(BaseHTTPRequestHandler):
    def do_GET(self):
        p = urlsplit(self.path).path
        if p.startswith('/api/workspace/'):
            if not p.startswith(tuple('/api/workspace/rooms/' + x * 16 for x in ('63', '64'))):
                return self.send_body(b'{}', 'application/json')
            suffix = p.split('/', 5)[-1]
            if suffix == 'result':
                room = json.loads((JOB / 'room.json').read_text())
                scene = json.loads((JOB / 'scene.json').read_text())
                if '/rooms/' + '64' * 16 in p:
                    item = room['shell']['kept'][0]
                    reason = 'SIMULATED restart regression: SF3D interrupted (server restart)'
                    item['upgrade'] = {'state': 'failed', 'reason': reason}
                    item['fallback_reason'] = reason
                    for obj in scene['objects']:
                        if obj['id'] == item['id']:
                            obj['shape'] = {'type': 'box', 'fallback_reason': reason}
                return self.send_body(json.dumps({'room': room, 'scene': scene}).encode(), 'application/json')
            if suffix.endswith('.glb'):
                name = suffix.rsplit('/', 1)[-1]
                file = JOB / 'objects' / name
                if file.is_file():
                    return self.send_body(file.read_bytes(), 'model/gltf-binary')
            if suffix == 'room.ply':
                return self.send_body((JOB / suffix).read_bytes(), 'application/octet-stream')
            if suffix.startswith('views/'):
                from Build.reconstruction.object_lift import view_png
                png, _, _ = view_png((JOB / 'mapanything.npz').read_bytes(), int(Path(suffix).stem))
                return self.send_body(png, 'image/png')
            status = json.loads((JOB / 'status.json').read_text())
            return self.send_body(json.dumps({'job': status}).encode(), 'application/json')
        connection = http.client.HTTPConnection('127.0.0.1', 3098, timeout=120)
        connection.request('GET', self.path, headers={'Host': '127.0.0.1:3163'})
        response = connection.getresponse()
        body = response.read()
        self.send_body(body, response.getheader('Content-Type', 'text/html'), response.status)
        connection.close()

    def send_body(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(OUT.parents[1]))
    assert JOB.is_dir(), 'Run the single public job first'
    if sys.argv[1:] == ['--check']:
        from urllib.request import urlopen
        base = 'http://127.0.0.1:3163/api/workspace/rooms/'
        with urlopen(base + '63' * 16 + '/result') as response:
            actual = json.load(response)
        meshes = [o for o in actual['scene']['objects'] if o.get('shape', {}).get('type') == 'mesh']
        assert len(meshes) == 4 and all(o['shape']['collider'] == 'box' for o in meshes)
        with urlopen('http://127.0.0.1:3163' + meshes[0]['shape']['glb']) as response:
            assert response.read(4) == b'glTF'
        with urlopen(base + '64' * 16 + '/result') as response:
            simulated = json.load(response)
        reason = simulated['room']['shell']['kept'][0]['upgrade']['reason']
        assert reason == 'SIMULATED restart regression: SF3D interrupted (server restart)'
        assert json.loads((JOB / 'room.json').read_text())['shell']['kept'][0]['upgrade']['state'] == 'ready'
        print('Public preview self-check passed; real meshes and isolated SIMULATED interruption')
        raise SystemExit(0)
    ThreadingHTTPServer(('127.0.0.1', 3163), Preview).serve_forever()
