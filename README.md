# Primr

**Primr** is an AI-powered Blender add-on that lets you generate and edit 3D scenes using natural language prompts. It features a multi-agent architecture (Coder, Critic, Validator) powered by an NVIDIA NIM cloud model. By leveraging a built-in macro **Skill Library** and **Chain-of-Thought** reasoning, Primr reliably builds complex, production-ready 3D setups on the fly.
## Prerequisites

- Blender 5.1 or later
- An NVIDIA API Key (get one from [NVIDIA NIM](https://build.nvidia.com/))

## Installation

1. Download the latest release `.zip` from the Releases page.
2. Open Blender.
3. Go to **Edit > Preferences > Add-ons**.
4. Click **Install from Disk...** and select the `.zip` file.
5. Enable the add-on by checking the box next to **Primr**.

## Usage

1. Open the 3D Viewport in Blender.
2. Press `N` to open the sidebar and navigate to the **Primr** tab.
3. Click the **Settings** dropdown and enter your NVIDIA API Key.
4. Type your prompt in the text box (e.g., "Create a 3-point lighting setup", "Add a red cube on top of a blue cylinder").
5. Click **Generate**.
6. The add-on will think, generate a Python script, and execute it in your scene.

## Features

- **Multi-Agent Architecture:** A Coder agent writes the initial script, a Validator checks for syntax errors, and a Critic agent automatically catches execution tracebacks to rewrite and fix failing scripts.
- **Skill Library:** Primr includes a massive internal macro library allowing the AI to instantly apply complex setups without writing boilerplate nodes:
  - `skills.modeling`: Hard-surface non-destructive modifiers (Bevel + Subdiv) and Boolean cuts.
  - `skills.physics`: 1-click Rigid Body dynamics and Cloth simulations.
  - `skills.materials`: Procedural Glass, Metal, and Emission PBR shaders.
  - `skills.camera & environment`: Cinematic camera tracking rigs, turntable animations, and curved studio backdrops.
  - `skills.wireframe`: Converts 2D orthographic images/drawings into 3D meshes using OpenCV contour extraction.
- **Chain-of-Thought Reasoning:** Powered by a strict XML prompt architecture, the AI is forced to mathematically plan its 3D operations inside `<thinking>` tags before writing Python, drastically reducing spatial hallucinations.
- **Rich Scene Context:** Primr explicitly feeds the AI your active objects, collections, and precise physical `dimensions` (in meters) so the AI understands true scene scale. Use `@object_name` in your prompt for deep introspection.
- **Chat Interface & Logs:** Review generated scripts directly inside the Blender N-Panel, toggle expanded code blocks, and read detailed logs written to the user's extension directory.

## License

GPL-3.0-or-later
