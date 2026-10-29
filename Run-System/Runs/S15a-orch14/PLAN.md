# S15a-orch14 PLAN
Parent project Meta AI Hackathon 91e441f8-e40c-4ec4-bea2-de7fa1582d97. Branch run/S15a-orch14 from main 1430b38.
Objective: document and test the upload/interview/run/fit/report workspace state graph, consuming accepted contracts (shell job DTO, S11 fit reveal, injected S08 validator) with visibly synthetic fixtures only.
Owns: Build/web/src/workspace/; tests/workspace/; evidence/S15/; Run-System/Runs/S15a-orch14/.
Checks: node --test "tests/workspace/*.test.mjs"; evidence/S15/job_schema_diff.py (parseJob vs integration.schema.json); shell test_contract.py unchanged.

