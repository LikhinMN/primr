import bpy
import threading
from . import agent, state
from .logger import logger


class PRIMR_OT_submit(bpy.types.Operator):
    bl_idname = "primr.submit"
    bl_label = "Generate"
    bl_description = "Send prompt to Primr AI agent"

    def execute(self, context):
        prompt = context.scene.primr_prompt
        if not prompt.strip():
            return {"CANCELLED"}

        scene = context.scene
        screen = context.screen

        prefs = context.preferences.addons[__package__].preferences
        model = prefs.primr_model
        api_key = prefs.primr_api_key
        base_url = prefs.primr_base_url.strip().rstrip("/")
        if base_url.endswith("/chat/completions"):
            base_url = base_url[:-17]  # Strip /chat/completions if user accidentally included it

        logger.info(f"Using Base URL: {base_url} | Model: {model}")
        logger.info(f"New user prompt: {prompt}")
        state.add_message("user", prompt)
        state.set_thinking(True)
        scene.primr_prompt = ""

        from . import context as scene_ctx
        try:
            scene_str = scene_ctx.get_scene_context(prompt)
        except Exception as e:
            logger.error(f"Failed to capture scene context: {e}")
            scene_str = "{}"

        def redraw_view3d_areas():
            if not screen:
                return
            for area in screen.areas:
                if area.type == "VIEW_3D":
                    area.tag_redraw()

        def run():
            from .agents.coder import generate
            from .agents.validator import validate
            from .agents.critic import review_and_fix
            from . import executor as bpy_executor

            max_retries = 3
            attempt = 0
            extra_context = ""
            result = ""

            state.set_thinking(True)
            state.add_message("assistant", "Generating coordinated script...")

            if not api_key and "localhost" not in base_url and "127.0.0.1" not in base_url:
                state.add_message("assistant", "⚠️ API Key is required for cloud providers. Please set it in Settings.", status="error")
                state.set_thinking(False)
                return

            chat_history = []
            msgs = state.get_messages()
            user_prompts_seen = 0
            total_user_prompts = sum(1 for m in msgs if m.role == "user")
            for m in msgs:
                if m.role == "user":
                    user_prompts_seen += 1
                    if user_prompts_seen < total_user_prompts:
                        chat_history.append({"role": "user", "content": m.content})
                elif m.role == "assistant" and m.is_code:
                    chat_history.append({"role": "assistant", "content": m.content})

            while attempt < max_retries:
                attempt += 1

                # Generate full script
                try:
                    code = generate(prompt, model, api_key, base_url, extra_context, chat_history, scene_str)
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"API Error during generate: {error_msg}")
                    if "404" in error_msg or "NotFoundError" in error_msg:
                        state.add_message("assistant", f"⚠️ The model '{model}' does not exist at the given API endpoint. Please check your model name and Base URL.", status="error")
                        state.set_thinking(False)
                        return
                    else:
                        state.add_message("assistant", f"⚠️ API Error: {error_msg}", status="error")
                        state.set_thinking(False)
                        return

                # Validate syntax
                valid, syntax_error = validate(code)
                if not valid:
                    logger.warning(f"Syntax error in generated code: {syntax_error}")
                    extra_context = f"Previous attempt had syntax error: {syntax_error}"
                    state.add_message("assistant", f"⚠️ Syntax error, retrying... ({attempt}/{max_retries})")
                    continue

                # Show code in chat
                state.add_message("assistant", code, is_code=True)

                # Execute thread-safely
                result_event = threading.Event()
                exec_result = []
                bpy_executor.code_queue.put((code, exec_result, result_event))
                result_event.wait()
                result = exec_result[0]

                if result.startswith("Success"):
                    logger.info(f"Attempt {attempt} succeeded.")
                    state.add_message("assistant", f"✅ Done in {attempt} attempt(s).")
                    break
                else:
                    logger.warning(f"Attempt {attempt} failed during execution. Invoking critic...")
                    code = review_and_fix(prompt, code, result, model, api_key, base_url, scene_str, chat_history)
                    extra_context = f"Previous attempt failed with: {result}"
                    state.add_message("assistant", f"⚠️ Attempt {attempt} failed, retrying...")

            else:
                logger.error(f"Failed after {max_retries} attempts.")
                state.add_message(
                    "assistant",
                    f"❌ Failed after {max_retries} attempts. Last error: {result}",
                    status="error",
                )

            state.set_thinking(False)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        redraw_view3d_areas()
        return {"FINISHED"}


class PRIMR_OT_toggle_code(bpy.types.Operator):
    bl_idname = "primr.toggle_code"
    bl_label = "Toggle Code"

    msg_index: bpy.props.IntProperty()

    def execute(self, context):
        msgs = state.get_messages()
        if 0 <= self.msg_index < len(msgs):
            msgs[self.msg_index].code_expanded = not msgs[self.msg_index].code_expanded
        return {"FINISHED"}


class PRIMR_OT_clear(bpy.types.Operator):
    bl_idname = "primr.clear"
    bl_label = "Clear History"
    bl_description = "Reset Primr conversation history"

    def execute(self, context):
        agent.reset_history()
        state.clear_messages()
        context.scene.primr_result = "History cleared."
        return {"FINISHED"}


class PRIMR_OT_mention_object(bpy.types.Operator):
    bl_idname = "primr.mention_object"
    bl_label = "@ Mention Object"

    def execute(self, context):
        obj_name = context.scene.primr_object_picker
        if obj_name and obj_name != "NONE":
            context.scene.primr_prompt += f"@{obj_name} "
            context.scene.primr_mention = obj_name
        return {"FINISHED"}


class PRIMR_OT_clear_image(bpy.types.Operator):
    bl_idname = "primr.clear_image"
    bl_label = "Clear Image"

    def execute(self, context):
        context.scene.primr_image_path = ""
        return {"FINISHED"}

