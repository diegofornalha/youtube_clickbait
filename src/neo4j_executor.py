"""Executor real de operações Neo4j via MCP tools."""

import json
import sys
from pathlib import Path
from typing import Any
import asyncio

# Importar biblioteca MCP para conexão direta
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️  Biblioteca MCP não disponível - usando modo simulado")


class Neo4jMCPExecutor:
    """Executa operações Neo4j usando ferramentas MCP reais.

    Este executor pega as operações preparadas pelo Neo4jClient
    e executa chamadas reais às ferramentas MCP do servidor neo4j-memory.
    """

    def __init__(self, mcp_server_path: str | None = None, enable_real_persistence: bool = False):
        """Inicializa executor com client configurado para MCP.

        Args:
            mcp_server_path: Caminho para o servidor MCP neo4j-memory.
                           Se None, usa o padrão ~/.claude/mcp-neo4j-py
            enable_real_persistence: Se True, tenta conectar ao MCP real.
                                    Se False (padrão), usa modo simulado.
        """
        self.operations_log: list[dict[str, Any]] = []
        self.mcp_available = MCP_AVAILABLE and enable_real_persistence
        self.enable_real_persistence = enable_real_persistence

        # Configurar caminho do servidor MCP
        if mcp_server_path is None:
            home = Path.home()
            self.mcp_server_path = home / ".claude" / "mcp-neo4j-py"
        else:
            self.mcp_server_path = Path(mcp_server_path)

        self._session = None
        self._stdio_context = None

        if not enable_real_persistence:
            print("  ℹ️  Neo4j em modo simulado (use enable_real_persistence=True para persistir)")

    async def _conectar_mcp(self):
        """Conecta ao servidor MCP neo4j-memory com timeout."""
        if not self.mcp_available:
            return None

        if self._session is not None:
            return self._session

        try:
            # Timeout de 5 segundos para conexão
            return await asyncio.wait_for(self._conectar_mcp_interno(), timeout=5.0)
        except asyncio.TimeoutError:
            print(f"⚠️  Timeout ao conectar ao MCP (5s)")
            return None
        except Exception as e:
            print(f"⚠️  Erro ao conectar ao MCP: {e}")
            return None

    async def _conectar_mcp_interno(self):
        """Lógica interna de conexão."""
        try:
            # Verificar se o servidor existe (múltiplos caminhos possíveis)
            possible_paths = [
                self.mcp_server_path / "mcp-neo4j" / "servers" / "mcp-neo4j-memory" / "src" / "mcp_neo4j_memory" / "server.py",
                self.mcp_server_path / "src" / "mcp_neo4j_memory" / "server.py",
                self.mcp_server_path / "src" / "mcp_neo4j" / "server.py",
            ]

            server_script = None
            for path in possible_paths:
                if path.exists():
                    server_script = path
                    break

            if server_script is None:
                print(f"⚠️  Servidor MCP não encontrado em nenhum caminho conhecido")
                return None

            # Configurar parâmetros do servidor
            server_params = StdioServerParameters(
                command="python",
                args=[str(server_script)],
                env=None
            )

            # Conectar via stdio (usa context manager)
            # Nota: guarda o context manager para não fechar a conexão
            self._stdio_context = stdio_client(server_params)
            read, write = await self._stdio_context.__aenter__()

            self._session = ClientSession(read, write)
            await self._session.initialize()

            print(f"✅ Conectado ao servidor MCP neo4j-memory")
            return self._session

        except Exception as e:
            print(f"⚠️  Erro ao conectar ao MCP: {e}")
            return None

    async def executar_operacao(self, operation: dict[str, Any]) -> dict[str, Any]:
        """Executa uma operação Neo4j via MCP.

        Tenta executar via conexão real ao MCP server.
        Se falhar, usa modo simulado.

        Args:
            operation: Dict com 'tool' e 'params' do Neo4jClient

        Returns:
            Resultado da operação (node_id real ou simulado)
        """
        import uuid

        tool_name = operation.get("tool")
        params = operation.get("params", {})

        # Extrair nome da ferramenta (sem prefixo mcp__)
        tool_short_name = tool_name.replace("mcp__neo4j-memory__", "")

        try:
            # Tentar execução real via MCP
            session = await self._conectar_mcp()

            if session is not None:
                # Executar ferramenta MCP real
                result = await session.call_tool(tool_short_name, params)

                # Log da operação
                self.operations_log.append({
                    "tool": tool_name,
                    "params": params,
                    "result": result.content,
                    "success": True,
                    "mode": "real"
                })

                print(f"  ✅ {tool_name} → REAL")

                # Extrair resultado
                if result.content:
                    return {"node_id": result.content[0].text if result.content else "created", "mode": "real"}
                return {"success": True, "mode": "real"}

        except Exception as e:
            print(f"  ⚠️  MCP falhou ({e}), usando modo simulado")

        # Fallback: modo simulado
        simulated_id = f"sim_{uuid.uuid4().hex[:8]}"

        result = {
            "node_id": simulated_id,
            "simulated": True,
            "tool": tool_name,
            "status": "logged"
        }

        if "learn_from_result" in tool_name:
            result = {
                "learning_saved": True,
                "simulated": True,
                "tool": tool_name
            }

        # Log da operação
        self.operations_log.append({
            "tool": tool_name,
            "params": params,
            "result": result,
            "success": True,
            "mode": "simulated"
        })

        print(f"  📝 {tool_name} → {simulated_id}")

        return result

    async def close(self):
        """Fecha conexão com o servidor MCP."""
        if self._stdio_context is not None:
            try:
                await self._stdio_context.__aexit__(None, None, None)
            except:
                pass
            self._stdio_context = None

        if self._session is not None:
            self._session = None

    def _criar_prompt_mcp(self, tool_name: str, params: dict[str, Any]) -> str:
        """Cria prompt que aciona a ferramenta MCP correta."""

        if tool_name == "mcp__neo4j-memory__create_memory":
            return f"""
Use a ferramenta mcp__neo4j-memory__create_memory para criar esta memória:

Label: {params['label']}
Properties: {json.dumps(params['properties'], indent=2)}

Retorne o ID do nó criado em formato JSON:
{{"node_id": "id_aqui"}}
"""

        elif tool_name == "mcp__neo4j-memory__create_connection":
            return f"""
Use a ferramenta mcp__neo4j-memory__create_connection para criar esta conexão:

From: {params['from_memory_id']}
To: {params['to_memory_id']}
Type: {params['connection_type']}
Properties: {json.dumps(params.get('properties', {}), indent=2)}

Retorne confirmação em JSON:
{{"connection_created": true, "type": "{params['connection_type']}"}}
"""

        elif tool_name == "mcp__neo4j-memory__learn_from_result":
            return f"""
Use a ferramenta mcp__neo4j-memory__learn_from_result para registrar este aprendizado:

Task: {params['task']}
Result: {params['result']}
Success: {params['success']}
Category: {params.get('category', 'general')}

Retorne confirmação em JSON:
{{"learning_saved": true}}
"""

        else:
            return f"""
Use a ferramenta {tool_name} com estes parâmetros:
{json.dumps(params, indent=2)}

Retorne o resultado em JSON.
"""

    def _extrair_resultado(self, response: str) -> dict[str, Any]:
        """Extrai resultado JSON da resposta do Claude."""
        try:
            # Tentar encontrar JSON na resposta
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)

            # Se não encontrou JSON, retornar resposta como texto
            return {"raw_response": response}

        except json.JSONDecodeError:
            return {"raw_response": response}

    async def executar_batch(
        self, operations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Executa múltiplas operações em sequência.

        Args:
            operations: Lista de operações preparadas pelo Neo4jClient

        Returns:
            Lista de resultados
        """
        results = []
        try:
            for op in operations:
                result = await self.executar_operacao(op)
                results.append(result)
        finally:
            await self.close()

        return results

    def get_operation_log(self) -> list[dict[str, Any]]:
        """Retorna log de todas as operações executadas."""
        return self.operations_log

    def clear_log(self) -> None:
        """Limpa o log de operações."""
        self.operations_log = []


# Função helper para uso direto
async def executar_operacoes_neo4j(
    operations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Helper para executar operações Neo4j de forma simples.

    Args:
        operations: Lista de operações do Neo4jClient

    Returns:
        Lista de resultados das operações MCP

    Example:
        >>> from neo4j_client import Neo4jClient
        >>> from neo4j_executor import executar_operacoes_neo4j
        >>>
        >>> neo4j = Neo4jClient()
        >>> ops = [
        ...     neo4j.criar_memoria_pattern(
        ...         pattern_name="Test Pattern",
        ...         description="Test",
        ...         success_rate=0.9
        ...     )
        ... ]
        >>>
        >>> results = await executar_operacoes_neo4j(ops)
        >>> print(results[0]['node_id'])
    """
    executor = Neo4jMCPExecutor()
    return await executor.executar_batch(operations)
