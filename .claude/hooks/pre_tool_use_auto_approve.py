"""Hook PreToolUse para auto-aprovação de tools seguras."""


async def hook(input_data, tool_use_id, context):
    """
    Auto-aprova tools seguras para permitir operação autônoma.

    Auto-aprova:
    - Task: Para invocar subagents
    - Read, Grep, Glob: Leitura é segura
    - Bash: Apenas comandos seguros (validados)
    - MCP Neo4j: Para aprendizado

    Bloqueia:
    - Write/Edit em paths protegidos (.env, secrets)
    - Comandos Bash perigosos (rm -rf, dd, etc)
    """
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Auto-aprovar Task tool (para subagents)
    if tool_name == "Task":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
            }
        }

    # Auto-aprovar tools de leitura
    if tool_name in ["Read", "Grep", "Glob"]:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
            }
        }

    # Auto-aprovar MCP Neo4j (aprendizado)
    if tool_name.startswith("mcp__neo4j-memory__"):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
            }
        }

    # Validar Bash commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")

        # Comandos perigosos
        dangerous_patterns = [
            "rm -rf /",
            "dd if=",
            "> /dev/",
            "mkfs",
            "format",
            ":(){:|:&};:",
        ]

        for pattern in dangerous_patterns:
            if pattern in command:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Comando perigoso: {pattern}",
                    }
                }

        # Comandos seguros são auto-aprovados
        safe_commands = ["ls", "cat", "grep", "find", "echo", "pwd", "which", "python"]
        if any(cmd in command for cmd in safe_commands):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                }
            }

    # Proteger paths em Write/Edit
    if tool_name in ["Write", "Edit", "MultiEdit"]:
        file_path = tool_input.get("file_path", "")
        protected_paths = ["/.env", "/secrets", "/credentials", "/.git/config"]

        for protected in protected_paths:
            if protected in file_path:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Path protegido: {file_path}",
                    }
                }

    # Para outras tools, pedir confirmação
    return {}
