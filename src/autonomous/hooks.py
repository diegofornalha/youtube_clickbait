"""Hooks automáticos para aprovação e registro de operações."""

import logging
import sys
from pathlib import Path
from typing import Any

# Adicionar claude-agent-sdk-python ao path
sdk_path = Path(__file__).parent.parent.parent / "claude-agent-sdk-python"
sys.path.insert(0, str(sdk_path))

logger = logging.getLogger("autonomous.hooks")


class AutoApprovalHooks:
    """
    Sistema de hooks para aprovação automática de operações.

    Implementa PreToolUse, PostToolUse e outros hooks para:
    - Auto-aprovar tools seguros
    - Bloquear tools perigosos
    - Registrar operações no Neo4j
    - Validar inputs/outputs
    """

    def __init__(
        self,
        auto_approve_tools: list[str] | None = None,
        block_tools: list[str] | None = None,
        protect_paths: list[str] | None = None,
    ):
        """
        Inicializa hooks de auto-aprovação.

        Args:
            auto_approve_tools: Lista de tools para aprovar automaticamente
            block_tools: Lista de tools para bloquear sempre
            protect_paths: Lista de paths protegidos (não permite Write/Edit)
        """
        self.auto_approve_tools = auto_approve_tools or [
            "Read",
            "Grep",
            "Glob",
            "Bash",  # Apenas comandos seguros
        ]
        self.block_tools = block_tools or []
        self.protect_paths = protect_paths or [
            "/.env",
            "/secrets",
            "/credentials",
            "/.git",
        ]
        self.operation_log: list[dict[str, Any]] = []

    async def pre_tool_use(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: Any,
    ) -> dict[str, Any]:
        """
        Hook executado ANTES de usar uma tool.

        Pode:
        - Aprovar automaticamente (permissionDecision: "allow")
        - Bloquear (permissionDecision: "deny")
        - Pedir confirmação (não retornar permissionDecision)

        Args:
            input_data: Dados da tool (tool_name, tool_input)
            tool_use_id: ID único da tool use
            context: Contexto adicional

        Returns:
            Hook output com decisão de permissão
        """
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        logger.info(f"🔍 PreToolUse: {tool_name}")

        # 1. Bloquear tools perigosas
        if tool_name in self.block_tools:
            logger.warning(f"🚫 BLOQUEADO: {tool_name} (tool bloqueada)")
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Tool '{tool_name}' está bloqueada",
                }
            }

        # 2. Proteger paths sensíveis em Write/Edit
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            file_path = tool_input.get("file_path", "")
            for protected_path in self.protect_paths:
                if protected_path in file_path:
                    logger.warning(
                        f"🚫 BLOQUEADO: {tool_name} em path protegido {file_path}"
                    )
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": f"Path '{file_path}' é protegido",
                        }
                    }

        # 3. Validar comandos Bash perigosos
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            dangerous_patterns = [
                "rm -rf /",
                "dd if=",
                "> /dev/",
                "mkfs",
                "format",
                ":(){:|:&};:",  # Fork bomb
            ]
            for pattern in dangerous_patterns:
                if pattern in command:
                    logger.warning(
                        f"🚫 BLOQUEADO: Bash com comando perigoso: {command[:50]}"
                    )
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": f"Comando perigoso detectado: {pattern}",
                        }
                    }

        # 4. Auto-aprovar tools seguras
        if tool_name in self.auto_approve_tools:
            logger.info(f"✅ AUTO-APROVADO: {tool_name}")
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                }
            }

        # 5. Pedir confirmação para outras tools
        logger.info(f"❓ SOLICITANDO CONFIRMAÇÃO: {tool_name}")
        return {}  # Sem decisão = pedir confirmação ao usuário

    async def post_tool_use(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: Any,
    ) -> dict[str, Any]:
        """
        Hook executado DEPOIS de usar uma tool.

        Usado para:
        - Registrar operação no Neo4j
        - Validar output
        - Coletar métricas
        - Detectar anomalias

        Args:
            input_data: Dados da execução (tool_name, tool_input, result)
            tool_use_id: ID da tool use
            context: Contexto

        Returns:
            Hook output (pode adicionar systemMessage)
        """
        tool_name = input_data.get("tool_name", "")
        result = input_data.get("result", "")
        is_error = input_data.get("is_error", False)

        logger.info(f"📊 PostToolUse: {tool_name} (error={is_error})")

        # Registrar operação
        operation = {
            "tool_name": tool_name,
            "tool_use_id": tool_use_id,
            "is_error": is_error,
            "result_length": len(str(result)),
        }
        self.operation_log.append(operation)

        # TODO: Registrar no Neo4j aqui
        # await self._register_in_neo4j(operation)

        # Detectar anomalias
        if is_error:
            logger.warning(f"⚠️  Erro detectado em {tool_name}")
            # Poderia acionar alert, auto-retry, etc.

        return {}

    async def user_prompt_submit(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: Any,
    ) -> dict[str, Any]:
        """
        Hook executado quando usuário submete um prompt.

        Pode:
        - Filtrar/sanitizar prompt
        - Enriquecer com contexto
        - Detectar intenções maliciosas
        - Adicionar instruções automáticas

        Args:
            input_data: Dados do prompt (user_message)
            tool_use_id: ID
            context: Contexto

        Returns:
            Hook output (pode modificar prompt)
        """
        user_message = input_data.get("user_message", "")

        logger.info(f"📝 UserPromptSubmit: {user_message[:50]}...")

        # Detectar prompts suspeitos
        suspicious_patterns = [
            "ignore previous instructions",
            "disregard all",
            "forget everything",
        ]
        for pattern in suspicious_patterns:
            if pattern.lower() in user_message.lower():
                logger.warning(f"🚨 Prompt suspeito detectado: {pattern}")
                # Poderia bloquear ou modificar

        # Enriquecer com contexto (exemplo)
        # enriched = f"{user_message}\n\nContexto: Use sempre validação de ideias."

        return {}

    async def stop_hook(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: Any,
    ) -> dict[str, Any]:
        """
        Hook executado quando agent vai parar.

        Pode:
        - Decidir se deve continuar ou parar
        - Registrar estatísticas finais
        - Cleanup de recursos

        Args:
            input_data: Motivo do stop
            tool_use_id: ID
            context: Contexto

        Returns:
            Hook output
        """
        stop_reason = input_data.get("stop_reason", "unknown")

        logger.info(f"🛑 Stop: {stop_reason}")

        # Registrar estatísticas
        logger.info(f"📊 Total de operações: {len(self.operation_log)}")

        return {}

    def get_hooks_config(self) -> dict[str, list[dict[str, Any]]]:
        """
        Retorna configuração de hooks para ClaudeAgentOptions.

        Returns:
            Dict com hooks configurados
        """
        from claude_agent_sdk import HookMatcher

        return {
            "PreToolUse": [
                HookMatcher(
                    matcher=None,  # Match todas as tools
                    hooks=[self.pre_tool_use],
                ),
            ],
            "PostToolUse": [
                HookMatcher(
                    matcher=None,
                    hooks=[self.post_tool_use],
                ),
            ],
            "UserPromptSubmit": [
                HookMatcher(
                    matcher=None,
                    hooks=[self.user_prompt_submit],
                ),
            ],
            "Stop": [
                HookMatcher(
                    matcher=None,
                    hooks=[self.stop_hook],
                ),
            ],
        }

    def print_statistics(self) -> None:
        """Imprime estatísticas de operações."""
        print("\n┌─────────────────────────────────────┐")
        print("│  HOOKS STATISTICS                   │")
        print("├─────────────────────────────────────┤")
        print(f"│  Total Operations: {len(self.operation_log)}")

        # Contar por tool
        tool_counts: dict[str, int] = {}
        error_counts: dict[str, int] = {}

        for op in self.operation_log:
            tool = op["tool_name"]
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
            if op.get("is_error"):
                error_counts[tool] = error_counts.get(tool, 0) + 1

        print("│")
        print("│  Operations by Tool:")
        for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
            errors = error_counts.get(tool, 0)
            status = "❌" if errors > 0 else "✅"
            print(f"│  {status} {tool}: {count} ({errors} errors)")

        print("└─────────────────────────────────────┘\n")


# Exemplo de uso
if __name__ == "__main__":
    import anyio

    async def test_hooks():
        hooks = AutoApprovalHooks(
            auto_approve_tools=["Read", "Grep"],
            block_tools=["Write"],
            protect_paths=["/.env"],
        )

        # Testar auto-approval
        result = await hooks.pre_tool_use(
            {"tool_name": "Read", "tool_input": {"file_path": "test.py"}},
            "test-id",
            None,
        )
        print("Auto-approve Read:", result)

        # Testar bloqueio
        result = await hooks.pre_tool_use(
            {"tool_name": "Write", "tool_input": {"file_path": "/.env"}},
            "test-id-2",
            None,
        )
        print("Block Write to .env:", result)

        # Estatísticas
        hooks.print_statistics()

    anyio.run(test_hooks)
