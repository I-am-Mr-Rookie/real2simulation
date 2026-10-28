import test from 'node:test';
import assert from 'node:assert/strict';
import { execFile, execFileSync } from 'node:child_process';
import { randomUUID, createHash } from 'node:crypto';
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync,
  realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { setTimeout as delay } from 'node:timers/promises';

const thisFile = fileURLToPath(import.meta.url);
const repository = resolve(dirname(thisFile), '../..');
const service = join(repository, 'Build/lab/session-service.mjs');
const fixtures = join(repository, 'evidence/S10/process-lifecycle/fixtures');
const powershell = join(process.env.SystemRoot || 'C:\\Windows', 'System32/WindowsPowerShell/v1.0/powershell.exe');
const failure = { status: 'error', error: { code: 'lab_request_failed' } };
const start = { action: 'start', template: 'free_fall', mystery: false };
const json = (path) => JSON.parse(readFileSync(path, 'utf8'));
const samePath = (a, b) => typeof a === 'string' && resolve(a).toLowerCase() === resolve(b).toLowerCase();

async function until(predicate, label, timeout = 10_000) {
  const end = Date.now() + timeout;
  do { const value = await predicate(); if (value) return value; await delay(40); } while (Date.now() < end);
  throw new Error(`Timed out: ${label}`);
}

function alive(pid) {
  assert.ok(Number.isSafeInteger(pid) && pid > 0);
  try { process.kill(pid, 0); return true; } catch (error) { if (error.code === 'ESRCH') return false; throw error; }
}

function identities(pids) {
  for (const pid of pids) assert.ok(Number.isSafeInteger(pid) && pid > 0);
  const filter = pids.map((pid) => `ProcessId = ${pid}`).join(' OR ');
  const script = `$ErrorActionPreference='Stop'; @(Get-CimInstance Win32_Process -Filter '${filter}' | Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine,@{Name='Created';Expression={$_.CreationDate.ToUniversalTime().ToString('o')}}) | ConvertTo-Json -Compress`;
  const result = execFileSync(powershell, ['-NoProfile', '-NonInteractive', '-Command', script],
    { encoding: 'utf8', timeout: 10_000, windowsHide: true }).trim();
  const parsed = result ? JSON.parse(result) : [];
  return Array.isArray(parsed) ? parsed : [parsed];
}

function records(root) {
  return readdirSync(root).filter((name) => /^bridge-\d+\.json$/.test(name)).map((name) => json(join(root, name)));
}

function assertOwned(identity, record, config, root, kind) {
  const parent = kind === 'bridge';
  assert.equal(identity.ProcessId, parent ? record.pid : record.childPid);
  assert.equal(identity.ParentProcessId, parent ? config.harnessPid : record.pid);
  assert.equal(record.token, config.token);
  assert.equal(record.parentPid, config.harnessPid);
  assert.ok(samePath(identity.ExecutablePath, parent ? config.python : config.node), 'owned executable');
  const commandLine = identity.CommandLine.replaceAll('/', '\\').toLowerCase();
  assert.ok(commandLine.includes(join(root, parent ? 'Build/lab/session-bridge.py' : 'idle-child.mjs').toLowerCase()), 'owned fixture path');
  if (!parent) assert.ok(identity.CommandLine.includes(config.token), 'owned child token');
  assert.ok(identity.Created, 'OS creation time recorded');
}

// Failure cleanup is deliberately separate from the cancellation under test.
// Re-query identity before killing; never target names, unrelated PIDs or a reused PID.
async function cleanupOwned(root, config) {
  const actions = [];
  for (const record of records(root)) {
    for (const [kind, pid] of [['bridge', record.pid], ['child', record.childPid]]) {
      if (!alive(pid)) continue;
      const identity = identities([pid]).find((item) => item.ProcessId === pid);
      if (!identity) continue;
      assertOwned(identity, record, config, root, kind);
      const captured = record.identities?.find((item) => item.ProcessId === pid);
      if (captured) assert.equal(identity.Created, captured.Created, 'no PID reuse');
      // No /T in fallback cleanup: only this exact, just-validated PID is terminated.
      execFileSync('taskkill', ['/PID', String(pid), '/F'], { timeout: 10_000, windowsHide: true, stdio: 'pipe' });
      actions.push({ pid, method: 'taskkill /PID exact-owned-PID /F', identity });
      await until(() => !alive(pid), `cleanup PID ${pid}`, 8000);
    }
  }
  return actions;
}

