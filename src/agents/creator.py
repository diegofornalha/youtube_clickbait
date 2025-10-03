"""Wrapper para o agent video_title_creator."""

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

# Importar Neo4j client para aprendizado
sys.path.insert(0, str(Path(__file__).parent.parent))
from neo4j_client import Neo4jClient
from neo4j_executor import executar_operacoes_neo4j


class VideoTitle:
    """Representa um título de vídeo gerado."""

    def __init__(self, data: dict[str, Any]):
        self.titulo: str = data.get("titulo", "")
        self.ctr_score: float = data.get("ctr_score", 0.0)
        self.gatilho: str = data.get("gatilho", "")
        self.formula: str = data.get("formula", "")
        self.emoji: str = data.get("emoji", "")

    def __repr__(self) -> str:
        return f"VideoTitle(titulo='{self.titulo}', ctr={self.ctr_score})"


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

    def __repr__(self) -> str:
        return (
            f"TitleCreationResult("
            f"titulos={len(self.titulos_virais)}, "
            f"recomendado='{self.recomendado}')"
        )


async def gerar_titulos(
    ideia: str,
    validacao: dict[str, Any] | None = None,
    cwd: str | None = None,
) -> TitleCreationResult:
    """Gera títulos virais usando o agent video_title_creator.

    Args:
        ideia: Ideia bruta do usuário
        validacao: Resultado da validação (opcional, mas recomendado)
        cwd: Diretório de trabalho (opcional)

    Returns:
        TitleCreationResult com lista de títulos ranqueados

    Example:
        >>> from agents.validator import validar_ideia
        >>> validacao = await validar_ideia("streaming do claude")
        >>> result = await gerar_titulos("streaming do claude", validacao.__dict__)
        >>> print(result.recomendado)
    """
    # Configurar opções do Claude
    options = ClaudeAgentOptions(
        system_prompt=(
            "Você é um especialista em criar títulos virais para YouTube sobre Claude SDK. "
            "Use fórmulas comprovadas de alto CTR e gatilhos psicológicos. "
            "Retorne APENAS um JSON válido no formato especificado."
        ),
        cwd=cwd,
    )

    # Criar cliente Claude SDK
    client = ClaudeSDKClient(options=options)

    # Construir prompt
    validation_context = ""
    if validacao:
        validation_context = f"""
Validação da ideia:
- Score: {validacao.get('score', 'N/A')}
- Ângulo: {validacao.get('best_angle', 'N/A')}
- Fatores virais: {', '.join(validacao.get('viral_factors', []))}
- Formato recomendado: {validacao.get('recommended_format', 'N/A')}
"""

    prompt = f"""Gere títulos virais para esta ideia sobre Claude SDK:

"{ideia}"

{validation_context}

FÓRMULAS DE TÍTULOS VIRAIS:
1. Choque + Número: "🚨 [NÚMERO] [COISA] que [AÇÃO SURPREENDENTE]"
2. Comparação Brutal: "[A] vs [B]: [RESULTADO CHOCANTE]"
3. Segredo Revelado: "O Segredo do [TÓPICO] que [AUTORIDADE] esconde"
4. Transformação Rápida: "Como [RESULTADO] em apenas [TEMPO] com [FERRAMENTA]"
5. Contradição: "Por que [COISA POPULAR] está ERRADO sobre [TÓPICO]"

GATILHOS PSICOLÓGICOS: FOMO, Curiosidade, Autoridade, Prova Social, Exclusividade, Urgência

REGRAS:
- CAPITALIZAR palavras-chave (CLAUDE, RÁPIDO, SEGREDO)
- Usar 1 emoji no máximo (🚨 ⚡ 🔥 💰)
- 40-70 caracteres
- Número ímpar quando usar números (3, 5, 7, 9)
- Sempre incluir "Claude" ou "Claude SDK"

Gere 5-10 títulos diferentes e retorne APENAS este JSON:
{{
  "ideia_original": "{ideia}",
  "titulos_virais": [
    {{
      "titulo": "Título completo aqui",
      "ctr_score": 9.5,
      "gatilho": "FOMO + Curiosidade",
      "formula": "Fórmula 1: Choque + Número",
      "emoji": "🚨"
    }}
  ],
  "recomendado": "Título com maior CTR score",
  "thumbnail_hint": "Sugestão visual rápida"
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

    # Tentar extrair JSON da resposta
    try:
        # Procurar por JSON na resposta
        json_start = full_response.find("{")
        json_end = full_response.rfind("}") + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("Nenhum JSON encontrado na resposta")

        json_str = full_response[json_start:json_end]
        data = json.loads(json_str)

        result = TitleCreationResult(data)

        # Registrar aprendizado sobre títulos gerados
        await _registrar_titulos_neo4j(ideia, result)

        return result

    except (json.JSONDecodeError, ValueError) as e:
        # Fallback: criar resultado básico
        fallback_title = {
            "titulo": f"Claude SDK: {ideia.capitalize()}",
            "ctr_score": 7.0,
            "gatilho": "Curiosidade",
            "formula": "Fórmula básica",
            "emoji": "🚀",
        }

        return TitleCreationResult(
            {
                "ideia_original": ideia,
                "titulos_virais": [fallback_title],
                "recomendado": fallback_title["titulo"],
                "thumbnail_hint": f"Erro ao gerar títulos: {e}",
            }
        )


async def gerar_titulos_com_neo4j(
    ideia: str,
    validacao: dict[str, Any] | None = None,
    neo4j_context: dict[str, Any] | None = None,
    cwd: str | None = None,
) -> TitleCreationResult:
    """Gera títulos virais incluindo contexto do Neo4j.

    Esta é a versão completa que inclui consulta ao Neo4j ANTES de gerar.

    Args:
        ideia: Ideia bruta do usuário
        validacao: Resultado da validação
        neo4j_context: Contexto recuperado do Neo4j
        cwd: Diretório de trabalho

    Returns:
        TitleCreationResult com títulos otimizados pelo contexto
    """
    # Construir contexto Neo4j se disponível
    neo4j_info = ""
    if neo4j_context:
        neo4j_info = f"""
