"""Descoberta de novos temas usando conexões do Neo4j."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "claude-agent-sdk-python"))

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, AssistantMessage, TextBlock


async def descobrir_temas_relacionados(tema_base: str):
    """
    Descobre novos temas para vídeos baseado em conexões no Neo4j.

    Como funciona:
    1. Busca memórias relacionadas ao tema base
    2. Analisa conexões entre conceitos
    3. Identifica gaps e oportunidades
    4. Sugere novos temas com potencial viral
    """
    print(f"\n{'='*70}")
    print(f"🔍 Descobrindo temas relacionados a: '{tema_base}'")
    print(f"{'='*70}\n")

    options = ClaudeAgentOptions(
        allowed_tools=[
            "mcp__neo4j-memory__search_memories",
            "mcp__neo4j-memory__get_context_for_task",
            "mcp__neo4j-memory__suggest_best_approach",
        ],
        system_prompt="""Você é um especialista em descobrir temas virais para YouTube.
Use o Neo4j para encontrar conexões inteligentes entre conceitos."""
    )

    async with ClaudeSDKClient(options=options) as client:
        prompt = f"""Analise o conhecimento do Neo4j e descubra novos temas de vídeo:

Tema base: "{tema_base}"

WORKFLOW:
1. Use search_memories para buscar tudo relacionado a "{tema_base}"
2. Analise as memórias encontradas
3. Identifique CONEXÕES interessantes entre conceitos
4. Baseado nas conexões, sugira 5 NOVOS temas de vídeo que:
   - Combinam conceitos do Neo4j de forma original
   - Preenchem gaps de conhecimento
   - Têm potencial viral

Retorne no formato:
```
TEMA 1: [título]
Conexão: [conceito A] + [conceito B]
Por que viral: [razão]
Score viral: X/10

TEMA 2: ...
```

Execute agora.
"""

        await client.query(prompt)

        full_response = ""
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        full_response += block.text
                        print(block.text)

    return full_response


async def demo():
    """Demo de descoberta de temas."""

    temas_base = [
        "hooks do claude sdk",
        "streaming",
        "multi-agents",
    ]

    for tema in temas_base:
        resultado = await descobrir_temas_relacionados(tema)
        print(f"\n{'─'*70}\n")
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(demo())
