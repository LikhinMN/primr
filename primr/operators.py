import bpy
import threading
from . import agent, state


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

        state.add_message("user", prompt)
        state.set_thinking(True)
        scene.primr_prompt = ""

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
            from . import context as scene_ctx

            max_retries = 3
            attempt = 0
            extra_context = ""
            result = ""

            state.set_thinking(True)
            state.add_message("assistant", "Generating coordinated script...")

            model = scene.primr_model

            while attempt < max_retries:
                attempt += 1

                # Generate full script
                code = generate(prompt, model, extra_context)

                # Validate syntax
                valid, syntax_error = validate(code)
                if not valid:
                    extra_context = f"Previous attempt had syntax error: {syntax_error}"
                    state.add_message("assistant", f"⚠️ Syntax error, retrying... ({attempt}/{max_retries})")
                    continue

                # Show code in chat
                state.add_message("assistant", code, is_code=True)

                # Execute
                result = bpy_executor.execute_code(code)

                if result == "Success":
                    state.add_message("assistant", f"✅ Done in {attempt} attempt(s).")
                    break
                else:
                    scene = scene_ctx.get_scene_context()
                    code = review_and_fix(prompt, code, result, model, scene)
                    extra_context = f"Previous attempt failed with: {result}"
                    state.add_message("assistant", f"⚠️ Attempt {attempt} failed, retrying...")

            else:
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