Contexto do Neo4j:
- Memórias relacionadas: {neo4j_context.get('related_memories', 'Nenhuma')}
- Aprendizados anteriores: {neo4j_context.get('learnings', 'Nenhum')}
- Melhores práticas: {neo4j_context.get('best_practices', 'N/A')}
"""

    # Configurar opções do Claude
    options = ClaudeAgentOptions(
        system_prompt=(
            "Você é um especialista em criar títulos virais para YouTube sobre Claude SDK. "
            "Use fórmulas comprovadas, gatilhos psicológicos e aprendizados anteriores. "
            "Retorne APENAS um JSON válido."
        ),
        cwd=cwd,
    )

    # Criar cliente Claude SDK
    client = ClaudeSDKClient(options=options)

    # Construir prompt completo
    validation_context = ""
    if validacao:
        validation_context = f"""
Validação:
- Score: {validacao.get('score', 'N/A')}
- Ângulo: {validacao.get('best_angle', 'N/A')}
- Fatores: {', '.join(validacao.get('viral_factors', []))}
"""

    prompt = f"""Gere títulos virais para esta ideia sobre Claude SDK:

Ideia: "{ideia}"

{validation_context}
{neo4j_info}

FÓRMULAS DE TÍTULOS VIRAIS:
1. Choque + Número: "🚨 [NÚMERO] [COISA] que [AÇÃO SURPREENDENTE]"
2. Comparação Brutal: "[A] vs [B]: [RESULTADO CHOCANTE]"
3. Segredo Revelado: "O Segredo do [TÓPICO] que [AUTORIDADE] esconde"
4. Transformação Rápida: "Como [RESULTADO] em apenas [TEMPO] com [FERRAMENTA]"
5. Contradição: "Por que [COISA POPULAR] está ERRADO sobre [TÓPICO]"

GATILHOS: FOMO, Curiosidade, Autoridade, Prova Social, Exclusividade, Urgência

REGRAS:
- CAPITALIZAR palavras-chave
- 1 emoji no máximo (🚨 ⚡ 🔥 💰)
- 40-70 caracteres
- Sempre incluir "Claude" ou "Claude SDK"

