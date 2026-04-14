import bpy
from . import executor, agent


class PRIMR_OT_submit(bpy.types.Operator):
    bl_idname = "primr.submit"
    bl_label = "Generate"
    bl_description = "Send prompt to Primr AI agent"

    def execute(self, context):
        prompt = context.scene.primr_prompt
        response = agent.ask(prompt, model=context.scene.primr_model, url=context.scene.primr_ollama_url)
        code = executor.extract_code(response)
        result = executor.execute_code(code)
        agent.add_to_prompt(prompt, result)
        context.scene.primr_history = "\n\n".join(agent.prompt_history)
        context.scene.primr_result = result
        print(f"code: {code}\nresult: {result}")
        return {"FINISHED"}


class PRIMR_OT_clear(bpy.types.Operator):
    bl_idname = "primr.clear"
    bl_label = "Clear History"
    bl_description = "Reset Primr conversation history"

    def execute(self, context):
        agent.reset_history()
        context.scene.primr_result = "History cleared."
        return {"FINISHED"}
