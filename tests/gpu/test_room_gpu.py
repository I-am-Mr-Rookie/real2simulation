"""N30 room GPU preference, narrow fallback, list-rate cost and Modal override (offline)."""
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from Build.gpu.cost_log import cost
from Build.gpu.image_spec import GPU
from Build.reconstruction import live_room


@pytest.mark.parametrize("error", [RuntimeError("CUDA out of memory"),
                                    RuntimeError("CUDA error: out of memory"),
                                    RuntimeError("no GPU capacity available"),
                                    type("OutOfMemoryError", (RuntimeError,), {})("allocation failed"),
                                    type("ResourceExhaustedError", (RuntimeError,), {})("no GPU capacity")])
def test_retry_choice(error):
    assert live_room.retry_on_a10g(error)


@pytest.mark.parametrize("error", [RuntimeError("authentication failed"), ValueError("bad frames"),
                                    TimeoutError("execution timed out"), RuntimeError("model failed"),
                                    type("ResourceExhaustedError", (RuntimeError,), {})("quota exceeded"),
                                    type("ResourceExhaustedError", (RuntimeError,), {})("rate limit")])
def test_other_errors_do_not_retry(error):
    assert not live_room.retry_on_a10g(error)


def test_l4_default_and_actual_gpu_prices():
    assert GPU == live_room.GPU == "L4"
    assert live_room.FALLBACK_GPU == "A10G"
    assert cost(100, "L4", 2, 16)["total_usd"] == 0.028372
    assert cost(100, "A10G", 2, 16)["total_usd"] == 0.036772
    assert live_room.ESTIMATE_USD == cost(1440, "L4", 2, 16)["total_usd"]


def test_fallback_uses_existing_deployed_function(monkeypatch):
    fn = Mock()
    lookup = Mock(return_value=fn)
    monkeypatch.setitem(sys.modules, "modal", SimpleNamespace(Function=SimpleNamespace(from_name=lookup)))
    live_room.modal_reconstruct([b"frame"])
    fn.spawn.assert_called_once_with([b"frame"])
    fn.spawn.return_value.get.assert_called_once_with(timeout=live_room.ROOM_START_BUDGET_S)
    fn.with_options.assert_not_called()
    live_room.modal_reconstruct([b"frame"], gpu="A10G")
    fn.with_options.assert_called_once_with(gpu="A10G")
    fn.with_options.return_value.spawn.assert_called_once_with([b"frame"])
    fn.with_options.return_value.spawn.return_value.get.assert_called_once_with(timeout=540)
    assert lookup.call_args.args == ("r2s-ondemand", "reconstruct")


def test_l4_budget_cancels_before_retry_choice(monkeypatch):
    fn = Mock()
    timeout = type("TimeoutError", (Exception,), {})
    fn.spawn.return_value.get.side_effect = timeout("still queued")
    monkeypatch.setitem(sys.modules, "modal", SimpleNamespace(
        Function=SimpleNamespace(from_name=Mock(return_value=fn)), exception=SimpleNamespace(TimeoutError=timeout)))
    with pytest.raises(RuntimeError, match="no GPU capacity/result") as error:
        live_room.modal_reconstruct([b"frame"])
    fn.spawn.return_value.cancel.assert_called_once_with(terminate_containers=True)
    assert live_room.retry_on_a10g(error.value)


@pytest.mark.parametrize("builtin", [False, True])
def test_a10g_timeout_cancels_without_another_retry(monkeypatch, builtin):
    fn = Mock()
    timeout = type("TimeoutError", (Exception,), {})
    call = fn.with_options.return_value.spawn.return_value
    error = TimeoutError if builtin else timeout
    call.get.side_effect = error("still queued")
    monkeypatch.setitem(sys.modules, "modal", SimpleNamespace(
        Function=SimpleNamespace(from_name=Mock(return_value=fn)), exception=SimpleNamespace(TimeoutError=timeout)))
    with pytest.raises(error):
        live_room.modal_reconstruct([b"frame"], gpu="A10G")
    call.cancel.assert_called_once_with(terminate_containers=True)