Gere 5-10 títulos e retorne APENAS este JSON:
{{
  "ideia_original": "{ideia}",
  "titulos_virais": [
    {{
      "titulo": "Título completo",
      "ctr_score": 9.5,
      "gatilho": "FOMO + Curiosidade",
      "formula": "Fórmula 1",
      "emoji": "🚨"
    }}
  ],
  "recomendado": "Título com maior CTR",
  "thumbnail_hint": "Sugestão visual"
}}

IMPORTANTE: Retorne APENAS o JSON, sem texto adicional.
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

    # Parse JSON
    try:
        json_start = full_response.find("{")
        json_end = full_response.rfind("}") + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("Nenhum JSON encontrado")

        json_str = full_response[json_start:json_end]
        data = json.loads(json_str)

        result = TitleCreationResult(data)

        # Registrar aprendizado sobre títulos gerados
        await _registrar_titulos_neo4j(ideia, result)

        return result

    except (json.JSONDecodeError, ValueError) as e:
        # Fallback
        fallback = {
            "titulo": f"🚀 Claude SDK: {ideia.capitalize()}",
            "ctr_score": 7.0,
            "gatilho": "Curiosidade",
            "formula": "Básica",
            "emoji": "🚀",
        }

        return TitleCreationResult(
            {
                "ideia_original": ideia,
                "titulos_virais": [fallback],
                "recomendado": fallback["titulo"],
                "thumbnail_hint": f"Erro: {e}",
            }
        )


async def _registrar_titulos_neo4j(ideia: str, result: TitleCreationResult) -> None:
    """Registra padrões de títulos virais e fórmulas no Neo4j.

    Registra:
    - Fórmulas de títulos usadas
    - Gatilhos psicológicos aplicados
    - Títulos gerados com CTR scores
    - Relacionamentos entre títulos, fórmulas e gatilhos
    """
    try:
        neo4j = Neo4jClient()

        # Pegar melhor título
        best_title = result.get_best_title()
        if not best_title:
            return

        # 1. Registrar fórmula usada (se diferente de fallback)
        if best_title.formula and best_title.formula != "Fórmula básica":
            formula_req = neo4j.criar_memoria_pattern(
                pattern_name=f"Title Formula: {best_title.formula}",
                description=f"Fórmula de título viral: {best_title.formula}",
                code_snippet=best_title.titulo,
                success_rate=best_title.ctr_score / 10.0  # Normalizar 0-1
            )

        # 2. Registrar gatilhos psicológicos
        gatilhos = best_title.gatilho.split("+") if "+" in best_title.gatilho else [best_title.gatilho]
        for gatilho in gatilhos:
            gatilho = gatilho.strip()
            if gatilho and gatilho != "Curiosidade":  # Evitar gatilho genérico
                gatilho_req = neo4j.criar_memoria_conceito(
                    concept_name=f"Psychological Trigger: {gatilho}",
                    explanation=f"Gatilho psicológico usado em títulos virais: {gatilho}",
                    use_cases=["title creation", "clickbait", "engagement"]
                )

        # 3. Registrar exemplo de título gerado
        exemplo_req = neo4j.criar_memoria_exemplo(
            example_name=f"Title: {best_title.titulo[:50]}",
            code=f"""
# Ideia: {ideia}
# Título: {best_title.titulo}
# CTR Score: {best_title.ctr_score}/10
# Fórmula: {best_title.formula}
# Gatilhos: {best_title.gatilho}
            """,
            demonstrates_what=f"Title creation using {best_title.formula}",
            complexity="easy"
        )

        # 4. Registrar aprendizado
        aprendizado_req = neo4j.criar_aprendizado(
            task=f"Gerar título para: {ideia[:50]}",
            result=f"CTR {best_title.ctr_score}/10, Formula: {best_title.formula}",
            success=best_title.ctr_score >= 8.0,
            category="title_generation"
        )

        # Preparar operações para execução externa
        # IMPORTANTE: Agents em subprocess NÃO têm acesso direto ao MCP
        operations = [exemplo_req, aprendizado_req]

        print(f"📊 {len(operations)} operações Neo4j preparadas (execução externa necessária)")

        # TODO: Registrar fórmulas e gatilhos como nós separados
        # TODO: Criar relacionamentos USED_FORMULA, USED_TRIGGER

    except Exception as e:
        print(f"⚠️  Erro ao registrar títulos no Neo4j (não-bloqueante): {e}")
