# Parent acceptance clarification (direct message during this run)

Parent read FINDINGS.md and independently confirmed both root mechanisms.
Core-only fixes are being made by the parent in isolated
`swarm12-covariance-fix`; this worker does not own those fixes.

Direct instruction received before the observed 2026-10-28T20:57:32.5760489Z
clock (message arrival timestamp not exposed):

> Once your bounded audit criteria complete (exact independent repro + tests +
> root/scoped risks + complete investigation), you may report DONE as an AUDIT
> with product defects still open, not product gate success; no requirement to
> own fixes. This clarifies original narrow verification acceptance, not a changed
> deadline.

Parent requested frozen regression tests and a committed pointer for cherry-pick;
no tests/reproducer changes to hide failures and no core edits. Original issue,
cutoff and deadline are unchanged. This is narrow verified-DONE acceptance, not
an early incomplete/safety-stop exception. No broader audit was started.

Frozen regression SHA256:
`DC3EBF3D96EA6D31F0D6CD9483B4EA35E9DD6742900DFDB6FD72AFDFAAA85703`.
Fresh combined suite:42 methods, seven intentional failing (sub)test events
across four methods, exactly the two documented unresolved numerical defects.
