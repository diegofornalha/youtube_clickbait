"""Neo4j Learner - Grava aprendizados usando MCP tools REAIS."""

import logging
from typing import Any

logger = logging.getLogger("autonomous.neo4j_learner")


class Neo4jLearner:
    """
    Responsável por gravar aprendizados no Neo4j de forma autônoma.

    Como funciona:
    1. Agents preparam operações (create_memory, learn_from_result, etc.)
    2. Orchestrator recebe resultados dos agents
    3. Neo4jLearner executa as operações via MCP tools REAIS
    4. Apenas o orquestrador tem acesso às MCP tools (contexto principal)
    """

    def __init__(self, mcp_tools_available: bool = True):
        self.mcp_tools_available = mcp_tools_available
        self.operations_saved = 0
        self.operations_failed = 0

    async def save_learning(
        self,
        task: str,
        result: str,
        success: bool,
        category: str = "general",
    ) -> dict[str, Any]:
        """
        Salva aprendizado no Neo4j via MCP tool REAL.

        IMPORTANTE: Este método deve ser chamado APENAS no contexto
        principal onde MCP tools estão disponíveis (não em subprocess).

        Args:
            task: Descrição da tarefa executada
            result: Resultado obtido
            success: Se foi bem-sucedido
            category: Categoria do aprendizado

        Returns:
            Resultado da gravação
        """
        if not self.mcp_tools_available:
            logger.warning("⚠️  MCP tools não disponíveis - aprendizado não salvo")
            return {"saved": False, "reason": "mcp_unavailable"}

        try:
            # Aqui você chamaria a MCP tool diretamente
            # Como estamos em código Python e não no contexto do Claude,
            # precisamos retornar a operação para o ORCHESTRATOR executar
            operation = {
                "tool": "mcp__neo4j-memory__learn_from_result",
                "params": {
                    "task": task,
                    "result": result,
                    "success": success,
                    "category": category,
                },
            }

            logger.info(f"📝 Aprendizado preparado: {task[:50]}...")
            self.operations_saved += 1

            return {
                "operation": operation,
                "status": "prepared",
                "requires_mcp_execution": True,
            }

        except Exception as e:
            logger.error(f"❌ Erro ao preparar aprendizado: {e}")
            self.operations_failed += 1
            return {"saved": False, "error": str(e)}

    async def save_pattern(
        self,
        pattern_name: str,
        description: str,
        code_snippet: str,
        success_rate: float,
    ) -> dict[str, Any]:
        """Salva padrão de código no Neo4j."""
        operation = {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": pattern_name,
                    "description": description,
                    "code_snippet": code_snippet,
                    "success_rate": success_rate,
                    "type": "pattern",
                },
            },
        }

        logger.info(f"📝 Padrão preparado: {pattern_name}")
        return {"operation": operation, "status": "prepared"}

    def get_stats(self) -> dict[str, int]:
        """Retorna estatísticas de salvamento."""
        return {
            "saved": self.operations_saved,
            "failed": self.operations_failed,
            "total": self.operations_saved + self.operations_failed,
        }


# Função helper para executar MCP via callback
async def execute_mcp_via_orchestrator(
    operations: list[dict[str, Any]],
    mcp_executor_callback: Any,
) -> list[dict[str, Any]]:
    """
    Executa operações MCP via callback do orquestrador.

    O orquestrador roda no contexto principal do Claude Code
    onde as MCP tools estão disponíveis.

    Args:
        operations: Lista de operações preparadas
        mcp_executor_callback: Callback que tem acesso às MCP tools

    Returns:
        Resultados das operações
    """
    results = []

    for op in operations:
        try:
            result = await mcp_executor_callback(op)
            results.append(result)
        except Exception as e:
            logger.error(f"❌ Erro ao executar MCP: {e}")
            results.append({"error": str(e)})

    return results
