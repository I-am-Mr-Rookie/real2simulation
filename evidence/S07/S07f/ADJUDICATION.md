# R-M source adjudication (before implementation)

Authority: S07f DISPATCH, R-M CONTROLLER_ACCEPTANCE, GATE_M.md,
UNCERTAINTY.md, approved final plan S07/S12/S14, S07a capture-group evidence.
Reviewer reproducers are synthetic; none establishes real calibration or coverage.

| Finding | Classification / owning contract | Disposition |
|---|---|---|
| F1 inconsistent g/error | Verified summary boundary defect. Gate M compares fitted g with 9.81; caller error cannot override the measurement. | Derive qualification and reported mean error from finite g, not supplied relative_error. Inclusive 5% bounds in g-space avoid division-roundoff excluding the exact boundary. No tolerance or changed percentage. |
| F2 raw group labels | Verified missing trusted independence boundary, not evidence that case-sensitive IDs alias. S07a groups FF01/FF02 together; provenance, not spelling, determines independence. | Default deny panel independence unless trusted caller verifies the exact panel's recording provenance outside outcome dictionaries. Reject noncanonical surrounding whitespace, preserve case-sensitive IDs. This is an explicit trust contract, NOT an implemented provenance authenticator or new real-source grant. |
| F3 evaluator cannot pass | Intentional fail-closed behavior under accepted S07d/GATE_M contracts. Standard uncertainty is not an interval. | Preserve coverage=null and blocker; no k/probability/distribution invented, no hand-patched real outputs. Future independently validated coverage and provenance integration required. |
| F4 suffix RMSE / one suffix frame | Diagnostic is correct; proposed Gate M criterion conflicts with separate approved Gate RS/S14 ownership. S07a requires a nonempty suffix; Gate M specifies g accuracy/covering uncertainty, not a prediction threshold. | Preserve suffix isolation and diagnostics; do not import Gate RS 5%, minimum count, or tune thresholds. No out-of-sample physical capability claimed. |
| F5 precision vs residuals | Reproducer demonstrates conditional uncertainty can mislead when supplied assumptions are unsupported; not a math defect under S07d's explicit external absolute one-standard errors, negligible-systematics/evidence contract. A standard deviation is not a deterministic residual bound. | Do not invent reduced-chi-square acceptance or estimate precision from suffix/training residuals. Require independent justification before any real use; coverage blocker remains. Record limitation explicitly. |
| F6 huge declared calibration errors | Reproducer violates required external small-error adequacy; no universal linearization bound specified or supported. Standard uncertainty cannot confer coverage regardless of its size. | Preserve conditional result and abstain at Gate M coverage boundary; document external adequacy obligation and unsupported large-error example. No invented relative-error ceiling. |

F5/F6 are not certified physically valid merely because conditional propagation
returns a number. Real-media assumption review and empirical interval validation
remain unresolved holds. Controller must obtain other-vendor follow-up on source
gate changes before acceptance; this run does not self-approve them.
