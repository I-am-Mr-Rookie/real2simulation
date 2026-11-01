import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
test("NOTICE equals the SF3D licence receipt text", () => {
  const receipt = readFileSync("evidence/owner/S06/SF3D-LICENCE.md", "utf8").match(/NOTICE file with exactly: "(.+)"/)[1];
  assert.equal(readFileSync("NOTICE", "utf8"), receipt);
});
