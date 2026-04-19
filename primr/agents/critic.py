import ollama
import json
from ..queue.runner import task_queue
from ..queue.task import Task

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
        task_queue.update_task(
            task.id,
            status="pending",
            bpy_code=review.get("fix", ""),
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

