import ollama
import threading
from ..queue.runner import task_queue
from ..queue.task import Task
from .. import executor as bpy_executor

EXECUTOR_PROMPT = """
You are Primr's Executor agent. You write Blender Python (bpy) code.

Rules you MUST follow:
1. After adding any object, immediately name it:
   bpy.context.object.name = "descriptive_name"
2. Always use the object's exact name to reference it in later operations.
3. Position objects logically when the task implies hierarchy (for example: trunk near origin, leaves above trunk).
4. No explanations, no markdown, no comments, only raw executable Python.
5. Always check objects exist before use:
   obj = bpy.data.objects.get("name")
6. The code runs in Blender 5.x with bpy available.

Quality constraints:
- Return only valid executable Python.
- Perform exactly one atomic task from the user instruction.
- Keep code idempotent and safe to re-run.
- Do not assume active selection unless you set it explicitly.
- Prefer deterministic object names and references over implicit context.
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

