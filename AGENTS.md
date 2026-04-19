# AGENTS.md

## Project intent
- `primr` is a Blender 5.1+ add-on that turns natural-language prompts into `bpy` Python operations via a local Ollama model (`README.md`, `primr/blender_manifest.toml`).

## Big-picture architecture
- Add-on bootstrap is in `primr/__init__.py`: `register()` defines `bpy.types.Scene` properties (`primr_prompt`, `primr_history`, `primr_ollama_url`, `primr_model`) and registers UI/operators.
- UI lives in `primr/panel.py` (`PRIMR_PT_main`), shown in `VIEW_3D` > sidebar > `Primr` tab.
- Main request flow is `primr/operators.py` (`PRIMR_OT_submit.execute`):
  1) read scene prompt/settings,
  2) call `agent.ask(...)`,
  3) parse code with `executor.extract_code(...)`,
  4) execute with `executor.execute_code(...)`,
  5) append history and update scene fields.
- Prompt enrichment is in `primr/agent.py`: `context.get_scene_context()` adds object list before sending to Ollama.
- Code execution is centralized in `primr/executor.py` and uses `exec(code, {"bpy": bpy})` after `bpy.ops.ed.undo_push(...)`.

## Critical workflows
- Build distributable zip: `make zip`.
- Install zip to Blender extensions dir from `makefile` (`~/.config/blender/5.1/extensions/user_default`): `make install`.
- Clean artifact: `make clean`.
- In Blender, open the N-panel -> `Primr`, set `Ollama URL` / `Model`, enter prompt, click `Generate` (`README.md`).

## Project-specific conventions and gotchas
- Operator IDs are stable integration points: `primr.submit` and `primr.clear` (`primr/operators.py`).
- Conversation shown in UI is plain text from `agent.prompt_history`, joined by `"\n\n"` into `scene.primr_history`.
- `agent.ask(prompt, model, url)` currently hardcodes `ollama.chat(model="gemma4:e4b", ...)` and does not pass `url`; keep this in mind when changing settings behavior.
- `ensure_dependencies()` in `primr/__init__.py` installs `ollama` with pip at add-on register time if missing.
- Model output is expected to be raw Python or fenced ```python blocks; parser strips fences if present (`executor.extract_code`).
- `primr/state.py` defines a dataclass message store but is not wired into the panel/operator flow yet.

## External integrations
- Blender Python API (`bpy`) is used across all runtime paths.
- Ollama Python client (`ollama`) is used in `primr/agent.py` for chat completion.
- Packaging/runtime metadata is split between `pyproject.toml` (Python deps) and `primr/blender_manifest.toml` (Blender add-on metadata).

## When editing
- Preserve `register()`/`unregister()` symmetry for all `bpy.types.Scene` properties and registered classes.
- Keep execution path (`operators -> agent/context -> executor`) easy to trace; avoid hidden side effects in UI code.
- If you add new user-visible settings, thread them from scene props -> panel -> operator -> agent/executor explicitly.

