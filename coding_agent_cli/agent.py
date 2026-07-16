from dotenv import load_dotenv
load_dotenv()

import os
import json
from groq import Groq

# ============================================
# CONFIGURATION
# ============================================

WORKSPACE = os.path.join(os.path.dirname(__file__), "workspaces", "default")

# Ensure default workspace exists
os.makedirs(WORKSPACE, exist_ok=True)

MODEL = "llama-3.3-70b-versatile"

MAX_SEARCH_RESULTS = 50

client = Groq()


# ============================================
# TOOLS
# ============================================

def read_file(path: str) -> dict:
    """Read the contents of a file in the workspace."""
    full_path = os.path.join(WORKSPACE, path)
    if not os.path.isfile(full_path):
        return {"status": "error", "message": f"File '{path}' not found in workspace."}

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": f"Could not read file: {str(e)}"}


def list_files(path: str = ".") -> dict:
    """List files and directories at a workspace-relative path."""
    full_path = os.path.join(WORKSPACE, path)
    if not os.path.isdir(full_path):
        return {"status": "error", "message": f"Path '{path}' is not a valid directory."}

    files = []
    for entry in os.listdir(full_path):
        entry_path = os.path.join(full_path, entry)
        if os.path.isdir(entry_path):
            files.append(entry + "/")
        else:
            files.append(entry)

    return {"status": "success", "files": files}


def edit_file(path: str, old_str: str, new_str: str) -> dict:
    """Edit a file by replacing old_str with new_str. Creates new file if old_str is empty."""
    full_path = os.path.join(WORKSPACE, path)

    if not os.path.exists(full_path):
        if old_str == "":
            os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_str)
            return {"status": "success", "message": f"File '{path}' created."}
        else:
            return {"status": "error", "message": f"File '{path}' does not exist."}

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    match_count = content.count(old_str)
    if match_count == 0:
        return {"status": "error", "message": f"'{old_str}' not found in '{path}'."}
    if match_count > 1:
        return {"status": "error", "message": f"'{old_str}' appears {match_count} times in '{path}'. Provide more context to make it unique."}

    updated_content = content.replace(old_str, new_str)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    return {"status": "success", "message": f"File '{path}' updated."}


def search_in_files(pattern: str, path: str = ".") -> dict:
    """Search for a text pattern across all files in a directory (like grep)."""
    full_path = os.path.join(WORKSPACE, path)
    if not os.path.isdir(full_path):
        return {"status": "error", "message": f"Path '{path}' is not a valid directory."}

    matches = []
    truncated = False

    for root, dirs, files in os.walk(full_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, WORKSPACE)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_number, line in enumerate(f, start=1):
                        if pattern in line:
                            matches.append({
                                "file": relative_path,
                                "line_number": line_number,
                                "line": line.rstrip("\n")
                            })
                            if len(matches) >= MAX_SEARCH_RESULTS:
                                truncated = True
                                break
            except Exception:
                # Skip unreadable files (binary, permission issues, etc.)
                continue

            if truncated:
                break
        if truncated:
            break

    result = {
        "status": "success",
        "matches": matches
    }
    if truncated:
        result["message"] = f"Results truncated to first {MAX_SEARCH_RESULTS} matches."
    if not matches:
        result["message"] = f"No matches found for '{pattern}' in '{path}'."

    return result


# Map function names to actual functions (for tool call dispatch)
AVAILABLE_TOOLS = {
    "read_file": read_file,
    "list_files": list_files,
    "edit_file": edit_file,
    "search_in_files": search_in_files,
}

# ============================================
# TOOL SCHEMAS (what we tell the LLM about the tools)
# ============================================

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file in the workspace. Use this to see what's inside a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file within the workspace directory."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given workspace-relative path. Defaults to workspace root if no path given.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path within the workspace. Defaults to '.' (workspace root)."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file by replacing old_str with new_str. If the file doesn't exist AND old_str is empty, creates a new file with new_str as content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file within the workspace."
                    },
                    "old_str": {
                        "type": "string",
                        "description": "Text to find and replace. Must match exactly. Empty string means 'create new file'."
                    },
                    "new_str": {
                        "type": "string",
                        "description": "Text to replace old_str with, or the initial content when creating a new file."
                    }
                },
                "required": ["path", "old_str", "new_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_files",
            "description": "Search for a text pattern across all files in a directory, like grep. Returns each matching line with its file and line number. Use this to find where something is defined or used without reading every file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The text to search for (case-sensitive substring match)."
                    },
                    "path": {
                        "type": "string",
                        "description": "Relative directory path within the workspace to search in. Defaults to '.' (workspace root)."
                    }
                },
                "required": ["pattern"]
            }
        }
    }
]

# ============================================
# AGENT LOOP
# ============================================

SYSTEM_PROMPT = """You are a helpful coding assistant. You have access to a workspace directory with these tools:

- list_files: explore the workspace to see what files exist
- read_file: view the contents of a specific file
- edit_file: modify existing files or create new ones
- search_in_files: search for a text pattern across all files (like grep) to find where something is defined or used

Workflow guidelines:
- Before editing a file, always read it first to understand its current content
- When creating a new file, use edit_file with an empty old_str and put the initial content in new_str
- When making changes, be precise about what old_str you're replacing — it must match exactly
- Use search_in_files when you need to locate where a function, variable, or text appears across the workspace instead of reading every file
- If the user asks you to write code, first understand what's in the workspace, then plan your changes, then execute them"""


MAX_ITERATIONS = 15


def run_agent(user_message: str, conversation_history: list) -> tuple[str, list]:
    """Run the agent loop for one user turn.

    Args:
        user_message: what the user just typed
        conversation_history: list of previous messages (grows over time)

    Returns:
        (assistant_response, updated_conversation_history)
    """
    # Add user's new message to history
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    iterations = 0

    while iterations < MAX_ITERATIONS:
        iterations += 1

        # Send full history + tools to LLM
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            temperature=0
        )

        choice = response.choices[0]

        # Case 1: LLM wants to call tools
        if choice.finish_reason == "tool_calls":
            # Add the LLM's tool call request to history
            # Extract only the fields Groq accepts as input
            msg_dict = {
                "role": choice.message.role,
                "content": choice.message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in choice.message.tool_calls
                ]
            }
            conversation_history.append(msg_dict)

            # Execute each tool call
            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                print(f"\n  [Tool] {fn_name}({fn_args})")

                if fn_name in AVAILABLE_TOOLS:
                    result = AVAILABLE_TOOLS[fn_name](**fn_args)
                else:
                    result = {"status": "error", "message": f"Unknown tool: {fn_name}"}

                print(f"  [Result] {result}")

                # Feed tool result back to LLM
                conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            # Loop back — LLM will see tool result and decide what next
            continue

        # Case 2: LLM gave a final answer
        else:
            assistant_message = choice.message.content
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            return assistant_message, conversation_history

    # Hit max iterations
    return "[Max iterations reached — stopping to prevent infinite loop]", conversation_history