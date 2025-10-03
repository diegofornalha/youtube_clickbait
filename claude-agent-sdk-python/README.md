# Claude Agent SDK para Python

SDK Python oficial para interagir com Claude Code de forma programática. Construa agentes, automatize workflows e crie aplicações inteligentes com Claude.

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Instalação

```bash
pip install claude-agent-sdk
```

**Pré-requisitos:**
- Python 3.10+
- Node.js
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`

## 📖 Índice

- [Início Rápido](#-início-rápido)
- [ClaudeSDKClient: Conversas Multi-Turno](#-claudesdkclient-conversas-multi-turno)
- [Configuração via ClaudeAgentOptions](#-configuração-via-claudeagentoptions)
- [Ferramentas Customizadas (MCP In-Process)](#-ferramentas-customizadas-mcp-in-process)
- [Hooks: Controle de Permissões](#-hooks-controle-de-permissões)
- [Tratamento de Erros](#-tratamento-de-erros)
- [Limitações Importantes](#-limitações-importantes)
- [Exemplos Avançados](#-exemplos-avançados)

## ⚡ Início Rápido

```python
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="Quanto é 2 + 2?"):
        print(message)

anyio.run(main)
```

## 🔄 ClaudeSDKClient: Conversas Multi-Turno

**`ClaudeSDKClient`** permite conversas **stateful** onde Claude lembra o contexto anterior:

### 🎯 Quando Usar?

| Use `ClaudeSDKClient` | Use `query()` |
|----------------------|---------------|
| ✅ Debugging iterativo | ✅ Perguntas isoladas |
| ✅ Refinamento de código | ✅ Validações rápidas |
| ✅ Chat interfaces | ✅ Scripts batch |
| ✅ Colaboração contextual | ✅ Automação simples |

### 💡 Exemplo: Multi-Turno

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def conversa_contextual():
    options = ClaudeAgentOptions(
        system_prompt="Você é um assistente de matemática conciso"
    )

    async with ClaudeSDKClient(options=options) as client:
        # Turno 1
        await client.query("Quanto é 10 + 5?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")  # "15"

        # Turno 2 - Claude LEMBRA que o resultado era 15
        await client.query("Multiplique esse resultado por 2")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")  # "30"

        # Turno 3 - Continua lembrando tudo
        await client.query("Divida por 3")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")  # "10"
```

**🧠 Como funciona:** Cada turno recebe **todo o histórico anterior** como contexto, permitindo colaboração iterativa.

## ⚙️ Configuração via ClaudeAgentOptions

**⚠️ IMPORTANTE:** `ClaudeSDKClient` **NÃO** aceita parâmetros diretos. Todas as configurações devem ser passadas via `ClaudeAgentOptions`:

### ✅ Correto:
```python
options = ClaudeAgentOptions(
    system_prompt="Você é um especialista em Python",
    allowed_tools=["Read", "Write", "Bash"],
    cwd="/path/to/project",
)

client = ClaudeSDKClient(options=options)
```

### ❌ Errado:
```python
# ERRO: system_prompt não é parâmetro direto!
client = ClaudeSDKClient(system_prompt="...")
```

### 📋 Parâmetros Principais

```python
ClaudeAgentOptions(
    # System prompt
    system_prompt="Sua instrução customizada",

    # Tools permitidas
    allowed_tools=["Read", "Write", "Bash", "Grep"],
    disallowed_tools=["WebSearch"],  # Bloquear específicas

    # Diretório de trabalho
    cwd="/caminho/para/projeto",

    # Limite de turnos (None = sem limite)
    max_turns=None,  # Conversação livre
    # max_turns=5,   # Máximo 5 turnos

    # Modo de permissões
    permission_mode="default",  # "acceptEdits", "plan", "bypassPermissions"

    # Modelo
    model="claude-sonnet-4-5-20250929",

    # Hooks customizados
    hooks={...},

    # Servidores MCP
    mcp_servers={...},
)
```

### 🎛️ max_turns: Controle de Conversação

```python
# ♾️ SEM LIMITE (padrão) - Conversação livre
ClaudeAgentOptions()  # max_turns=None

# 🔢 COM LIMITE - Controle de custo/contexto
ClaudeAgentOptions(max_turns=5)  # Máximo 5 turnos
```

**Por que limitar?**
- 💰 **Custo**: Cada turno consome tokens (histórico cresce)
- 🧹 **Contexto**: Evitar "poluição" de histórico muito longo
- ⚡ **Performance**: Sessões muito longas ficam lentas

## 🛠️ Ferramentas Customizadas (MCP In-Process)

Crie ferramentas Python que Claude pode usar, sem gerenciar subprocessos externos:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeSDKClient, ClaudeAgentOptions

# Definir ferramenta com decorator
@tool("greet", "Cumprimentar usuário", {"name": str})
async def greet_user(args):
    return {
        "content": [
            {"type": "text", "text": f"Olá, {args['name']}!"}
        ]
    }

# Criar servidor MCP in-process
server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user]
)