async function harness(root, actualService) {
  const config = json(join(root, 'config.json'));
  config.harnessPid = process.pid;
  writeFileSync(join(root, 'config.json'), JSON.stringify(config));
  process.env.PYTHON = config.python;
  process.chdir(root);
  const { handleLab, _sessionTest } = await import(pathToFileURL(actualService).href);
  const requests = [], owned = [], events = [];
  const evidence = { platform: process.platform, node: process.version, service: actualService,
    sourceSha256: createHash('sha256').update(readFileSync(actualService)).digest('hex'),
    root, harnessPid: process.pid, events, trees: owned, cleanup: [] };
  writeFileSync(join(root, 'result.json'), JSON.stringify(evidence, null, 2));
  function launch() {
    const controller = new AbortController();
    const request = { controller, settled: false };
    request.promise = handleLab(start, { signal: controller.signal }).then((reply) => {
      request.settled = true; request.reply = reply; return reply;
    });
    requests.push(request); return request;
  }
  async function ready(request) {
    const record = await until(() => records(root).find((r) => !owned.some((o) => o.pid === r.pid) &&
      existsSync(join(root, `ready-${r.childPid}.json`))), 'Python and Node PID readiness');
    const child = json(join(root, `ready-${record.childPid}.json`));
    assert.deepEqual(child, { pid: record.childPid, parentPid: record.pid, token: config.token });
    assert.equal(request.settled, false, 'bridge must remain live before abort');
    record.identities = identities([record.pid, record.childPid]);
    assert.equal(record.identities.length, 2);
    assertOwned(record.identities.find((i) => i.ProcessId === record.pid), record, config, root, 'bridge');
    assertOwned(record.identities.find((i) => i.ProcessId === record.childPid), record, config, root, 'child');
    assert.ok(alive(record.pid) && alive(record.childPid), 'both exact owned PIDs alive immediately before abort');
    record.requestIndex = requests.indexOf(request);
    owned.push(record);
    writeFileSync(join(root, `bridge-${record.pid}.json`), JSON.stringify(record));
    return record;
  }
  async function abortAndVerify(request, record) {
    assert.ok(alive(record.pid) && alive(record.childPid));
    const abortedAt = Date.now();
    request.controller.abort();
    await until(() => request.settled, `abort settles request ${record.pid}`, 10_000);
    assert.deepEqual(await request.promise, failure);
    await until(() => !alive(record.pid) && !alive(record.childPid), `OS tree ${record.pid} terminates`, 10_000);
    events.push({ action: 'abort', bridgePid: record.pid, childPid: record.childPid,
      abortedAt: new Date(abortedAt).toISOString(), bothDeadAfterMs: Date.now() - abortedAt,
      response: request.reply, activeBridges: _sessionTest.getActiveBridges(), sessions: _sessionTest.sessions.size,
      serviceKillMethod: 'actual Windows stopTree: taskkill /PID bridge-PID /T /F (unmocked)' });
    assert.equal(_sessionTest.sessions.size, 0, 'no post-abort successful session');
  }
  try {
    for (let index = 0; index < 4; index += 1) { const request = launch(); await ready(request); }
    assert.equal(_sessionTest.getActiveBridges(), 4);
    assert.deepEqual(await handleLab(start), failure);
    assert.equal(records(root).length, 4, 'busy fifth request must not spawn a process');
    events.push({ action: 'four-real-trees-fill-capacity; fifth-rejected', activeBridges: 4 });
    await abortAndVerify(requests[0], owned[0]);
    assert.equal(_sessionTest.getActiveBridges(), 3);
    const replacement = launch(); await ready(replacement);
    assert.equal(_sessionTest.getActiveBridges(), 4, 'real replacement occupies released slot');
    events.push({ action: 'capacity-recovered-with-real-replacement', activeBridges: 4 });
    for (let index = 1; index < requests.length; index += 1) await abortAndVerify(requests[index], owned[index]);
    assert.equal(_sessionTest.getActiveBridges(), 0);
    assert.equal(_sessionTest.sessions.size, 0);
    assert.ok(owned.every((record) => !alive(record.pid) && !alive(record.childPid)));
    evidence.status = 'PASS';
  } finally {
    // Do not mask leaked descendants with cleanup before the OS-death assertions above.
    for (const request of requests) if (!request.settled) request.controller.abort();
    await until(() => requests.every((request) => request.settled), 'final pending requests', 10_000).catch((error) => {
      evidence.finalSettleError = error.message;
    });
    try { evidence.cleanup = await cleanupOwned(root, config); }
    finally { writeFileSync(join(root, 'result.json'), JSON.stringify(evidence, null, 2)); }
  }
}

