"""Wrapper para o agent idea_validator com tratamento robusto de erros."""

import json
import sys
from pathlib import Path
from typing import Any

# Adicionar claude-agent-sdk-python ao path
sdk_path = Path(__file__).parent.parent.parent / "claude-agent-sdk-python"
sys.path.insert(0, str(sdk_path))

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
)

# Importar sistema de error handling
sys.path.insert(0, str(Path(__file__).parent.parent))
from error_handler import logger, validation_fallback, with_retry
from neo4j_client import Neo4jClient
from neo4j_executor import executar_operacoes_neo4j


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

    def __repr__(self) -> str:
        return (
            f"ValidationResult(score={self.score}, "
            f"verdict={self.verdict}, "
            f"angle={self.best_angle})"
        )


async def validar_ideia(
    ideia: str,
    cwd: str | None = None,
) -> ValidationResult:
    """Valida uma ideia de vídeo usando o agent idea_validator.

    Args:
        ideia: Ideia bruta do usuário
        cwd: Diretório de trabalho (opcional)

    Returns:
        ValidationResult com score, ângulo, fatores virais, etc.

    Example:
        >>> result = await validar_ideia("streaming do claude sdk")
        >>> print(result.score)  # 8.5
        >>> print(result.best_angle)  # "comparação técnica"
    """
    logger.info(f"🔍 Iniciando validação: {ideia}")

    # Wrapper interno com retry e fallback específico para esta ideia
    @with_retry(
        operation_name=f"validar_ideia:{ideia[:30]}",
        max_retries=3,
        fallback=lambda: validation_fallback(ideia),
    )
    async def _executar_validacao() -> dict[str, Any]:
        # Configurar opções do Claude
        options = ClaudeAgentOptions(
            system_prompt=(
                "Você é um especialista em validar ideias de vídeo sobre Claude SDK para YouTube. "
                "Analise a viralidade, valor técnico, fit de audiência e uniqueness. "
                "Retorne APENAS um JSON válido no formato especificado."
            ),
            cwd=cwd,
        )

        # Prompt para o agente
        prompt = f"""Valide esta ideia de vídeo sobre Claude SDK:

"{ideia}"

Avalie nos seguintes critérios (0-10):
- viral_potential: Título clickbait ético, thumbnail potencial, shareability
- technical_value: Código prático, problema real, accuracy
- audience_fit: Nível adequado, duração, relevância
- production_feasibility: Complexidade, recursos, tempo
- uniqueness: Ângulo original, informação exclusiva

Retorne APENAS este JSON:
{{
  "original_idea": "{ideia}",
  "refined_idea": "versão otimizada da ideia",
  "best_angle": "melhor ângulo para abordar",
  "score": 0.0-10.0,
  "score_breakdown": {{
    "viral_potential": 0.0-10.0,
    "technical_value": 0.0-10.0,
    "audience_fit": 0.0-10.0,
    "production_feasibility": 0.0-10.0,
    "uniqueness": 0.0-10.0
  }},
  "viral_factors": ["fator1", "fator2"],
  "improvements_needed": ["melhoria1", "melhoria2"],
  "estimated_metrics": {{
    "views": "range estimado",
    "ctr": "percentage",
    "retention": "percentage"
  }},
  "recommended_format": "tutorial|comparison|revelation|speedrun",
  "title_suggestions": ["sugestão 1", "sugestão 2", "sugestão 3"],
  "verdict": "APPROVED|NEEDS_WORK|PIVOT_RECOMMENDED",
  "next_steps": ["passo1", "passo2"]
}}

IMPORTANTE: Retorne APENAS o JSON, sem texto antes ou depois.
"""

        # Coletar resposta
        full_response = ""

        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            full_response += block.text

        # Procurar por JSON na resposta
        json_start = full_response.find("{")
        json_end = full_response.rfind("}") + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("Nenhum JSON encontrado na resposta")

        json_str = full_response[json_start:json_end]
        data = json.loads(json_str)

        logger.info(f"✅ Validação concluída com sucesso: score={data.get('score', 'N/A')}")
        return data

    # Executar validação com retry
    result_data = await _executar_validacao()

    # Registrar aprendizado no Neo4j (async, não-bloqueante)
    await _registrar_aprendizado_neo4j(ideia, result_data)

    # Converter para ValidationResult
    return ValidationResult(result_data)


async def _registrar_aprendizado_neo4j(ideia: str, validation_data: dict[str, Any]) -> None:
    """Registra padrões e aprendizados no Neo4j após validação bem-sucedida.

    Registra:
    - Padrão SDK usado (ClaudeSDKClient async context)
    - Conceito demonstrado (validação de ideias)
    - Exemplo de código (este arquivo)
    - Relacionamentos IMPLEMENTS, DEMONSTRATES
    """
    try:
        neo4j = Neo4jClient()

        # 1. Criar/atualizar padrão SDK usado
        pattern_req = neo4j.criar_memoria_pattern(
            pattern_name="ClaudeSDKClient async context validation",
            description="Usar async with ClaudeSDKClient para validar ideias com retry automático",
            code_snippet="""
async with ClaudeSDKClient(options=options) as client:
    await client.query(prompt)
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    full_response += block.text
            """,
            success_rate=0.95
        )

        # 2. Criar conceito demonstrado
        conceito_req = neo4j.criar_memoria_conceito(
            concept_name="Idea Validation with JSON parsing",
            explanation="Validar ideias de vídeo usando Claude SDK e extrair JSON estruturado",
            use_cases=["video ideas", "content validation", "structured output"]
        )

        # 3. Criar exemplo deste código
        exemplo_req = neo4j.criar_memoria_exemplo(
            example_name="validator.py - async idea validation",
            code=open(__file__).read(),
            demonstrates_what="ClaudeSDKClient async validation with error handling",
            complexity="medium"
        )

        # 4. Registrar aprendizado sobre resultado
        score = validation_data.get("score", 0.0)
        aprendizado_req = neo4j.criar_aprendizado(
            task=f"Validar ideia: {ideia[:50]}",
            result=f"Score: {score}, Angle: {validation_data.get('best_angle', 'N/A')}",
            success=score >= 7.0,
            category="idea_validation"
        )

        # Preparar operações para execução externa
        # IMPORTANTE: Agents em subprocess NÃO têm acesso direto ao MCP
        # As operações são retornadas para serem executadas pelo orquestrador
        operations = [pattern_req, conceito_req, exemplo_req, aprendizado_req]

        logger.info(f"📊 {len(operations)} operações Neo4j preparadas (execução externa necessária)")

        # TODO: Criar relacionamentos IMPLEMENTS, DEMONSTRATES
        # Precisa dos IDs retornados para criar as conexões

    except Exception as e:
        logger.warning(f"⚠️  Erro ao registrar no Neo4j (não-bloqueante): {e}")
