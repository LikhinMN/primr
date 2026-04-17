import bpy
from . import executor, agent, state


class PRIMR_OT_submit(bpy.types.Operator):
    bl_idname = "primr.submit"
    bl_label = "Generate"
    bl_description = "Send prompt to Primr AI agent"

    def execute(self, context):
        prompt = context.scene.primr_prompt
        state.add_message("user", prompt)
        context.scene.primr_prompt = ""
        state.set_thinking(True)
        response = agent.ask(
            prompt,
            model=context.scene.primr_model,
            url=context.scene.primr_ollama_url,
            image_path=context.scene.primr_image_path,
        )
        code = executor.extract_code(response)
        result = executor.execute_code(code)
        state.add_message("assistant", code, is_code=True)
        state.set_thinking(False)
        agent.add_to_prompt(prompt, result)
        context.scene.primr_result = result
        print(f"code: {code}\nresult: {result}")
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