if (process.argv[2] === '--process-tree-harness') {
  await harness(process.argv[3], process.argv[4]);
} else {
  test('Windows actual session service abort kills owned Python/Node trees and restores real capacity',
    { skip: process.platform !== 'win32' ? 'Windows OS process-tree evidence only' : false, timeout: 120_000 }, async (t) => {
      const root = mkdtempSync(join(tmpdir(), 'real2sim-process-tree-'));
      const config = { token: randomUUID(), node: process.execPath,
        python: execFileSync('python', ['-c', 'import sys; print(sys.executable)'],
          { encoding: 'utf8', timeout: 10_000, windowsHide: true }).trim() };
      mkdirSync(join(root, 'Build/lab'), { recursive: true });
      copyFileSync(join(fixtures, 'session-bridge.py'), join(root, 'Build/lab/session-bridge.py'));
      copyFileSync(join(fixtures, 'idle-child.mjs'), join(root, 'idle-child.mjs'));
      writeFileSync(join(root, 'config.json'), JSON.stringify(config));
      let output;
      try {
        output = await new Promise((resolveOutput, reject) => {
          execFile(process.execPath, [thisFile, '--process-tree-harness', root, service],
            { cwd: root, timeout: 90_000, windowsHide: true, maxBuffer: 1024 * 1024 }, (error, stdout, stderr) => {
              if (error) { error.message += `\n${stdout}\n${stderr}`; reject(error); }
              else resolveOutput({ stdout, stderr });
            });
        });
        const result = json(join(root, 'result.json'));
        assert.equal(result.status, 'PASS');
        assert.equal(result.trees.length, 5);
        assert.deepEqual(result.cleanup, [], 'success must be service cancellation, not fallback cleanup');
        assert.equal(result.finalSettleError, undefined);
        assert.equal(result.sourceSha256, createHash('sha256').update(readFileSync(service)).digest('hex'));
        t.diagnostic(JSON.stringify(result));
        assert.equal(output.stderr, '');
      } finally {
        const finalConfig = json(join(root, 'config.json'));
        const cleanup = await cleanupOwned(root, finalConfig);
        if (cleanup.length) t.diagnostic(`FALLBACK CLEANUP: ${JSON.stringify(cleanup)}`);
        if (existsSync(join(root, 'result.json')) && !output) t.diagnostic(readFileSync(join(root, 'result.json'), 'utf8'));
        assert.ok(records(root).every((record) => !alive(record.pid) && !alive(record.childPid)), 'all owned recorded PIDs dead');
        assert.equal(dirname(resolve(root)).toLowerCase(), resolve(tmpdir()).toLowerCase());
        assert.ok(basename(root).startsWith('real2sim-process-tree-'));
        assert.ok(samePath(realpathSync(root), root), 'resolved temporary cleanup target, not a symlink');
        rmSync(root, { recursive: true });
      }
    });
}