# Usar com Claude
options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet"]
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Cumprimente Alice")
    async for msg in client.receive_response():
        print(msg)
```

**✨ Benefícios:**
- ✅ Sem gerenciamento de subprocessos
- ✅ Melhor performance (sem overhead IPC)
- ✅ Deploy mais simples (processo único)
- ✅ Debug mais fácil (tudo no mesmo processo)
- ✅ Type safety com Python

## 🔐 Hooks: Controle de Permissões

**Hooks** são funções Python que controlam o comportamento do Claude Code em pontos específicos:

```python
from claude_agent_sdk import HookMatcher

async def auto_approve_safe_tools(input_data, tool_use_id, context):
    """Auto-aprova tools seguras."""
    tool_name = input_data.get("tool_name", "")

    # Auto-aprovar tools de leitura
    if tool_name in ["Read", "Grep", "Glob"]:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }

    # Bloquear Write em paths sensíveis
    if tool_name == "Write":
        file_path = input_data.get("tool_input", {}).get("file_path", "")
        if "/.env" in file_path:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Path protegido"
                }
            }

    return {}  # Pedir confirmação

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Bash"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher=None, hooks=[auto_approve_safe_tools])
        ]
    }
)
```

**Hooks disponíveis:**
- `PreToolUse`: Antes de executar tool (aprovar/bloquear)
- `PostToolUse`: Depois de executar (validar/registrar)
- `UserPromptSubmit`: Quando usuário envia prompt (filtrar/enriquecer)
- `Stop`: Quando agent vai parar (cleanup/decidir continuar)

## 🛡️ Tratamento de Erros

```python
from claude_agent_sdk import (
    ClaudeSDKError,      # Erro base
    CLINotFoundError,    # Claude Code não instalado
    CLIConnectionError,  # Problemas de conexão
    ProcessError,        # Processo falhou
    CLIJSONDecodeError,  # Parsing JSON falhou
)

# Exemplo com retry automático
import asyncio

async def query_with_retry(prompt: str, max_retries: int = 3):
    """Query com retry automático e backoff exponencial."""
    for attempt in range(max_retries):
        try:
            async for message in query(prompt=prompt):
                return message

        except CLIConnectionError as e:
            if attempt == max_retries - 1:
                raise
            delay = 2 ** attempt  # Backoff: 1s, 2s, 4s
            print(f"⚠️  Retry {attempt + 1}/{max_retries} após {delay}s")
            await asyncio.sleep(delay)

        except CLINotFoundError:
            print("❌ Claude Code não instalado!")
            print("Instale: npm install -g @anthropic-ai/claude-code")
            raise
```

## ⚠️ Limitações Importantes

### 1. **MCP Tools em Subprocess**

**❌ Problema:**
```python
# ClaudeSDKClient cria subprocess
# Subprocess NÃO herda MCP tools do contexto pai
async with ClaudeSDKClient() as client:
    # Este client NÃO tem acesso a mcp__neo4j-memory__* tools
    # Mesmo que estejam disponíveis no Claude Code principal
```

**✅ Solução:**
```python
# Use agents em .claude/agents/ que rodam no contexto principal
# Esses agents TÊM acesso às MCP tools
```

### 2. **Contexto Async**

**❌ Limitação:**
```python
# NÃO pode reutilizar client entre contextos async diferentes
client = ClaudeSDKClient()

async def task1():
    await client.connect()  # ❌ Não funciona

async def task2():
    await client.query()  # ❌ Cliente já está em outro contexto
```

**✅ Solução:**
```python
# Criar nova instância para cada contexto
async def task1():
    async with ClaudeSDKClient() as client1:
        await client1.query("...")

async def task2():
    async with ClaudeSDKClient() as client2:
        await client2.query("...")
```

### 3. **Configuração Explícita (v0.1.0+)**

**⚠️ Breaking Change:** A partir da v0.1.0, configurações **NÃO** são carregadas automaticamente:

```python
# ❌ v0.0.x (antigo): carregava CLAUDE.md automaticamente
options = ClaudeAgentOptions()

# ✅ v0.1.0+ (novo): precisa especificar explicitamente
options = ClaudeAgentOptions(
    setting_sources=["user", "project", "local"]  # Carregar CLAUDE.md
)
```

## 💡 Exemplos Avançados

### Sistema Autônomo com Agents + Hooks

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher

# 1. Definir hooks de auto-aprovação
async def auto_approve_hook(input_data, tool_use_id, context):
    tool_name = input_data.get("tool_name", "")

    # Auto-aprovar Task tool (para invocar subagents)
    if tool_name == "Task":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }

    # Auto-aprovar tools seguras
    if tool_name in ["Read", "Grep", "Glob"]:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }

    return {}  # Pedir confirmação para outras

# 2. Configurar sistema
options = ClaudeAgentOptions(
    allowed_tools=["Task", "Read", "Grep", "Glob"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher=None, hooks=[auto_approve_hook])
        ]
    }
)

# 3. Usar agents de .claude/agents/
async with ClaudeSDKClient(options=options) as client:
    # Claude invoca agents automaticamente se existirem em .claude/agents/
    await client.query("""
    Use o agent idea_validator para validar esta ideia:
    "sistema autônomo com claude sdk"
    """)

    async for msg in client.receive_response():
        print(msg)
```

