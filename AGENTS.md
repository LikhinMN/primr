# AGENTS.md

## Project intent
- `primr` is a Blender 5.1+ add-on that turns natural-language prompts into `bpy` Python operations via NVIDIA NIM cloud API (`README.md`, `primr/blender_manifest.toml`).

## Big-picture architecture
- Add-on bootstrap is in `primr/__init__.py`: `register()` defines `bpy.types.Scene` properties (`primr_prompt`, `primr_result`, `primr_history`, `primr_api_key`, `primr_model`, `primr_image_path`, `primr_mention`, `primr_object_picker`, `primr_show_settings`) and registers UI/operators via a `_classes` tuple for clean register/unregister symmetry.
- UI lives in `primr/panel.py` (`PRIMR_PT_main`), shown in `VIEW_3D` > sidebar > `Primr` tab.
- Main request flow is `primr/operators.py` (`PRIMR_OT_submit.execute`):
  1) read scene prompt/settings,
  2) push user message to `state` and set thinking flag,
  3) spawn a background thread that calls `agents.coder.generate(...)`,
  4) validate syntax with `agents.validator.validate(...)`,
  5) enqueue code for thread-safe main-thread execution via `executor.code_queue`,
  6) on failure, call `agents.critic.review_and_fix(...)` and retry (up to 3 attempts).
- Rich scene context is built by `primr/context.py`: `get_scene_context(prompt=...)` produces JSON with object transforms, materials, mesh stats, modifiers, bounding boxes, collections hierarchy, lights, cameras, and detailed introspection for `@mentioned` objects.
- Code generation uses NVIDIA NIM via the `openai` Python client with `base_url="https://integrate.api.nvidia.com/v1"`.
- Code execution is centralized in `primr/executor.py`: uses `exec(code, {"bpy": bpy, "mathutils": mathutils})` with stdout capture via `redirect_stdout` and undo push. A `code_queue` (queue.Queue) ensures thread-safe execution.
- Thread safety: background threads place `(code, result_list, event)` tuples into `executor.code_queue`. The `primr_execution_timer` in `__init__.py` drains this queue on the main thread at ~10 Hz.
- `primr/agent.py` holds conversation history state and `reset_history()` / `add_to_prompt()` helpers.
- `primr/state.py` manages chat messages, code expand/collapse state, and thinking state for the UI.

## Critical workflows
- Build distributable zip: `make zip`.
- Install zip to Blender extensions dir from `makefile` (`~/.config/blender/5.1/extensions/user_default`): `make install`.
- Clean artifact: `make clean`.
- In Blender, open the N-panel -> `Primr`, set `API Key` / `Model`, enter prompt, click `Generate` (`README.md`).

## Project-specific conventions and gotchas
- Operator IDs are stable integration points: `primr.submit` and `primr.clear` (`primr/operators.py`); panel wiring also depends on `primr.toggle_code`, `primr.mention_object`, and `primr.clear_image`.
- Conversation shown in UI comes from in-memory `state.messages` (`primr/state.py`) rendered in `primr/panel.py`.
- All LLM calls go through NVIDIA NIM (OpenAI-compatible API) — the `api_key` is read from `scene.primr_api_key` and passed through `operators -> coder/critic`.
- `context.get_scene_context()` returns a JSON string (not plain text) with rich scene data. Objects limit is 20 to avoid token bloat.
- `executor.execute_code()` returns strings starting with "Success" on success (may include stdout output) or "Error executing code:" on failure. The operator checks `result.startswith("Success")`.
- `executor.extract_code()` handles both fenced ```python blocks and raw Python output.
- Register/unregister symmetry is maintained via a `_classes` tuple in `__init__.py`.

## External integrations
- Blender Python API (`bpy`, `mathutils`) is used across all runtime paths.
- OpenAI Python client (`openai`) is used in `primr/agents/coder.py` and `primr/agents/critic.py` for NVIDIA NIM chat completion.
- Packaging/runtime metadata is split between `pyproject.toml` (Python deps) and `primr/blender_manifest.toml` (Blender add-on metadata).

## When editing
- Preserve `register()`/`unregister()` symmetry via the `_classes` tuple for all registered classes, and explicit `del` for all `bpy.types.Scene` properties.
- Keep execution path (`operators -> state + coder/critic -> executor`) easy to trace; avoid hidden side effects in UI code.
- If you add new user-visible settings, thread them from scene props -> panel -> operator -> coder/critic explicitly.
- Thread safety is critical: never call `bpy` from a background thread. Always use the `code_queue` pattern.
