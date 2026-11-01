// N24: Projects card grouping, SAMPLE label and short readable names.
import test from 'node:test';
import assert from 'node:assert/strict';
import { shortId, shortWhen, jobName, isSample, projectName, groupJobs } from '../../Build/web/src/workspace/projects.mjs';

test('long ids become short readable names', () => {
  assert.equal(jobName({ id: 'a'.repeat(32), sample: { title: 'SAMPLE (RECORDED): falling apple' } }, 'experiment'), 'SAMPLE (RECORDED): falling apple'); // N26
  assert.equal(shortId('acdb8a00edca4ba8b60f264f505719da'), 'acdb8a');
  assert.equal(shortId('room-1'), 'room-1');
  assert.equal(jobName({ id: 'acdb8a00edca4ba8b60f264f505719da' }, 'experiment'), 'Experiment acdb8a');
  assert.equal(jobName({ id: 'x', title: 'acdb8a00edca4ba8b60f264f505719da' }, 'room'), 'Room x');
  assert.equal(jobName({ id: 'x', title: 'Pendulum swing' }, 'experiment'), 'Pendulum swing');
  assert.equal(shortWhen('2026-11-01T13:05:59Z'), 'Nov 1, 13:05 UTC');
  assert.equal(shortWhen('nope'), '');
  assert.equal(shortWhen(null), '');
});

test('jobs group under their project; SAMPLE last and labelled; unknown project last', () => {
  const projects = [{ id: 's', title: 'SAMPLE (RECORDED): classroom room and falling apple', mode: 'room' }, { id: 'p1', title: 'Experiment 2026-11-01 13:05', mode: 'experiment' }];
  const g = groupJobs(projects, [{ id: 'e1', project_id: 'p1' }, { id: 'e2', project_id: 's' }, { id: 'e3', project_id: null }], [{ id: 'r1', project_id: 's' }]);
  assert.deepEqual(g.map((x) => x.id), ['p1', 's', null]);
  assert.equal(g[1].sample, true); assert.equal(isSample(projects[1]), false);
  assert.equal(g[1].name, 'classroom room and falling apple');
  assert.deepEqual(g[1].rooms.map((r) => r.id), ['r1']); assert.deepEqual(g[1].experiments.map((e) => e.id), ['e2']);
  assert.deepEqual(g[2].experiments.map((e) => e.id), ['e3']);
  assert.equal(projectName({ id: 'abcdef1234567890' }), 'Project abcdef');
  assert.deepEqual(groupJobs(), []);
});
