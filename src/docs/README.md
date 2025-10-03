# 📚 Claude Agent SDK - Documentação Completa

## Índice Organizado por Clusters

### 🎯 **Iniciantes - Comece Aqui**

1. **[Conceitos Fundamentais](01_CONCEITOS_FUNDAMENTAIS.md)**
   - O que é o Claude Agent SDK?
   - Componentes principais (ClaudeSDKClient, Transport)
   - Tipos de mensagens
   - Ciclo de vida
   - Modo async obrigatório

2. **[ClaudeSDKClient Completo](02_CLAUDESDKCLIENT_COMPLETO.md)**
   - Construtor e inicialização
   - Métodos principais (connect, query, receive_response)
   - Context manager pattern
   - Controles avançados (interrupt, set_model, set_permission_mode)
   - Exemplos práticos

### 🔧 **Intermediário - Customização**

3. **[Sistema de Hooks](03_HOOKS_SISTEMA.md)**
   - O que são hooks?
   - Tipos de hooks (PreToolUse, PostToolUse, etc)
   - Hook callbacks e matchers
   - Exemplos práticos (logging, validação, persistência)
   - Debugging de hooks

4. **[MCP Tools Customizadas](04_MCP_TOOLS_CUSTOMIZADAS.md)**
   - Criar tools in-process com @tool decorator
   - Input schemas (dict, TypedDict, JSON Schema)
   - create_sdk_mcp_server()
   - Acesso ao estado da aplicação
   - SDK MCP vs Servidores externos
   - Exemplos completos (calculator, database, web scraper)

5. **[Permissões e Segurança](05_PERMISSOES_SEGURANCA.md)**
   - Permission modes (default, acceptEdits, bypassPermissions)
   - Sistema can_use_tool (callback programático)
   - PermissionResult (Allow/Deny)
   - PermissionUpdate (atualizar regras)
   - Estratégias de segurança
   - Exemplos avançados (whitelist, rate limiting, trust score)

### 🚀 **Avançado - Best Practices**

6. **[Padrões de Uso](06_PADROES_USO.md)**
   - Padrões fundamentais (context manager, processamento de mensagens)
   - Padrões de conversa (multi-turn, streaming)
   - Padrões de erro (retry, fallback)
   - Padrões de performance (batch, sessões paralelas)
   - Padrões de integração (FastAPI, workers)
   - Anti-padrões (o que evitar)

7. **[Troubleshooting](07_TROUBLESHOOTING.md)**
   - Erros de conexão (CLINotFoundError, timeouts)
   - Erros de runtime (deadlock, JSON parsing)
   - Erros de configuração (tools não chamadas, hooks não executam)
   - Erros de performance (lentidão, memory leak)
   - FAQ e debugging checklist

### 🧠 **Especialista - Conhecimento Profundo**

8. **[SDK Knowledge Graph](SDK_KNOWLEDGE_GRAPH.md)**
   - Modelo de grafo para aprendizado sobre SDK
   - Relacionamentos (IMPLEMENTS, DEMONSTRATES, VALIDATES)
   - Categorias de nós (sdk_pattern, sdk_concept, code_example)
   - Queries úteis
   - Evolução de padrões

9. **[Integração Neo4j](NEO4J_FINAL_ARCHITECTURE.md)**
   - Arquitetura de persistência
   - Como funciona o sistema de aprendizado
   - Operações preparadas vs executadas
   - Persistência via hooks
   - Scripts de sincronização

10. **[Sistema Autônomo](SISTEMA_AUTONOMO_RESUMO.md)**
    - Aprendizado contínuo
    - Auto-discovery de padrões
    - Consolidação de conhecimento
    - Dashboard e analytics

## Mapa de Navegação

```
📚 Documentação
│
├─ 🎯 INICIANTES
│  ├─ 01_CONCEITOS_FUNDAMENTAIS.md ──► Leia primeiro!
│  └─ 02_CLAUDESDKCLIENT_COMPLETO.md ──► API reference
│
├─ 🔧 INTERMEDIÁRIO
│  ├─ 03_HOOKS_SISTEMA.md ──────────► Interceptar execuções
│  ├─ 04_MCP_TOOLS_CUSTOMIZADAS.md ─► Criar ferramentas
│  └─ 05_PERMISSOES_SEGURANCA.md ───► Controle de acesso
│
├─ 🚀 AVANÇADO
│  ├─ 06_PADROES_USO.md ────────────► Best practices
│  └─ 07_TROUBLESHOOTING.md ────────► Resolver problemas
│
└─ 🧠 ESPECIALISTA
   ├─ SDK_KNOWLEDGE_GRAPH.md ──────► Grafo de conhecimento
   ├─ NEO4J_FINAL_ARCHITECTURE.md ─► Persistência
   └─ SISTEMA_AUTONOMO_RESUMO.md ──► Auto-aprendizado
```

