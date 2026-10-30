"""Serialized local patch -> synthetic lab rebuild -> S14 numeric receipts. No providers."""
from __future__ import annotations

import copy
from importlib import import_module
import json
from pathlib import Path
import subprocess
import tempfile
from threading import RLock

from Build.agent.tools import fit_tool_output
from Build.lab.pipeline import run_lab
from contracts.agent.validate import TOOL_OUTPUT_VERSION, validate_tool_output
from contracts.experiment.validate_experiment import load_json, validate_setup

patch_tool = import_module("Build.sidebar-tools.spec_patch")
contracts = patch_tool.contracts


class RebuildSession:
    """Trusted per-scene owner; callers supply storage paths/settings, never the model.

    shortcut: current spec and successful receipt live in memory, not a durable queue;
    add transactional storage only when the server composition needs cross-process jobs.
    The lock covers patch commit, preflight, execution and receipt publication.
    """

    def __init__(self, base_spec, *, scene_path, instruments, scratch_dir):
        self._lock = RLock()
        self._spec = copy.deepcopy(base_spec)
        self._scene_path = Path(scene_path).resolve()
        self._scene = load_json(self._scene_path)
        validate_setup(self._spec, self._scene, self._scene_path.parent)
        self._instruments = copy.deepcopy(instruments)
        self._scratch_dir = Path(scratch_dir)
        self._pending = False
        self._completed = None

    @property
    def current_spec(self):
        with self._lock:
            return copy.deepcopy(self._spec)

    def _error(self, call, code, issue):
        return contracts.validate_result({
            "schema_version": contracts.VERSION, "call_id": call["id"],
            "scene_id": call["scene_id"], "tool": call["tool"], "status": "error",
            "payload": {"code": code, "issues": [issue]}, "tool_outputs": [],
        }, call, base_spec=self._spec)

    def handle(self, call) -> contracts.ToolResult:
        """Malformed calls raise SidebarContractError; admitted failures are safe wire errors."""
        with self._lock:
            call = contracts.validate_call(call, base_spec=self._spec)
            if call["tool"] not in ("spec.patch", "scene.rebuild"):
                return self._error(call, "not_ready", "Library search is not handled by the local rebuild session.")
            try:
                if load_json(self._scene_path) != self._scene:
                    return self._error(call, "stale_spec", "Scene bundle changed; open a new validated session.")
                validate_setup(self._spec, self._scene, self._scene_path.parent)
            except (ValueError, OSError):
                return self._error(call, "not_ready", "Scene bundle preflight failed; repair the trusted bundle before retrying.")
            if call["tool"] == "spec.patch":
                result = patch_tool.apply_patch(call, base_spec=self._spec, scene=self._scene,
                                               scene_root=self._scene_path.parent)
                self._spec = copy.deepcopy(result["payload"]["spec"])
                self._pending, self._completed = True, None
                return result
            if call["arguments"]["spec_sha256"] != contracts.spec_sha256(self._spec):
                return self._error(call, "stale_spec", "Rebuild must match the trusted current spec revision.")
            if self._completed is not None:
                result = copy.deepcopy(self._completed)
                result["call_id"] = call["id"]
                return contracts.validate_result(result, call)
            if not self._pending:
                return self._error(call, "not_ready", "Apply a validated spec.patch before requesting a rebuild.")
            if self._scene["synthetic"] is not True or self._spec["template"] not in ("free_fall", "projectile"):
                return self._error(call, "not_ready", "Local rebuild supports synthetic ballistic scenes only; no physical or paid job was started.")
            try:
                with tempfile.TemporaryDirectory(prefix="sidebar-rebuild-", dir=self._scratch_dir) as tmp:
                    spec_path = Path(tmp) / "spec.json"
                    spec_path.write_text(json.dumps(self._spec, allow_nan=False), encoding="utf-8")
                    lab = run_lab(spec_path, self._scene_path, instruments=copy.deepcopy(self._instruments))
                outputs = self._outputs(call["id"], lab)
                result = contracts.validate_result({
                    "schema_version": contracts.VERSION, "call_id": call["id"],
                    "scene_id": call["scene_id"], "tool": "scene.rebuild", "status": "ok",
                    "payload": {"job_id": call["id"], "spec_sha256": contracts.spec_sha256(self._spec),
                                "state": "completed", "output_sha256": {
                                    output["id"]: contracts.output_sha256(output) for output in outputs}},
                    "tool_outputs": outputs,
                }, call)
            except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
                return self._error(call, "internal_error", "Local simulator/fitter rebuild failed; retry this validated request. No numeric output was published.")
            self._completed = copy.deepcopy(result)
            self._pending = False
            return result

    def _outputs(self, job_id, lab):
        if lab["source"] != "simulated" or lab["inputProvenance"] != "synthetic":
            raise ValueError("local lab did not return simulated synthetic evidence")
        # Receipt ids stay within S14's 64-character limit even for maximum-length call ids.
        digest = contracts.spec_sha256(self._spec)
        prefix = digest[:48]
        simulator = validate_tool_output({
            "schema_version": TOOL_OUTPUT_VERSION, "id": f"{prefix}-sim", "tool": "simulator",
            "status": "ok", "quantities": {
                "duration": copy.deepcopy(lab["observations"]["times"][-1]),
                "drop": copy.deepcopy(lab["observations"]["positions"][-1])},
        })
        fitter = fit_tool_output(f"{prefix}-fit", lab["fit"])
        for output in (simulator, fitter):
            for quantity in output["quantities"].values():
                if quantity["source"]["label"] != "simulated":
                    raise ValueError("synthetic local rebuild cannot publish measured quantities")
                quantity["source"]["evidence"] += f"; rebuild {job_id}; spec {digest}; synthetic, not calibrated"
        return [validate_tool_output(output) for output in (simulator, fitter)]
