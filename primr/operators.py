import bpy
from . import executor, agent, state


class PRIMR_OT_submit(bpy.types.Operator):
    bl_idname = "primr.submit"
    bl_label = "Generate"
    bl_description = "Send prompt to Primr AI agent"

    def execute(self, context):
        prompt = context.scene.primr_prompt
        state.add_message("user", prompt)
        state.set_thinking(True)
        response = agent.ask(prompt, model=context.scene.primr_model, url=context.scene.primr_ollama_url)
        code = executor.extract_code(response)
        result = executor.execute_code(code)
        state.add_message("assistant", code, is_code=True)
        state.set_thinking(False)
        state.add_message("assistant", code, is_code=True)
        agent.add_to_prompt(prompt, result)
        context.scene.primr_result = result
        print(f"code: {code}\nresult: {result}")
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
