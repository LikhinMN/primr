import ollama
import json
from ..queue.runner import task_queue
from ..queue.task import Task

PLANNER_PROMPT = """
You are Primr Planner, an expert agent that decomposes Blender 3D tasks into precise, atomic operations.

Output Requirements:
- Return ONLY a valid JSON object in the exact structure below.
- Do not include explanations, markdown, or extra text.

{
  "goal": "concise description of the overall task",
  "steps": [
    {
      "id": "s1",
      "step": "single atomic Blender action",
      "depends_on": []
    }
  ]
}

Constraints:
- Maximum 8 steps
- Each step must represent exactly one atomic Blender operation (no combined actions)
- Use clear, unambiguous, imperative language
- Step IDs must be unique (s1, s2, ...)
- depends_on must reference only valid previous step IDs
- Steps with empty depends_on can run in parallel
- Ensure logical execution order and correct dependency flow

Behavior Rules:
- Do NOT skip necessary steps
- Do NOT add redundant steps
- Do NOT explain anything outside JSON
- Optimize for minimal steps while preserving correctness
"""


def plan(goal: str, model: str, on_step=None) -> list[Task]:
    task_queue.clear()

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": goal},
        ],
        format="json",
        stream=False,
    )

    content = response["message"]["content"]
    plan_data = json.loads(content)

    id_map: dict[str, str] = {}
    created_tasks: list[Task] = []
    for step in plan_data.get("steps", []):
        planner_deps = step.get("depends_on", [])
        real_deps = [id_map[dep_id] for dep_id in planner_deps if dep_id in id_map]
        task = task_queue.add_task(step["step"], depends_on=real_deps)
        planner_id = step.get("id")
        if planner_id:
            id_map[planner_id] = task.id
        created_tasks.append(task)
        if on_step is not None:
            on_step(step["step"])

    return created_tasks

