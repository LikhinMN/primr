# AGENTS.md

## Project intent
- `primr` is a Blender 5.1+ add-on that turns natural-language prompts into `bpy` Python operations via a local Ollama model (`README.md`, `primr/blender_manifest.toml`).

## Big-picture architecture
- Add-on bootstrap is in `primr/__init__.py`: `register()` defines `bpy.types.Scene` properties (`primr_prompt`, `primr_result`, `primr_history`, `primr_ollama_url`, `primr_model`, `primr_image_path`, `primr_mention`, `primr_object_picker`, `primr_show_settings`) and registers UI/operators.
- UI lives in `primr/panel.py` (`PRIMR_PT_main`), shown in `VIEW_3D` > sidebar > `Primr` tab.
- Main request flow is `primr/operators.py` (`PRIMR_OT_submit.execute`):
  1) read scene prompt/settings,
  2) push user message to `state` and set thinking flag,
  3) run `agent.ask(...)` in a background thread,
  4) parse code with `executor.extract_code(...)`,
  5) execute with `executor.execute_code(...)`, then append assistant message/result.
- Prompt enrichment is in `primr/agent.py`: `context.get_scene_context(prompt=...)` adds object list and prioritizes `@ObjectName` mentions before sending to Ollama.
- `agent.ask(...)` optionally encodes `scene.primr_image_path` and sends it as an Ollama image attachment when the file exists.
- Code execution is centralized in `primr/executor.py` and uses `exec(code, {"bpy": bpy})` after `bpy.ops.ed.undo_push(...)`.
- Experimental multi-agent scaffolding exists in `primr/agents/` (`planner.py`, `executor.py`, `critic.py`) plus task orchestration in `primr/queue/`, but this path is not wired into `register()`, panel operators, or the `primr.submit` flow.
- `primr/tools/` modules are currently placeholders (empty files) and are not imported by active runtime code.

## Critical workflows
- Build distributable zip: `make zip`.
- Install zip to Blender extensions dir from `makefile` (`~/.config/blender/5.1/extensions/user_default`): `make install`.
- Clean artifact: `make clean`.
- In Blender, open the N-panel -> `Primr`, set `Ollama URL` / `Model`, enter prompt, click `Generate` (`README.md`).

## Project-specific conventions and gotchas
- Operator IDs are stable integration points: `primr.submit` and `primr.clear` (`primr/operators.py`); panel wiring also depends on `primr.toggle_code`, `primr.mention_object`, and `primr.clear_image`.
- Conversation shown in UI comes from in-memory `state.messages` (`primr/state.py`) rendered in `primr/panel.py`; `scene.primr_history` is currently not used by the panel/operator flow.
- `agent.ask(prompt, model, url, image_path)` passes the selected `model` into `ollama.chat(...)`, but `url` is still not used; keep this in mind when changing settings behavior.
- `agent.ask(...)` appends to `conversation_history`, but the actual `ollama.chat(...)` request currently sends only `SYSTEM_PROMPT` + current `user_message`; prior turns are not included.
- `ensure_dependencies()` in `primr/__init__.py` installs `ollama` with pip at add-on register time if missing.
- Model output is expected to be raw Python or fenced ```python blocks; parser strips fences if present (`executor.extract_code`).
- `primr/state.py` is part of the active runtime path (`operators.py` + `panel.py`) for chat messages, code expand/collapse state, and thinking state.
- Success-status mapping is currently inconsistent in `primr/operators.py`: code marks assistant status as `done` only when result equals `"Success"`, but `executor.execute_code(...)` returns `"Code executed successfully."` on success.

## External integrations
- Blender Python API (`bpy`) is used across all runtime paths.
- Ollama Python client (`ollama`) is used in `primr/agent.py` for chat completion.
- Packaging/runtime metadata is split between `pyproject.toml` (Python deps) and `primr/blender_manifest.toml` (Blender add-on metadata).

## When editing
- Preserve `register()`/`unregister()` symmetry for all `bpy.types.Scene` properties and registered classes.
- Keep execution path (`operators -> state + agent/context -> executor`) easy to trace; avoid hidden side effects in UI code.
- If you add new user-visible settings, thread them from scene props -> panel -> operator -> agent/executor explicitly.

