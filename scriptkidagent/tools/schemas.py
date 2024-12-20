schema_execute_in_msfconsole = {
    "name": "execute_in_msfconsole",
    "description": "Executes a command in msfconsole.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command to execute in msfconsole."
            }
        },
        "required": ["command"]
    }
}

schema_success_exploited ={
    "name": "success_exploited",
    "description": "Generates a final exploit report. Only call this function when the exploitation is successful, otherwise do not call this function.",
    "parameters": {
        "type": "object",
        "properties": {
            "capabilities": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of capabilities provided by the vulnerability (e.g., file read/write, shell access)."
            },
            "if_shell": {
                "type": "boolean",
                "description": "Whether a shell was obtained."
            },
            "if_root": {
                "type": "boolean",
                "description": "Whether root privileges were obtained."
            }
        },
        "required": ["capabilities", "if_shell", "if_root"]
    }
}

schema_execute_in_bash = {
    "name": "execute_in_bash",
    "description": "Executes a command in the Bash shell.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The Bash command to execute."
            }
        },
        "required": ["command"]
    }
}
