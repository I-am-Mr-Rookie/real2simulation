"""Offline review evidence only: synthetic inputs, no credentials or network."""
import contextlib
import importlib
import io
import json
import os
import runpy
import threading
import time
from unittest.mock import patch

from fastapi.testclient import TestClient


def main():
    observations = {}
    with patch.dict(os.environ, {}, clear=True):
        deps = importlib.import_module('Build.api.health.dependencies')
        worker = importlib.import_module('Build.worker.health.app')
        config = {
            'R2S_ENVIRONMENT': 'development',
            'REDIS_URL': 'redis://synthetic.invalid/0',
            'BUCKET_ENDPOINT': 'https://synthetic.invalid',
            'BUCKET_NAME': 'synthetic', 'BUCKET_REGION': 'synthetic',
            'BUCKET_ACCESS_KEY_ID': 'synthetic',
            'BUCKET_SECRET_ACCESS_KEY': 'synthetic',
        }
        with patch.object(deps, 'probe', return_value=True) as probe:
            health = deps.DependencyHealth(config, ('redis',))
            observations['missing_railway_environment'] = {
                'enabled': health.enabled, 'states': health.check(),
                'synthetic_probe_calls': probe.call_count,
            }
        with patch.dict(os.environ, config, clear=True), patch.object(deps, 'probe', return_value=True):
            with TestClient(worker.create_app()) as client:
                response = client.get('/health/ready')
                observations['worker_all_dependencies_success'] = {
                    'http_status': response.status_code, 'body': response.json(),
                }
                assert response.status_code == 503
                assert response.json()['dependencies']['heartbeat'] == 'unavailable'

        # Prove shared-pool head-of-line blocking without actual slow connections.
        release = threading.Event()
        started = threading.Event()
        calls = []
        mutex = threading.Lock()
        def blocked(name, env):
            with mutex:
                calls.append(name)
                if len(calls) == 3:
                    started.set()
            release.wait(2)
            return True
        with patch.object(deps, 'probe', side_effect=blocked):
            first = deps.DependencyHealth(config, ('redis',), deadline=.01)
            second = deps.DependencyHealth(config, ('redis',), deadline=.01)
            third = deps.DependencyHealth(config, ('redis',), deadline=.01)
            fourth = deps.DependencyHealth(config, ('bucket',), deadline=.01)
            try:
                for health in (first, second, third):
                    health.check()
                assert started.wait(1)
                start = time.monotonic()
                states = fourth.check()
                observations['shared_pool_contention'] = {
                    'fourth_states': states, 'started_adapter_calls': len(calls),
                    'fourth_adapter_started': 'bucket' in calls,
                    'elapsed_seconds': round(time.monotonic() - start, 4),
                }
                assert states == {'bucket': 'unavailable'} and 'bucket' not in calls
            finally:
                release.set()
                for health in (first, second, third, fourth):
                    for future in health.pending.values():
                        future.result(timeout=3)

    # Execute the real verifier with every HTTP response replaced locally.
    # Deliberately wrong identity/status labels, correct revisions/dependency maps.
    revision = '300cd2096f9e32bcdf3433520b36b67f709df0d5'
    class Response:
        def __init__(self, status, body):
            self.status, self.body = status, body
        def read(self):
            return self.body.encode()
    def fake_urlopen(url, timeout):
        if 'web-dev-' in url:
            return Response(404 if '/workspace/' in url else 200,
                'Real2Simulation No demos are published yet Sign-in unavailable Private workspaces remain unavailable')
        is_worker = 'worker-dev-' in url
        ready = url.endswith('/health/ready')
        dependencies = {'redis': 'ok', 'bucket': 'ok'}
        dependencies['heartbeat' if is_worker else 'postgres'] = 'unavailable' if is_worker else 'ok'
        return Response(503 if is_worker and ready else 200, json.dumps({
            'service': 'WRONG-SERVICE', 'status': 'WRONG-STATUS',
            'revision': revision, 'dependencies': dependencies,
        }))
    capture = io.StringIO()
    with patch('urllib.request.urlopen', side_effect=fake_urlopen), contextlib.redirect_stdout(capture):
        try:
            runpy.run_path('infra/railway/dev/verify.py', run_name='__main__')
        except SystemExit as result:
            exit_code = result.code
    receipt = json.loads(capture.getvalue())
    observations['verifier_wrong_identity_and_status'] = {
        'exit_code': exit_code,
        'passing_checks': sum(bool(c['pass']) for c in receipt['checks']),
        'total_checks': len(receipt['checks']),
        'synthetic_health_body': receipt['checks'][0]['body'],
    }
    assert exit_code == 0
    print(json.dumps(observations, indent=2))


if __name__ == '__main__':
    main()
