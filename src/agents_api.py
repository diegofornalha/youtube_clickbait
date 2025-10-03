"""API simplificada para invocar agents de .claude/agents/ via Claude SDK."""

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "claude-agent-sdk-python"))

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    TextBlock,
)


class ValidationResult:
    """Resultado da validação de uma ideia."""

    def __init__(self, data: dict[str, Any]):
        self.original_idea: str = data.get("original_idea", "")
        self.refined_idea: str = data.get("refined_idea", "")
        self.best_angle: str = data.get("best_angle", "")
        self.score: float = data.get("score", 0.0)
        self.score_breakdown: dict[str, float] = data.get("score_breakdown", {})
        self.viral_factors: list[str] = data.get("viral_factors", [])
        self.improvements_needed: list[str] = data.get("improvements_needed", [])
        self.estimated_metrics: dict[str, str] = data.get("estimated_metrics", {})
        self.recommended_format: str = data.get("recommended_format", "")
        self.title_suggestions: list[str] = data.get("title_suggestions", [])
        self.verdict: str = data.get("verdict", "")
        self.next_steps: list[str] = data.get("next_steps", [])


class VideoTitle:
    """Representa um título de vídeo gerado."""

    def __init__(self, data: dict[str, Any]):
        self.titulo: str = data.get("titulo", "")
        self.ctr_score: float = data.get("ctr_score", 0.0)
        self.gatilho: str = data.get("gatilho", "")
        self.formula: str = data.get("formula", "")
        self.emoji: str = data.get("emoji", "")


class TitleCreationResult:
    """Resultado da geração de títulos."""

    def __init__(self, data: dict[str, Any]):
        self.ideia_original: str = data.get("ideia_original", "")
        self.titulos_virais: list[VideoTitle] = [
            VideoTitle(t) for t in data.get("titulos_virais", [])
        ]
        self.recomendado: str = data.get("recomendado", "")
        self.thumbnail_hint: str = data.get("thumbnail_hint", "")

    def get_best_title(self) -> VideoTitle | None:
        """Retorna o título com maior CTR score."""
        if not self.titulos_virais:
            return None
        return max(self.titulos_virais, key=lambda t: t.ctr_score)


async def _invoke_agent_with_hooks(
    agent_name: str,
    prompt: str,
) -> str:
    """Invoca agent de .claude/agents/ com hooks de auto-approval."""

    # Hook de auto-approval
    async def auto_approve_hook(input_data, tool_use_id, context):
        tool_name = input_data.get("tool_name", "")
        # Auto-aprovar Task tool (para subagents)
        if tool_name == "Task":
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                }
            }
        # Auto-aprovar MCP Neo4j
        if tool_name.startswith("mcp__neo4j-memory__"):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                }
            }
        return {}

    options = ClaudeAgentOptions(
        allowed_tools=["Task", "Read", "Grep", "mcp__neo4j-memory__search_memories"],
        hooks={
            "PreToolUse": [HookMatcher(matcher=None, hooks=[auto_approve_hook])]
        },
    )

    full_response = ""

    async with ClaudeSDKClient(options=options) as client:
        # Invocar agent via Task tool
        agent_prompt = f"Use o agent {agent_name} para: {prompt}"
        await client.query(agent_prompt)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        full_response += block.text

    return full_response


async def validar_ideia(ideia: str, cwd: str | None = None) -> ValidationResult:
    """
    Valida uma ideia usando agent idea_validator de .claude/agents/

    Args:
        ideia: Ideia bruta do usuário
        cwd: Diretório de trabalho (não usado, mantido por compatibilidade)

    Returns:
        ValidationResult com score, ângulo, fatores virais
    """
    response = await _invoke_agent_with_hooks(
        agent_name="idea_validator",
        prompt=f'"{ideia}"',
    )

    # Extrair JSON da resposta
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            return ValidationResult(data)

    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback
    return ValidationResult(
        {
            "original_idea": ideia,
            "score": 6.0,
            "verdict": "NEEDS_WORK",
            "best_angle": "desconhecido",
        }
    )


async def gerar_titulos(
    ideia: str,
    validacao: dict[str, Any] | None = None,
    cwd: str | None = None,
) -> TitleCreationResult:
    """
    Gera títulos usando agent video_title_creator de .claude/agents/

    Args:
        ideia: Ideia bruta
        validacao: Resultado da validação (opcional)
        cwd: Diretório de trabalho (não usado)

    Returns:
        TitleCreationResult com títulos ranqueados
    """
    validation_context = ""
    if validacao:
        validation_context = f"""
Validação prévia:
- Score: {validacao.get('score', 'N/A')}
- Ângulo: {validacao.get('best_angle', 'N/A')}
"""

    prompt = f'"{ideia}"\n{validation_context}'

    response = await _invoke_agent_with_hooks(
        agent_name="video_title_creator",
        prompt=prompt,
    )

    # Extrair JSON
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            return TitleCreationResult(data)

    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback
    return TitleCreationResult(
        {
            "ideia_original": ideia,
            "titulos_virais": [
                {
                    "titulo": f"🚀 Claude SDK: {ideia.capitalize()}",
                    "ctr_score": 7.0,
                    "formula": "Básica",
                    "gatilho": "Curiosidade",
                    "emoji": "🚀",
                }
            ],
            "recomendado": f"🚀 Claude SDK: {ideia.capitalize()}",
            "thumbnail_hint": "Logo Claude SDK + código",
        }
    )


# Alias para compatibilidade
gerar_titulos_com_neo4j = gerar_titulos

# Exportar tudo
__all__ = [
    "ValidationResult",
    "VideoTitle",
    "TitleCreationResult",
    "validar_ideia",
    "gerar_titulos",
    "gerar_titulos_com_neo4j",
]
