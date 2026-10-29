"""Caller deadlines only; provider cancellation/stop requires fresh confirmation."""
import asyncio
import math
import time


# orch13: 900s total fits the session deadline; admission window = 900-60-90-480-60 = 210s (controller cap 300s).
TOTAL_SECONDS = 900
STARTUP_SECONDS = 90
EXECUTION_SECONDS = 480
CLEANUP_SECONDS = 60
STOP_SECONDS = 20
EXIT_SECONDS = 10


class ResourceIncident(RuntimeError):
    """The caller cannot confirm that all remote resources stopped."""


async def guarded_probe(app, probe, args, record, *, total_seconds=TOTAL_SECONDS,
                        clock=time.monotonic, sleep=asyncio.sleep,
                        deadline=None, save_result=None):
    # Start before app.run(): image/function setup and queue wait consume this budget.
    started = clock()
    if not math.isfinite(total_seconds) or total_seconds <= (
            STARTUP_SECONDS + EXECUTION_SECONDS + CLEANUP_SECONDS):
        raise ValueError("Budget cannot admit startup, execution and cleanup")
    end = started + total_seconds
    if deadline is not None:
        if not math.isfinite(deadline) or deadline <= 0:
            raise ValueError("Need a finite positive absolute deadline")
        end = min(end, deadline)
    admission_end = end - STARTUP_SECONDS - EXECUTION_SECONDS - CLEANUP_SECONDS
    if admission_end <= started:
        raise TimeoutError("Absolute budget exhausted before remote setup")
    work_end = end - CLEANUP_SECONDS

    async def before(deadline, operation):
        remaining = deadline - clock()
        if remaining <= 0:
            raise TimeoutError("Caller deadline exhausted")
        result = await asyncio.wait_for(operation(), timeout=remaining)
        if clock() > deadline:
            raise TimeoutError("Caller deadline exhausted")
        return result

    context = app.run.aio()
    entered = False
    attempted_setup = False
    call = None
    result_task = None
    receipt = {"total_budget_s": total_seconds, "stop_requested": False,
               "absolute_deadline_monotonic": end, "remaining_at_start_s": end - started,
               "stop_attempted": False, "stop_dispatched": "NOT_VERIFIED",
               "stop_acknowledged": False, "remote_stop_confirmed": False,
               "admission_observed": False, "resource_incident": False}

    def emit():
        try:
            record(receipt.copy())
        except Exception as exc:
            # Broken local evidence storage must never prevent the remote stop attempt.
            receipt["record_error"] = type(exc).__name__

    async def enter():
        nonlocal entered
        await context.__aenter__()
        entered = True

    async def publish_id():
        # SDK sets app_id before image/function setup completes; publish if observed.
        while not app.app_id:
            await asyncio.sleep(.05)
        receipt["app_id"] = app.app_id
        emit()

    publisher = asyncio.create_task(publish_id())

    try:
        attempted_setup = True
        await before(admission_end, enter)
        receipt["app_id"] = app.app_id
        emit()
        call = await before(admission_end, lambda: probe.spawn.aio(*args))
        receipt["function_call_id"] = call.object_id
        emit()
        result_task = asyncio.create_task(before(
            work_end, lambda: call.get.aio(timeout=work_end - clock())))
        # Conservative admission evidence: a running input on this single-input app.
        # A missed/late snapshot fails closed, not a claim of scheduler failure.
        while True:
            if result_task.done():
                break
            stats = await before(admission_end, probe.get_current_stats.aio)
            if stats.num_running_inputs > 0:
                receipt["admission_observed"] = True
                break
            await before(admission_end, lambda: sleep(1))
        result = await result_task
        receipt["result_received"] = True
        emit()
        if save_result is not None:
            # Preserve received bytes BEFORE cleanup, which can block until parent kill.
            save_result(result)
            receipt["result_persisted"] = True
            emit()
        return result
    except BaseException as exc:
        receipt["caller_error"] = type(exc).__name__
        raise
    finally:
        publisher.cancel()
        errors = []
        # A late noncooperative await must not consume the emergency stop attempt.
        # The independent parent enforces the absolute cap, even if this loop hangs.
        cleanup_end = clock() + CLEANUP_SECONDS
        if app.app_id:
            receipt["app_id"] = app.app_id
            # Stop even if spawn never returned a handle. Cancellation alone is not stop.
            async def stop():
                receipt.update(stop_attempted=True, stop_requested=True)
                emit()
                await app.stop.aio()
                receipt.update(stop_dispatched=True, stop_acknowledged=True)
            try:
                await before(clock() + STOP_SECONDS, stop)
            except (Exception, asyncio.CancelledError) as exc:
                errors.append("stop:" + type(exc).__name__)
            try:
                while True:
                    info = await before(cleanup_end - EXIT_SECONDS, lambda: app.info.aio(refresh=True))
                    stats = await before(cleanup_end - EXIT_SECONDS, probe.get_current_stats.aio)
                    if (info.lifecycle.state == "stopped"
                            and stats.num_total_runners == 0
                            and stats.num_running_inputs == 0 and stats.backlog == 0):
                        receipt["remote_stop_confirmed"] = True
                        break
                    await before(cleanup_end - EXIT_SECONDS, lambda: sleep(1))
            except (Exception, asyncio.CancelledError) as exc:
                errors.append("verification:" + type(exc).__name__)
        elif attempted_setup:
            # A lost setup response can hide a created app; absence of an ID is not proof.
            errors.append("setup:unknown_remote_state")
        if result_task is not None:
            if not result_task.done():
                result_task.cancel()
            try:
                await before(cleanup_end - EXIT_SECONDS, lambda: result_task)
            except (Exception, asyncio.CancelledError):
                pass  # Original failure is preserved; app stop is verified independently.
        if entered:
            try:
                # Keep half the exit margin for timer dispatch / local unwinding.
                await before(cleanup_end - EXIT_SECONDS / 2,
                             lambda: context.__aexit__(None, None, None))
            except (Exception, asyncio.CancelledError) as exc:
                errors.append("context_exit:" + type(exc).__name__)
        receipt.update(elapsed_s=clock() - started, cleanup_errors=errors,
                       resource_incident=bool(errors) or not receipt["remote_stop_confirmed"])
        emit()
        if receipt["resource_incident"]:
            raise ResourceIncident("Remote resource incident; inspect deadline receipt")
        if "record_error" in receipt:
            raise OSError("Remote stop confirmed but deadline receipt could not be persisted")
