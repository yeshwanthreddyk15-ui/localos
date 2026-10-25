import os
import json
import ollama

# Define local tool schemas that Ollama can call
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List all files and folders in a specified local directory path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to list (e.g., '.' or 'workspace')."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the text contents of a local file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The relative path to the file you want to read."
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a local file. Creates parent directories automatically.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The destination path where the file should be written."
                    },
                    "content": {
                        "type": "string",
                        "description": "The complete text content to write into the file."
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    }
]

def execute_tool(name, tool_input):
    """Executes the local system function requested by the model."""
    try:
        if name == "list_directory":
            path = tool_input.get("path", ".")
            files = os.listdir(path)
            return json.dumps({"files": files})
            
        elif name == "read_file":
            file_path = tool_input.get("file_path")
            with open(file_path, "r", encoding="utf-8") as f:
                return json.dumps({"content": f.read()})
                
        elif name == "write_file":
            file_path = tool_input.get("file_path")
            content = tool_input.get("content")
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return json.dumps({"status": "success", "file_path": file_path})
            
        return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

def run_local_ai_assistant(user_prompt):
    messages = [{"role": "user", "content": user_prompt}]
    
    print(f"\n🚀 Running Local Ollama Assistant for prompt: '{user_prompt}'\n" + "—"*50)
    
    model_name = "llama3.2"
    
    while True:
        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                tools=TOOLS
            )
        except Exception as e:
            print(f"\n❌ Ollama Connection Error: {e}")
            print("Make sure Ollama is running in the background on your machine!")
            break
        
        # Check if the model wants to call a tool
        if not response.get('message', {}).get('tool_calls'):
            print(f"\n🤖 Local AI Final Response:\n{response['message']['content']}")
            break
            
        # Append assistant message to history
        messages.append(response['message'])
        
        # Handle tool calls
        for tool in response['message']['tool_calls']:
            fn_name = tool['function']['name']
            fn_args = tool['function']['arguments']
            print(f"⚙️ [Executing Tool Locally] -> {fn_name}({fn_args})")
            
            result_str = execute_tool(fn_name, fn_args)
            
            # Feed tool output back into message history
            messages.append({
                'role': 'tool',
                'content': result_str,
            })

if __name__ == "__main__":
    sample_prompt = "Scan the workspace directory, summarize what files exist, and save a report into tasks/system_status.md."
    run_local_ai_assistant(sample_prompt)