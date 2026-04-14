# Primr

Prompt it. Build it. In Blender.

Blender 5.1+ | Ollama | GPL-3.0

## What is Primr?

Primr is an AI-powered Blender add-on that lets you generate and edit 3D scenes using natural language prompts. It works by sending your prompt to a local Ollama model and executing generated Blender operations directly in your scene.

## Requirements

- Blender 5.1+
- Ollama installed and running locally
- `gemma3:4b` model pulled (`ollama pull gemma3:4b`)

## Installation

1. Go to [Releases](https://github.com/LikhinMN/primr/releases) and download `primr.zip`.
2. In Blender, go to **Edit -> Preferences -> Add-ons -> Install from Disk**.
3. Select `primr.zip`.
4. Search for **Primr** and enable it.

## Usage

1. Press `N` in the 3D Viewport to open the sidebar.
2. Click the **Primr** tab.
3. Type your instruction and click **Generate**.

Example prompts:

- `add a red sphere at the origin`
- `scale the cube to 2x on the Z axis`
- `delete all objects and add a plane`

## Settings

- **Ollama URL** - default `http://localhost:11434`
- **Model** - default `gemma3:4b`; change to any model you have pulled

## Contributing

PRs are welcome - please open pull requests against the [`develop`](https://github.com/LikhinMN/primr/tree/develop) branch.

## License

GPL-3.0-or-later
