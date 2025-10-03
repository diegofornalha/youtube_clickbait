# 🎯 Como Gravar no Neo4j DE VERDADE

## ❌ Problema Atual

```python
# Agents rodam em SUBPROCESS (via ClaudeSDKClient)
async with ClaudeSDKClient() as client:
    # Este processo NÃO tem acesso às MCP tools
    # Porque MCP tools só existem no Claude Code principal
```

**Resultado:** Operações ficam em modo SIMULADO ❌

## ✅ Solução: Orquestrador Grava

### Arquitetura Correta:

```
┌─────────────────────────────────────┐
│   CLAUDE CODE (contexto principal)  │ ← MCP tools disponíveis aqui!
│                                     │
│  ┌──────────────────────────────┐   │
│  │   ORCHESTRATOR               │   │
│  │                              │   │
│  │  1. Despacha tarefa          │   │
│  │  2. Agent executa (subprocess)│  │
│  │  3. Recebe resultado         │   │
│  │  4. GRAVA NO NEO4J ✅        │   │ ← Aqui tem MCP!
│  └──────────────────────────────┘   │
│         │                            │
│         ├──> Agent subprocess 1      │ ← Sem MCP
│         ├──> Agent subprocess 2      │ ← Sem MCP
│         └──> Agent subprocess 3      │ ← Sem MCP
└─────────────────────────────────────┘
```

### Implementação:

```python
# orchestrator.py

async def _execute_task_and_learn(self, task: Task) -> None:
    """Executa tarefa e grava aprendizado."""

    # 1. Executar agent (subprocess)
    result = await self._execute_validator(task.input_data)

    # 2. Extrair operações Neo4j preparadas pelo agent
    # Os agents retornam operações preparadas, não executam

    # 3. GRAVAR DE VERDADE usando MCP tools disponíveis AQUI
    # ESTE código roda no contexto principal!
    if hasattr(result, 'neo4j_operations'):
        for op in result.neo4j_operations:
            # Chamar MCP tool DIRETAMENTE
            # Isso só funciona se este código for executado
            # por um Claude Code agent, não por subprocess
            await self._execute_mcp_operation(op)

async def _execute_mcp_operation(self, op: dict) -> Any:
    \"\"\"
    Executa operação MCP.

    IMPORTANTE: Este método só funciona quando chamado
    de dentro de um Claude Code agent (como EU).
    \"\"\"
    tool_name = op['tool']
    params = op['params']

    # Exemplo para create_memory
    if tool_name == "mcp__neo4j-memory__create_memory":
        # Aqui, SE este código estiver rodando em um Claude Code agent,
        # você poderia usar as MCP tools diretamente
        # Mas em Python puro, não há como
        pass
```

## 🔑 Solução Real: Agent Markdown

**A melhor solução é criar um AGENT de orquestração:**

### `.claude/agents/orchestrator_agent.md`

```markdown
# Orchestrator Agent

Você é responsável por coordenar agents e gravar aprendizados.

## Workflow

1. Receba uma tarefa
2. Invoque idea_validator ou video_title_creator
3. Receba o resultado
4. **GRAVE NO NEO4J** usando ferramentas MCP:
   - mcp__neo4j-memory__create_memory
   - mcp__neo4j-memory__learn_from_result
   - mcp__neo4j-memory__create_connection
5. Retorne resultado final

IMPORTANTE: Você TEM acesso às ferramentas MCP porque é um agent
rodando no contexto do Claude Code principal.
```

### Uso:

```python
# Invocar orchestrator_agent via Task tool
async with ClaudeSDKClient() as client:
    await client.query("""
    Use o orchestrator_agent para processar esta ideia:
    "streaming do claude sdk"

    O agent deve:
    1. Validar com idea_validator
    2. Gerar títulos com video_title_creator
    3. GRAVAR TUDO NO NEO4J
    4. Retornar resumo
    """)
```

## ✅ Resumo

| Método | Grava Neo4j? | Porque |
|--------|-------------|---------|
| Agents Python (subprocess) | ❌ Simulado | Subprocess não tem MCP |
| Orchestrator Python | ❌ Simulado | Código Python puro sem MCP |
| **Claude Code Agent** | ✅ **REAL** | Tem acesso às MCP tools |
| MCP tools diretas (eu) | ✅ **REAL** | Contexto do Claude Code |

## 🎯 Ação Recomendada

Criar `.claude/agents/autonomous_orchestrator.md` que:
- Coordena outros agents
- Grava resultados no Neo4j (tem acesso às MCP tools)
- Funciona 100% autônomo
