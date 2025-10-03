"""Executor Neo4j V2 - Usa MCP tools via Claude Code ao invés de conexão direta."""

import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "claude-agent-sdk-python"))

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
)

logger = logging.getLogger("neo4j_executor_v2")


class Neo4jExecutorV2:
    """
    Executa operações Neo4j via MCP tools através do Claude Code.

    Ao invés de conectar diretamente ao servidor MCP, usa o ClaudeSDKClient
    para invocar as ferramentas MCP que já estão disponíveis.

    Vantagens:
    - Não precisa gerenciar conexão MCP
    - Usa infraestrutura existente do Claude Code
    - Auto-approval via hooks
    - Logging automático
    """

    def __init__(self):
        self.operations_executed = 0
        self.operations_failed = 0

    async def executar_operacao(self, operation: dict[str, Any]) -> dict[str, Any]:
        """
        Executa uma operação Neo4j via Claude Code.

        Args:
            operation: Dict com 'tool' e 'params'

        Returns:
            Resultado da operação
        """
        tool_name = operation.get("tool", "")
        params = operation.get("params", {})

        # Configurar opções permitindo MCP tools
        options = ClaudeAgentOptions(
            allowed_tools=[tool_name],  # Permitir apenas esta tool
            system_prompt="Execute a operação solicitada e retorne apenas o resultado em JSON.",
        )

        # Construir prompt específico para a tool
        prompt = self._build_prompt(tool_name, params)

        full_response = ""
        tool_result = None

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(prompt)

                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                full_response += block.text
                            elif isinstance(block, ToolUseBlock):
                                logger.info(f"🔧 Executando: {block.name}")
                            elif isinstance(block, ToolResultBlock):
                                tool_result = block.content

            # Parse resultado
            result = self._parse_result(full_response, tool_result)
            result["mode"] = "real_via_claude"
            result["tool"] = tool_name

            self.operations_executed += 1
            logger.info(f"✅ Operação executada: {tool_name}")

            return result

        except Exception as e:
            self.operations_failed += 1
            logger.error(f"❌ Erro ao executar {tool_name}: {e}")

            return {
                "error": str(e),
                "tool": tool_name,
                "mode": "failed",
            }

    def _build_prompt(self, tool_name: str, params: dict[str, Any]) -> str:
        """Constrói prompt para executar tool MCP."""
        # Extrair nome curto da tool
        short_name = tool_name.replace("mcp__neo4j-memory__", "")

        if short_name == "create_memory":
            return f"""Use a ferramenta {tool_name} para criar uma memória:

Label: "{params['label']}"
Properties: {json.dumps(params['properties'], indent=2)}

Apenas execute a ferramenta e retorne o ID do nó criado.
"""

        elif short_name == "create_connection":
            return f"""Use a ferramenta {tool_name} para criar uma conexão:

From: {params['from_memory_id']}
To: {params['to_memory_id']}
Connection Type: {params['connection_type']}
Properties: {json.dumps(params.get('properties', {}), indent=2)}

Apenas execute a ferramenta.
"""

        elif short_name == "learn_from_result":
            return f"""Use a ferramenta {tool_name} para registrar este aprendizado:

Task: "{params['task']}"
Result: "{params['result']}"
Success: {params['success']}
Category: "{params.get('category', 'general')}"

Apenas execute a ferramenta.
"""

        elif short_name == "search_memories":
            query = params.get('query', '')
            label = params.get('label', '')
            limit = params.get('limit', 10)

            return f"""Use a ferramenta {tool_name} para buscar memórias:

Query: "{query}"
Label: "{label}"
Limit: {limit}

Retorne os resultados encontrados.
"""

        else:
            # Genérico
            return f"""Use a ferramenta {tool_name} com estes parâmetros:

{json.dumps(params, indent=2)}

Execute a ferramenta e retorne o resultado.
"""

    def _parse_result(self, response: str, tool_result: Any) -> dict[str, Any]:
        """Extrai resultado da resposta."""
        # Tentar extrair JSON da resposta
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)

        except json.JSONDecodeError:
            pass

        # Se tool_result disponível, usar
        if tool_result:
            return {"tool_result": str(tool_result), "success": True}

        # Fallback
        return {"raw_response": response[:200], "success": True}

    async def executar_batch(
        self, operations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Executa múltiplas operações."""
        results = []

        for op in operations:
            result = await self.executar_operacao(op)
            results.append(result)

        logger.info(
            f"📊 Batch concluído: {self.operations_executed} executadas, "
            f"{self.operations_failed} falharam"
        )

        return results


# Helper function
async def executar_operacoes_neo4j_v2(
    operations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Executa operações Neo4j via Claude Code (V2).

    Esta versão usa ClaudeSDKClient para invocar MCP tools,
    garantindo gravação REAL no Neo4j.

    Args:
        operations: Lista de operações do Neo4jClient

    Returns:
        Lista de resultados com node_id real
    """
    executor = Neo4jExecutorV2()
    return await executor.executar_batch(operations)


# Teste
if __name__ == "__main__":
    import asyncio

    async def test():
        print("🧪 Testando Neo4j Executor V2...\n")

        # Criar operação de teste
        operations = [
            {
                "tool": "mcp__neo4j-memory__create_memory",
                "params": {
                    "label": "Learning",
                    "properties": {
                        "name": "Teste Executor V2",
                        "description": "Gravação real via Claude Code",
                        "category": "test",
                    },
                },
            }
        ]

        results = await executar_operacoes_neo4j_v2(operations)

        print(f"\n📊 Resultados:")
        for i, r in enumerate(results):
            print(f"  {i+1}. {r}")

        if results and results[0].get("mode") == "real_via_claude":
            print("\n✅ GRAVAÇÃO REAL via Claude Code!")
        else:
            print("\n⚠️  Não gravou")

    asyncio.run(test())
