# N87 checks

Scope: AgentPanel cards/chips and cleanup-only exports/callers, its unused hint CSS, the one agent INSTRUCTIONS sentence, and offline panel tests. No config, dependency, fixture or stored-scene changes. Existing batch-tool handlers/schema/tests, LabEditor Undo and Before/After remain intact. Guide search found no cleanup wording.

Commands run from the run worktree:

```powershell
node --test tests/lab-editor/agent-panel.test.mjs
# 8 passed. Then the exact requested directory-form command:
node --test tests/lab-editor tests/workspace tests/shell-workspace tests/web-guide
# Node 24 treats these directories as module paths: MODULE_NOT_FOUND. Same suites, explicit files:
$files = Get-ChildItem -LiteralPath 'tests/lab-editor','tests/workspace','tests/shell-workspace','tests/web-guide' -Filter '*.test.mjs' -File -Recurse | Select-Object -ExpandProperty FullName
node --test @files
# 47 files; 266 passed, 0 failed, 0 skipped.
python -m pytest tests/agent -q
# 213 passed, 464 subtests passed; installed anyio pytest plugin deprecation warning.
npm --prefix Build/web run build
# PASS, Next.js 16.4.3 webpack production build.
git diff --check
# PASS.
```

Regression coverage: four remaining suggestions fill without sending in both empty cards and post-turn chips; cleanup action and Wonder hint absent in both states; typed batch-tool response makes exactly one scene callback with the preserved honesty label; conversation history remains correct; Undo/redo and Before/After retain both scenes. Existing Python batch-tool tests remain unchanged and pass in the full agent suite.

No browser QA, paid calls, push or deployment. Manual natural-language object edits remain available by design.
