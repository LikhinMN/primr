import subprocess
import sys


def ensure_dependencies():
    try:
        import ollama
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "ollama"], check=True)
        import ollama


def register():
    ensure_dependencies()


def unregister():
    pass


if __name__ == "__main__":
    register()
