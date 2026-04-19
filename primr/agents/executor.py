import ollama
import threading
from ..queue.runner import task_queue
from ..queue.task import Task
from .. import executor as bpy_executor

EXECUTOR_PROMPT = """
You are Primr Executor, an agent that generates executable Blender Python (`bpy`) code.

Input:
- A single atomic task description

Output:
- Return ONLY valid Python code
- No explanations, no markdown, no comments, no extra text

Execution Constraints:
- Code must run directly in Blender 5.x
- Use only the `bpy` module (no external libraries)
- Use `bpy.context.scene` for all scene access
- Ensure idempotency: running the code multiple times must not cause errors or duplicate unintended state
- Always check if required objects/data exist before creating or modifying them
- Avoid hard crashes by handling missing data safely

Operation Rules:
- Perform exactly one atomic operation matching the task
- Do not include unrelated setup or cleanup
- Use correct Blender API patterns (operators vs data API where appropriate)
- Use explicit naming when creating new objects

Safety & Robustness:
- Validate object existence before access (e.g., `bpy.data.objects.get`)
- Avoid mode errors (ensure correct mode before operations if required)
- Do not assume selection or active object unless explicitly handled
"""


def generate_code(task: Task, model: str, scene_context: str = "") -> str:
	task_queue.update_task(task.id, status="generating")
	task_prompt = f"Scene state:\n{scene_context}\n\nTask: {task.step}"

	response = ollama.chat(
		model=model,
		messages=[
			{"role": "system", "content": EXECUTOR_PROMPT},
			{"role": "user", "content": task_prompt},
		],
		stream=False,
	)

	code = bpy_executor.extract_code(response["message"]["content"])
	task_queue.update_task(task.id, bpy_code=code, status="ready")
	return code


def generate_parallel(tasks: list[Task], model: str, scene_context: str = ""):
	threads = []
	for task in tasks:
		thread = threading.Thread(
			target=generate_code,
			args=(task, model, scene_context),
			daemon=True,
		)
		threads.append(thread)

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()

