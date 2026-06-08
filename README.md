# Primr

**Primr** is an AI-powered Blender add-on that lets you generate and edit 3D scenes using natural language prompts. It works by sending your prompt to an NVIDIA NIM cloud model (like LLaMA 3.1 405B) and executing generated Blender operations directly in your scene.

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

- **Rich Context:** Mentions (@object) pull deep data about the object including materials, modifiers, and bounding boxes.
- **Auto-Correction:** If the generated script fails, Primr's internal Critic agent will automatically read the traceback, fix the script, and try again.
- **Chat Interface:** Review generated scripts directly inside the Blender panel.

## License

GPL-3.0-or-later
