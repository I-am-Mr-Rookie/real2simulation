import { writeFileSync, renameSync } from 'node:fs';
import { join } from 'node:path';

const [, , token, root] = process.argv;
const target = join(root, `ready-${process.pid}.json`);
writeFileSync(`${target}.tmp`, JSON.stringify({ pid: process.pid, parentPid: process.ppid, token }));
renameSync(`${target}.tmp`, target);
// Ready means this exact real grandchild has initialized, not that a sleep elapsed.
setInterval(() => {}, 1000);
setTimeout(() => process.exit(1), 60_000);