### Retry Automático com Backoff Exponencial

```python
import asyncio
from functools import wraps

def with_retry(max_retries: int = 3):
    """Decorator para retry automático."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except CLIConnectionError as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = 2 ** attempt  # Backoff exponencial
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

@with_retry(max_retries=3)
async def validar_ideia(ideia: str):
    """Valida ideia com retry automático."""
    options = ClaudeAgentOptions(
        system_prompt="Você é um validador de ideias"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(f"Valide: {ideia}")
        async for msg in client.receive_response():
            # Processar resposta
            pass
```

### Workflow Multi-Agent

```python
async def workflow_completo(ideia: str):
    """Pipeline com múltiplos agents."""
    options = ClaudeAgentOptions(
        allowed_tools=["Task", "Read", "Grep"],
    )

    async with ClaudeSDKClient(options=options) as client:
        # Step 1: Validação
        await client.query(f"Use idea_validator para validar: '{ideia}'")
        validacao = ""
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        validacao += block.text

        # Step 2: Geração (na mesma sessão - lembra validação)
        await client.query(f"Use video_title_creator para gerar títulos")
        titulos = ""
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        titulos += block.text

        return {"validacao": validacao, "titulos": titulos}
```

## 📊 Tipos

```python
from claude_agent_sdk import (
    # Opções
    ClaudeAgentOptions,

    # Mensagens
    AssistantMessage,
    UserMessage,
    SystemMessage,
    ResultMessage,

    # Blocos de conteúdo
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,

    # Hooks
    HookMatcher,

    # Erros
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError,
)
```

## 🎓 Padrões Recomendados

### ✅ Separação de Responsabilidades

```python
# ClaudeAgentOptions: APENAS configuração
options = ClaudeAgentOptions(
    system_prompt="...",
    cwd="/path",
)

# ClaudeSDKClient: APENAS gerenciamento de sessão
client = ClaudeSDKClient(options=options)
```

### ✅ Context Manager Sempre

```python
# ✅ BOM: Garante cleanup correto
async with ClaudeSDKClient(options=options) as client:
    await client.query("...")

# ❌ EVITAR: Pode deixar processos órfãos
client = ClaudeSDKClient(options=options)
await client.connect()
# Esquecer de disconnect()
```

### ✅ Parse de Mensagens Robusto

```python
async for message in client.receive_response():
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
            elif isinstance(block, ToolUseBlock):
                print(f"Tool: {block.name}")
    elif isinstance(message, ResultMessage):
        print(f"Custo: ${message.total_cost_usd}")
```

## 📚 Recursos

- [Documentação Completa](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-python)
- [Exemplos](examples/)
- [Changelog](CHANGELOG.md)
- [Issues](https://github.com/anthropics/claude-agent-sdk/issues)

## 🔄 Migrando de v0.0.x

```python
# ❌ Antigo (v0.0.x)
from claude_code_sdk import query, ClaudeCodeOptions

options = ClaudeCodeOptions()  # Carregava CLAUDE.md automaticamente

# ✅ Novo (v0.1.0+)
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    setting_sources=["user", "project", "local"]  # Explícito
)
```

## 🎯 Casos de Uso Reais

### Chat com Memória
```python
# Chat que lembra conversas anteriores
async with ClaudeSDKClient() as client:
    while True:
        user_input = input("Você: ")
        await client.query(user_input)
        async for msg in client.receive_response():
            # Claude lembra tudo que foi dito antes
            print(f"Claude: {msg}")
```

### Debugging Iterativo
```python
# Refinar código em múltiplas iterações
async with ClaudeSDKClient() as client:
    await client.query("Escreva função que valida email")
    # ... Claude escreve versão 1

    await client.query("Adicione validação de domínio")
    # Claude MELHORA o código anterior

    await client.query("Adicione testes")
    # Claude cria testes para o código refinado
```

### Sistema Autônomo
```python
# Pipeline autônomo com hooks e auto-approval
options = ClaudeAgentOptions(
    allowed_tools=["Task", "Read", "Write"],
    hooks={
        "PreToolUse": [HookMatcher(matcher=None, hooks=[auto_approve_hook])]
    }
)

async with ClaudeSDKClient(options=options) as client:
    # Processa ideias automaticamente sem intervenção
    for ideia in ideias:
        await client.query(f"Processe: {ideia}")
        # Hooks aprovam automaticamente
        # Resultados salvos automaticamente
```

## 📄 Licença

MIT

---

**Desenvolvido com conhecimento do Neo4j** 🧠
- Multi-turno vs Single-turno
- ClaudeAgentOptions obrigatório
- MCP tools limitados ao contexto principal
- Hooks para automação
- Error handling robusto

Veja documentação completa em [docs.anthropic.com](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-python)
