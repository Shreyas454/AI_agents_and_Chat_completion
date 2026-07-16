from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
import os

WORKSPACE = os.path.join(os.path.dirname(__file__), "workspace")


def read_file(path: str) -> dict:
    """Read the contents of a file in the workspace.
    
    Args:
        path: Relative path to the file within the workspace directory.
    
    Returns:
        A dictionary with:
        - "status": "success" or "error"
        - "content": file contents as a string, if success
        - "message": error message if the file doesn't exist or can't be read
    """
    full_path = os.path.join(WORKSPACE, path)
    if not os.path.isfile(full_path):
        return {
            "status": "error",
            "message": f"File '{path}' not found in workspace."
        }
    
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "status": "success",
            "content": content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not read file: {str(e)}"
        }


def list_files(path: str = ".") -> dict:
    """List files and directories at a given workspace-relative path.
    
    Args:
        path: Relative path within the workspace. Defaults to workspace root.
    
    Returns:
        A dictionary with:
        - "status": "success" or "error"
        - "files": list of filenames (directories end with "/")
        - "message": error message if path is invalid
    """
    full_path = os.path.join(WORKSPACE, path)
    if not os.path.isdir(full_path):
        return {
            "status": "error",
            "message": f"Path '{path}' is not a valid directory in workspace."
        }
    
    files = []
    for entry in os.listdir(full_path):
        entry_path = os.path.join(full_path, entry)
        if os.path.isdir(entry_path):
            files.append(entry + "/")
        else:
            files.append(entry)
    
    return {
        "status": "success",
        "files": files
    }


def edit_file(path: str, old_str: str, new_str: str) -> dict:
    """Edit a file by replacing old_str with new_str.
    
    If the file doesn't exist AND old_str is empty, creates a new file with new_str as content.
    
    Args:
        path: Relative path to the file within the workspace.
        old_str: Text to find and replace. Must match exactly. Empty string means "create file".
        new_str: Text to replace old_str with, or the initial content when creating a new file.
    
    Returns:
        A dictionary with:
        - "status": "success" or "error"
        - "message": what happened (e.g., "File created", "File updated", or an error)
    """
    full_path = os.path.join(WORKSPACE, path)
    
    if not os.path.exists(full_path):
        if old_str == "":
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_str)
            return {
                "status": "success",
                "message": f"File '{path}' created."
            }
        else:
            return {
                "status": "error",
                "message": f"File '{path}' does not exist. Cannot replace text."
            }
    
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    match_count = content.count(old_str)
    if match_count == 0:
        return {
            "status": "error",
            "message": f"'{old_str}' not found in '{path}'. No changes made."
        }
    if match_count > 1:
        return {
            "status": "error",
            "message": f"'{old_str}' appears {match_count} times in '{path}'. Please provide more context to make it unique."
        }
    
    updated_content = content.replace(old_str, new_str)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    return {
        "status": "success",
        "message": f"File '{path}' updated successfully."
    }


root_agent = Agent(
    name="coding_agent",
    model="gemini-flash-latest",
    description="A coding assistant that reads, lists, and edits files in a workspace directory",
    instruction="""You are a helpful coding assistant. You have access to a workspace directory with these tools:

- list_files: explore the workspace to see what files exist
- read_file: view the contents of a specific file
- edit_file: modify existing files or create new ones

Workflow guidelines:
- Before editing a file, always read it first to understand its current content
- When creating a new file, use edit_file with an empty old_str and put the initial content in new_str
- When making changes, be precise about what old_str you're replacing — it must match exactly

If the user asks you to write code, first understand what's in the workspace, then plan your changes, then execute them.""",
    tools=[read_file, list_files, edit_file],
)