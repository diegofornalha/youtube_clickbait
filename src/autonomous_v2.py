"""Sistema Autônomo V2 - Usa agents de .claude/agents/ via Task tool."""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "claude-agent-sdk-python"))

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    TextBlock,
    ToolUseBlock,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("autonomous_v2")


class AutonomousSystemV2:
    """Sistema autônomo que usa agents de .claude/agents/ via Task tool."""

    def __init__(self):
        # Hooks de auto-aprovação
        self.approved_count = 0
        self.blocked_count = 0

    async def pre_tool_use_hook(self, input_data, tool_use_id, context):
        """Auto-aprova Task tool para invocar subagents."""
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Auto-aprovar Task tool (para subagents)
        if tool_name == "Task":
            subagent_type = tool_input.get("subagent_type", "")
            logger.info(f"✅ Auto-aprovando subagent: {subagent_type}")
            self.approved_count += 1
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                }
            }

        # Auto-aprovar tools seguras
        safe_tools = ["Read", "Grep", "Glob", "mcp__neo4j-memory__search_memories"]
        if tool_name in safe_tools:
            logger.info(f"✅ Auto-aprovando: {tool_name}")
            self.approved_count += 1
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                }
            }

        # Bloquear Write em paths sensíveis
        if tool_name in ["Write", "Edit"]:
            file_path = tool_input.get("file_path", "")
            if "/.env" in file_path or "/secrets" in file_path:
                logger.warning(f"🚫 Bloqueando: {tool_name} em {file_path}")
                self.blocked_count += 1
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "Path protegido",
                    }
                }

        # Pedir confirmação para o resto
        return {}

    async def post_tool_use_hook(self, input_data, tool_use_id, context):
        """Registra operações após execução."""
        tool_name = input_data.get("tool_name", "")
        logger.info(f"📊 Executou: {tool_name}")
        return {}

    async def process_idea(self, ideia: str) -> dict[str, Any]:
        """
        Processa uma ideia usando os agents configurados.

        Workflow:
        1. Invoca idea_validator (via Task tool)
        2. Invoca video_title_creator (via Task tool)
        3. Retorna resultados combinados
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🎯 Processando ideia: '{ideia}'")
        logger.info(f"{'='*70}\n")

        # Configurar opções com hooks
        options = ClaudeAgentOptions(
            allowed_tools=["Task", "Read", "Grep", "mcp__neo4j-memory__search_memories"],
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher=None, hooks=[self.pre_tool_use_hook])
                ],
                "PostToolUse": [
                    HookMatcher(matcher=None, hooks=[self.post_tool_use_hook])
                ],
            },
        )

        full_response = ""
        tool_uses = []

        async with ClaudeSDKClient(options=options) as client:
            # Prompt que invoca os subagents
            prompt = f"""Execute este workflow usando os agents configurados:

1. Use o agent idea_validator para validar: "{ideia}"
2. Aguarde o resultado da validação
3. Use o agent video_title_creator para gerar títulos baseado na validação
4. Retorne um resumo com validação + melhor título gerado

Execute agora e me retorne os resultados.
"""

            await client.query(prompt)

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            full_response += block.text
                            logger.info(f"💬 Claude: {block.text[:100]}...")
                        elif isinstance(block, ToolUseBlock):
                            tool_uses.append(
                                {
                                    "tool": block.name,
                                    "id": block.id,
                                    "input": block.input,
                                }
                            )
                            if block.name == "Task":
                                subagent = block.input.get("subagent_type", "")
                                logger.info(f"🤖 Invocando subagent: {subagent}")

        return {
            "ideia": ideia,
            "response": full_response,
            "tool_uses": tool_uses,
            "approved_count": self.approved_count,
            "blocked_count": self.blocked_count,
        }


async def demo():
    """Demo do sistema V2."""
    print("\n" + "=" * 70)
    print("🤖  SISTEMA AUTÔNOMO V2 - Usando agents de .claude/agents/")
    print("=" * 70 + "\n")

    system = AutonomousSystemV2()

    # Processar ideias
    ideias = [
        "streaming real-time com claude sdk",
        "hooks inteligentes para auto-aprovação",
    ]

    for i, ideia in enumerate(ideias, 1):
        print(f"\n{'─'*70}")
        print(f"Ideia {i}/{len(ideias)}")
        print(f"{'─'*70}\n")

        result = await system.process_idea(ideia)

        print(f"\n📊 Resultado:")
        print(f"  Tools usadas: {len(result['tool_uses'])}")
        print(f"  Auto-aprovações: {result['approved_count']}")
        print(f"  Bloqueios: {result['blocked_count']}")
        print(f"  Resposta: {result['response'][:200]}...")

    print("\n" + "=" * 70)
    print("✅  Demo concluída")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(demo())
