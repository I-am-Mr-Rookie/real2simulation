"""Apply a spec.patch locally; return a validated handoff, never run a rebuild."""
from __future__ import annotations

import copy
from importlib import import_module

from contracts.experiment.validate_experiment import validate_setup

# import_module supports the existing hyphenated directory without sys.path edits.
contracts = import_module("Build.sidebar-tools.contracts")
SidebarContractError = contracts.SidebarContractError


def apply_patch(call, *, base_spec, scene, scene_root) -> contracts.ToolResult:
    """Validate a copied candidate against the trusted bundle before any handoff.

    base_spec and scene must come from trusted current storage, not tool arguments.
    Return value is the S16a spec.patch result, not persistence or rebuild approval.
    Invalid inputs raise SidebarContractError and leave caller-owned values alone.
    """
    call = contracts.validate_call(call, base_spec=base_spec)
    if call["tool"] != "spec.patch":
        raise SidebarContractError("apply_patch requires a spec.patch call")
    candidate = copy.deepcopy(base_spec)
    candidate.update(copy.deepcopy(call["arguments"]["patch"]))
    try:
        validate_setup(candidate, scene, scene_root)
    except ValueError as error:
        raise SidebarContractError(str(error)) from error
    result = {
        "schema_version": contracts.VERSION,
        "call_id": call["id"], "scene_id": call["scene_id"], "tool": "spec.patch",
        "status": "ok",
        "payload": {"spec": candidate, "spec_sha256": contracts.spec_sha256(candidate),
                    "rebuild_required": True},
        "tool_outputs": [],
    }
    return contracts.validate_result(result, call, base_spec=base_spec)
