# Harmless S03 dispatcher fixture — never a product queue
| ID | Lane | Model / effort | Step | Min | Task | Depends | Owns (paths) | Acceptance / evidence | Status |
|---|---|---|---|---:|---|---|---|---|---|
| DRY-C1-A | CODEX-1 | GPT-6.1 Sol / medium | DRY1 | 1 | Write harmless marker A | — | dry-run/CODEX-1/A.txt | Exact harmless marker on disk | TODO |
| DRY-C1-B | CODEX-1 | GPT-6.1 Sol / medium | DRY1 | 1 | Write harmless marker B | DRY-C1-A | dry-run/CODEX-1/B.txt | Exact harmless marker on disk | TODO |
| DRY-C2-A | CODEX-2 | GPT-6.1 Sol / medium | DRY2 | 1 | Write harmless marker C | — | dry-run/CODEX-2/A.txt | Exact harmless marker on disk | TODO |
| DRY-CL-A | CLAUDE | Opus 5.5 / medium | DRY3 | 1 | Write harmless marker D | — | dry-run/CLAUDE/A.txt | Exact harmless marker on disk | TODO |
