# 🎯 Conceitos Fundamentais do Claude Agent SDK

## O que é o Claude Agent SDK?

SDK Python para interagir com **Claude Code** (CLI oficial da Anthropic). Permite criar agents, automações e pipelines usando Claude.

## Componentes Principais

### 1. **ClaudeSDKClient** 🔄
```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient(options=options) as client:
    await client.query("Sua pergunta")
    async for message in client.receive_response():
        print(message)
```

**Características:**
- ✅ **Stateful** - Mantém contexto de conversação
- ✅ **Bidirecional** - Enviar e receber mensagens a qualquer momento
- ✅ **Streaming** - Respostas em tempo real
- ✅ **Multi-turn** - Conversas com múltiplas interações
- ✅ **Context Manager** - Gerencia conexão automaticamente

**Quando usar:**
- Chat interfaces
- Conversas interativas
- Debugging exploratório
- Aplicações em tempo real
- Quando precisa reagir às respostas

### 2. **query()** ⚡ (DEPRECATED - usar ClaudeSDKClient)
```python
from claude_agent_sdk import query

async for message in query("Sua pergunta", options=options):
    print(message)
```

**Características:**
- ⚠️ **Stateless** - Sem contexto entre chamadas
- ⚠️ **One-shot** - Uma pergunta, uma resposta
- ⚠️ **Simplificado** - API mais básica

**Quando usar:**
- **NUNCA** - Prefira sempre ClaudeSDKClient

### 3. **Transport** 🚇
```python
from claude_agent_sdk import Transport
```

**O que é:**
Camada de comunicação com Claude Code CLI. Gerencia subprocess, stdin/stdout, protocolo de controle.

**Tipos:**
- `SubprocessCLITransport` - Roda Claude Code como subprocess
- Custom transports - Você pode criar o seu próprio

**Normalmente:**
Não precisa usar diretamente. O `ClaudeSDKClient` cria automaticamente.

## Fluxo de Dados

```
Seu Código Python
      ↓
ClaudeSDKClient
      ↓
Transport (subprocess)
      ↓
Claude Code CLI
      ↓
API Anthropic
      ↓
Claude (modelo)
      ↓
Resposta (streaming)
      ↑
Seu Código (async iterator)
```

## Tipos de Mensagens

### **UserMessage** 👤
```python
from claude_agent_sdk import UserMessage

message = UserMessage(
    content="Sua pergunta",
    parent_tool_use_id=None
)
```

### **AssistantMessage** 🤖
```python
from claude_agent_sdk import AssistantMessage, TextBlock

# Recebida do Claude
async for msg in client.receive_response():
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(block.text)
```

**Content Blocks:**
- `TextBlock` - Texto normal
- `ThinkingBlock` - Pensamento interno do Claude
- `ToolUseBlock` - Claude quer usar ferramenta
- `ToolResultBlock` - Resultado de ferramenta

### **ResultMessage** 📊
```python
from claude_agent_sdk import ResultMessage

# Última mensagem do streaming
if isinstance(msg, ResultMessage):
    print(f"Custo: ${msg.total_cost_usd}")
    print(f"Turnos: {msg.num_turns}")
    print(f"Duração: {msg.duration_ms}ms")
```

### **SystemMessage** ⚙️
```python
# Mensagens internas do sistema
if isinstance(msg, SystemMessage):
    print(f"Sistema: {msg.subtype} - {msg.data}")
```

## Ciclo de Vida

### **1. Inicialização**
```python
client = ClaudeSDKClient(options=ClaudeAgentOptions(...))
```

### **2. Conexão**
```python
await client.connect()
# ou
async with ClaudeSDKClient() as client:
    # Conecta automaticamente
```

### **3. Interação**
```python
# Enviar mensagem
await client.query("Pergunta")

# Receber respostas
async for msg in client.receive_response():
    process(msg)
```

### **4. Desconexão**
```python
await client.disconnect()
# ou
# Context manager desconecta automaticamente ao sair
```

## Options e Configuração

### **ClaudeAgentOptions**
```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    # Modelo
    model="claude-sonnet-4-5",

    # Prompt de sistema
    system_prompt="Você é um especialista em...",

    # Ferramentas permitidas
    allowed_tools=["Read", "Write", "Bash"],
    disallowed_tools=["SlashCommand"],

    # Permissões
    permission_mode="default",  # ou "acceptEdits", "bypassPermissions"

    # Diretório de trabalho
    cwd="/path/to/project",

    # MCP Servers
    mcp_servers={"server_name": server_config},

    # Hooks
    hooks={
        "PreToolUse": [HookMatcher(matcher="Bash", hooks=[my_hook])],
    },

    # Limites
    max_turns=10,

    # Ambiente
    env={"VAR": "value"},
)
```

## Modo Async Obrigatório

**IMPORTANTE:** Todo o SDK é async. Você DEVE usar:

```python
import anyio

async def main():
    async with ClaudeSDKClient() as client:
        await client.query("...")
        async for msg in client.receive_response():
            print(msg)

# Executar
anyio.run(main)
```

Ou com `asyncio`:
```python
import asyncio

asyncio.run(main())
```

## Próximos Passos

- 📖 Ler `02_API_REFERENCE.md` para detalhes de cada classe
- 🪝 Ler `03_HOOKS_SISTEMA.md` para interceptar execuções
- 🔧 Ler `04_MCP_TOOLS.md` para criar ferramentas customizadas
- 🛡️ Ler `05_PERMISSOES.md` para controle de segurança
