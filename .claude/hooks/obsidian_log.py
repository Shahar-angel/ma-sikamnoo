"""PostToolUse hook: append a line to the project's action log in the Obsidian vault."""
import datetime
import json
import os
import sys

VAULT_LOG = r"C:\Users\Shahar Angel\Desktop\vault\מה סיכמנו\יומן פעולות.md"
# Read-only / bookkeeping tools that don't change anything worth logging
SKIP = {"Read", "Glob", "Grep", "ToolSearch", "TodoWrite", "ListAgents", "AskUserQuestion"}


def describe(name, inp):
    if name in ("Write", "Edit", "NotebookEdit"):
        return f"{name}: `{os.path.basename(inp.get('file_path', ''))}`"
    if name in ("Bash", "PowerShell"):
        desc = inp.get("description") or inp.get("command", "")[:120]
        return f"{name}: {desc}"
    if name == "Agent":
        return f"Agent: {inp.get('description', '')}"
    if name == "Artifact":
        return f"Artifact: {inp.get('action', 'publish')} {os.path.basename(inp.get('file_path', '') or '')}"
    if name.startswith("mcp__obsidian__"):
        return f"Obsidian {name.split('__')[-1]}: `{inp.get('path', '')}`"
    return name


def main():
    data = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    name = data.get("tool_name", "")
    inp = data.get("tool_input") or {}
    if name in SKIP or (name.startswith("mcp__obsidian__") and "יומן פעולות" in inp.get("path", "")):
        return
    now = datetime.datetime.now()
    day = f"## {now:%Y-%m-%d}"
    with open(VAULT_LOG, "a+", encoding="utf-8") as f:
        f.seek(0)
        prefix = "" if day in f.read() else f"\n{day}\n"
        f.write(f"{prefix}- {now:%H:%M} · {describe(name, inp)}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never block the agent because of logging
        print(f"obsidian_log: {e}", file=sys.stderr)
