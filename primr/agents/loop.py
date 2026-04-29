import threading
import time
import bpy

from .planner import plan
from .executor import generate_parallel
from .critic import review_all
from ..queue.runner import task_queue
from .. import executor as bpy_executor
from .. import context as scene_context


def _run_on_main_thread(func, *args, **kwargs):
    """Schedule Blender-touching work through a timer and block until complete."""
    if threading.current_thread() is threading.main_thread():
        return func(*args, **kwargs)

    done = threading.Event()
    result = None
    error = None

    def callback():
        nonlocal result, error
        try:
            result = func(*args, **kwargs)
        except Exception as callback_error:
            error = callback_error
        finally:
            done.set()
        return None

    bpy.app.timers.register(callback, first_interval=0.0)

    while not done.wait(0.05):
        pass

    if error is not None:
        raise error

    return result


def execute_ready_tasks() -> list:
    tasks = [task for task in task_queue.get_all() if task.status == "ready"]
    executed = []

    for task in tasks:
        task_queue.update_task(task.id, status="executing")
        result = _run_on_main_thread(bpy_executor.execute_code, task.bpy_code)
        is_success = result in ("Success", "Code executed successfully.")
        task_queue.update_task(
            task.id,
            result=result,
            status="done" if is_success else "failed",
        )
        executed.append(task)

    return executed


def run_agent(goal: str, model: str, on_update=None):
    task_queue.clear()

    if on_update:
        on_update("planning", None)

    plan(goal, model, on_step=lambda step: on_update("step", step) if on_update else None)

    max_iterations = 20
    iteration = 0
    scene_ctx: str = str(_run_on_main_thread(scene_context.get_scene_context) or "")
    executed_task_ids: set[str] = set()

    while iteration < max_iterations:
        iteration += 1

        pending = task_queue.get_pending()
        if pending:
            if on_update:
                on_update("generating", pending)
            generate_parallel(pending, model, scene_ctx)

        all_tasks = task_queue.get_all()
        done_tasks = [task for task in all_tasks if task.status == "done"]
        current_done_ids = {task.id for task in done_tasks}
        newly_done_ids = current_done_ids - executed_task_ids
        if newly_done_ids:
            executed_task_ids = current_done_ids
            # Refresh context after execution so future generated steps can reference new objects.
            scene_ctx = str(_run_on_main_thread(scene_context.get_scene_context) or "")
            if on_update:
                on_update(
                    "executed",
                    [task for task in done_tasks if task.id in newly_done_ids],
                )

        active = [task for task in all_tasks if task.status not in ("done", "failed")]
        if active:
            time.sleep(0.1)
            continue

        if on_update:
            on_update("reviewing", None)

        summary = review_all(model)
        post_review_tasks = task_queue.get_all()
        post_review_active = [
            task for task in post_review_tasks if task.status not in ("done", "failed")
        ]
        if post_review_active:
            time.sleep(0.1)
            continue

        if on_update:
            on_update("done", summary)
        return summary

    summary = review_all(model)
    if on_update:
        on_update("done", summary)

    return summary

