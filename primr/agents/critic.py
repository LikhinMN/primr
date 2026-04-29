import ollama
import json
import threading
import bpy
from ..queue.runner import task_queue
from ..queue.task import Task
from .. import context as scene_ctx
from .. import executor as bpy_executor

CRITIC_PROMPT = """You are Primr Critic, an agent that validates Blender (`bpy`) code execution.

Input:
- Task description (expected outcome)
- Executed `bpy` code
- Execution result (stdout / error message)

Output:
Return ONLY a valid JSON object in this exact format:
{
  "success": true or false,
  "reason": "concise, specific explanation",
  "fix": "corrected bpy code if success is false, otherwise empty string"
}

Evaluation Rules:
- If result contains "Error" or "Exception" -> "success": false
- If result indicates success, verify the code actually fulfills the task intent (not just runs without error)
- Validate both:
  - Runtime correctness (no crashes, proper API usage)
  - Semantic correctness (does the code achieve the task?)

Failure Conditions:
Mark "success": false if any of the following:
- Code does not achieve the described task
- Missing required operations
- Incorrect object references or assumptions
- Non-idempotent behavior that can break on re-run
- Unsafe operations (e.g., relying on undefined selection/active object)
- Violates Blender API best practices for the task

Fix Requirements:
- Provide a fully corrected, minimal, executable `bpy` script
- Fix must directly satisfy the task
- No explanations, no comments, no markdown
- Ensure:
  - Safe object access (`bpy.data.objects.get`)
  - Proper mode handling if needed
  - Idempotency (no duplicate side effects on re-run)

Constraints:
- Do not include anything outside the JSON
- Keep "reason" short but precise
- "fix" must be empty string if "success": true
"""


def _get_scene_context_main_thread() -> str:
    if threading.current_thread() is threading.main_thread():
        return scene_ctx.get_scene_context()

    done = threading.Event()
    result = ""
    error = None

    def callback():
        nonlocal result, error
        try:
            result = scene_ctx.get_scene_context()
        except Exception as callback_error:
            error = callback_error
        finally:
            done.set()
        return None

    bpy.app.timers.register(callback, first_interval=0.0)
    done.wait()

    if error is not None:
        raise error

    return result


def review_task(task: Task, model: str) -> bool:
    review_prompt = f"Task: {task.step}\nCode:\n{task.bpy_code}\nResult: {task.result}"

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": CRITIC_PROMPT},
            {"role": "user", "content": review_prompt},
        ],
        format="json",
        stream=False,
    )
    review = json.loads(response["message"]["content"])

    if review.get("success") is True:
        return True

    if task.retry_count < 3:
        current_scene = _get_scene_context_main_thread()
        fix_prompt = (
            f"Scene state:\n{current_scene}\n\n"
            f"Failed task: {task.step}\n"
            f"Failed code:\n{task.bpy_code}\n"
            f"Error: {review.get('reason', 'Unknown failure')}\n\n"
            "Write corrected bpy code:"
        )
        fix_response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": CRITIC_PROMPT},
                {"role": "user", "content": fix_prompt},
            ],
            stream=False,
        )
        fix_code = bpy_executor.extract_code(fix_response["message"]["content"])
        if not fix_code.strip():
            fix_code = review.get("fix", "")
        if not fix_code.strip():
            task_queue.update_task(
                task.id,
                status="failed",
                error=review.get("reason", "Review failed"),
            )
            return False

        task_queue.update_task(
            task.id,
            status="ready",
            bpy_code=fix_code,
            result="",
            error="",
            retry_count=task.retry_count + 1,
        )
        return False

    task_queue.update_task(
        task.id,
        status="failed",
        error=review.get("reason", "Review failed"),
    )
    return False


def review_all(model: str) -> dict:
    tasks = task_queue.get_all()
    completed_tasks = [task for task in tasks if task.status == "done"]

    summary = {
        "total": len(completed_tasks),
        "succeeded": 0,
        "failed": 0,
        "errors": [],
    }

    for task in completed_tasks:
        success = review_task(task, model)
        if success:
            summary["succeeded"] += 1
            continue

        summary["failed"] += 1
        refreshed = next((item for item in task_queue.get_all() if item.id == task.id), task)
        summary["errors"].append(
            {
                "step": task.step,
                "reason": refreshed.error or "Review failed",
            }
        )

    return summary