## Fluxo de Aprendizado Recomendado

### **Dia 1: Básico**
1. Ler `01_CONCEITOS_FUNDAMENTAIS.md`
2. Ler `02_CLAUDESDKCLIENT_COMPLETO.md`
3. Executar exemplo básico:
```python
import anyio
from claude_agent_sdk import ClaudeSDKClient

async def main():
    async with ClaudeSDKClient() as client:
        await client.query("Olá!")
        async for msg in client.receive_response():
            print(msg)

anyio.run(main)
```

### **Dia 2: Customização**
1. Ler `03_HOOKS_SISTEMA.md`
2. Ler `04_MCP_TOOLS_CUSTOMIZADAS.md`
3. Criar seu primeiro hook
4. Criar sua primeira tool customizada

### **Dia 3: Segurança**
1. Ler `05_PERMISSOES_SEGURANCA.md`
2. Implementar callback de permissão
3. Configurar whitelist/blacklist de tools

### **Dia 4: Produção**
1. Ler `06_PADROES_USO.md`
2. Ler `07_TROUBLESHOOTING.md`
3. Implementar retry, error handling
4. Adicionar logging e metrics

### **Dia 5+: Expertise**
1. Estudar knowledge graph
2. Implementar sistema de aprendizado
3. Contribuir com novos padrões

## Exemplos por Caso de Uso

### **Caso de Uso: Chat Interface**
```
Docs relevantes:
- 02_CLAUDESDKCLIENT_COMPLETO.md (receive_response)
- 06_PADROES_USO.md (Padrão 4: Multi-Turn)
- 03_HOOKS_SISTEMA.md (UserPromptSubmit)
```

### **Caso de Uso: Automação de Tarefas**
```
Docs relevantes:
- 02_CLAUDESDKCLIENT_COMPLETO.md (query)
- 05_PERMISSOES_SEGURANCA.md (bypassPermissions)
- 06_PADROES_USO.md (Padrão 9: Batch Processing)
```

### **Caso de Uso: Validação de Ideias**
```
Docs relevantes:
- 02_CLAUDESDKCLIENT_COMPLETO.md (receive_response)
- 04_MCP_TOOLS_CUSTOMIZADAS.md (tools com validação)
- 06_PADROES_USO.md (Padrão 3: Processar por tipo)
```

### **Caso de Uso: Pipeline de Processamento**
```
Docs relevantes:
- 06_PADROES_USO.md (Padrão 16: Pipeline)
- 03_HOOKS_SISTEMA.md (PostToolUse para persistência)
- NEO4J_FINAL_ARCHITECTURE.md (Aprendizado)
```

## Referência Rápida

### **Imports Essenciais:**

```python
from claude_agent_sdk import (
    # Cliente
    ClaudeSDKClient,
    ClaudeAgentOptions,

    # Mensagens
    AssistantMessage,
    UserMessage,
    ResultMessage,
    SystemMessage,

    # Content Blocks
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,

    # Hooks
    HookMatcher,
    HookContext,

    # Permissões
    PermissionResultAllow,
    PermissionResultDeny,
    PermissionUpdate,

    # MCP Tools
    tool,
    create_sdk_mcp_server,

    # Erros
    CLIConnectionError,
    CLINotFoundError,
)
```

### **Template Base:**

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
)

async def main():
    # Configurar
    options = ClaudeAgentOptions(
        system_prompt="Você é um assistente útil",
        model="claude-sonnet-4-5",
        max_turns=5,
    )

    # Executar
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Sua pergunta aqui")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

            elif isinstance(msg, ResultMessage):
                print(f"Custo: ${msg.total_cost_usd:.4f}")

# Executar
anyio.run(main)
```

## Contribuindo

Encontrou erro na documentação? Quer adicionar exemplo?

1. Abra issue no GitHub
2. Sugira melhorias
3. Compartilhe seus padrões descobertos

## Próximos Passos

Depois de dominar a documentação:

- [ ] Explore os exemplos em `/claude-agent-sdk-python/exemplos/`
- [ ] Leia o código fonte em `/claude-agent-sdk-python/claude_agent_sdk/`
- [ ] Implemente seu primeiro agent customizado
- [ ] Compartilhe seus aprendizados (contribua com padrões)

---

**Versão da Documentação:** 1.0.0
**Última Atualização:** 2025-10-03
**Compatível com:** claude-agent-sdk ^0.1.0
