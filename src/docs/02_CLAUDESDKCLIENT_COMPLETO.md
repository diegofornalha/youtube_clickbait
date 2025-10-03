# 🔄 ClaudeSDKClient - Referência Completa

## Classe Principal

```python
class ClaudeSDKClient:
    """Cliente para conversas bidirecionais e interativas com Claude Code."""
```

## Construtor

```python
def __init__(
    self,
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None,
)
```

### **Parâmetros:**

**`options`** (ClaudeAgentOptions | None)
- Configurações do agent (model, system_prompt, tools, etc)
- Se None, usa padrões

**`transport`** (Transport | None)
- Transporte customizado (avançado)
- Se None, cria `SubprocessCLITransport` automaticamente

### **Exemplo:**
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

# Padrões
client = ClaudeSDKClient()

# Com opções
options = ClaudeAgentOptions(
    system_prompt="Especialista em Python",
    model="claude-sonnet-4-5",
    max_turns=5
)
client = ClaudeSDKClient(options=options)

# Com transport customizado (raro)
custom_transport = MyCustomTransport()
client = ClaudeSDKClient(transport=custom_transport)
```

## Métodos Principais

### **1. connect()** - Conectar ao Claude

```python
async def connect(
    self,
    prompt: str | AsyncIterable[dict[str, Any]] | None = None
) -> None
```

**Parâmetros:**
- `prompt` (opcional):
  - `str` - Prompt inicial simples
  - `AsyncIterable` - Stream de mensagens
  - `None` - Conecta vazio (modo interativo)

**Uso:**
```python
# Conectar vazio
await client.connect()

# Conectar com prompt inicial
await client.connect("Analise este código...")

# Conectar com stream (avançado)
async def message_stream():
    yield {"type": "user", "message": {...}}
    yield {"type": "user", "message": {...}}

await client.connect(message_stream())
```

### **2. query()** - Enviar Mensagem

```python
async def query(
    self,
    prompt: str | AsyncIterable[dict[str, Any]],
    session_id: str = "default"
) -> None
```

**Parâmetros:**
- `prompt` - Mensagem ou stream
- `session_id` - ID da sessão (para múltiplas conversas paralelas)

**Uso:**
```python
# Enviar mensagem simples
await client.query("Qual é a capital da França?")

# Múltiplas sessões paralelas
await client.query("Pergunta 1", session_id="sessao_1")
await client.query("Pergunta 2", session_id="sessao_2")

# Stream de mensagens
async def messages():
    yield {"type": "user", "message": {"role": "user", "content": "Oi"}}

await client.query(messages())
```

### **3. receive_messages()** - Receber Todas Mensagens

```python
async def receive_messages() -> AsyncIterator[Message]
```

**Retorna:**
AsyncIterator que **nunca termina** sozinho. Continue recebendo até decidir parar.

**Uso:**
```python
async for msg in client.receive_messages():
    if isinstance(msg, AssistantMessage):
        # Processar resposta
        print(msg.content)

    if isinstance(msg, ResultMessage):
        # Conversa terminou
        print(f"Custo: ${msg.total_cost_usd}")
        break  # Você decide quando parar
```

### **4. receive_response()** - Receber Até ResultMessage

```python
async def receive_response() -> AsyncIterator[Message]
```

**Retorna:**
AsyncIterator que **termina automaticamente** após `ResultMessage`.

**Diferença de `receive_messages()`:**
- `receive_messages()` - Nunca para sozinho
- `receive_response()` - Para após ResultMessage

**Uso:**
```python
await client.query("Pergunta")

# Para automaticamente após ResultMessage
async for msg in client.receive_response():
    print(msg)  # Processa todas as mensagens
# Loop termina automaticamente após ResultMessage
```

### **5. interrupt()** - Interromper Execução

```python
async def interrupt() -> None
```

**O que faz:**
Cancela execução em andamento (para ferramentas longas, loops, etc).

**Uso:**
```python
import asyncio

async def interromper_apos_timeout():
    await asyncio.sleep(30)  # Espera 30s
    await client.interrupt()  # Cancela

# Iniciar timeout em paralelo
asyncio.create_task(interromper_apos_timeout())

# Executar query (pode ser interrompida)
await client.query("Tarefa muito longa...")
```

### **6. set_permission_mode()** - Mudar Permissões

```python
async def set_permission_mode(self, mode: str) -> None
```

**Modos:**
- `"default"` - CLI pede permissão para ferramentas perigosas
- `"acceptEdits"` - Auto-aceita edições de arquivos
- `"bypassPermissions"` - Permite tudo (⚠️ cuidado)

**Uso:**
```python
async with ClaudeSDKClient() as client:
    # Começa em modo seguro
    await client.query("Analise este código")

    # Muda para aceitar edições
    await client.set_permission_mode("acceptEdits")
    await client.query("Agora conserte os bugs")
```

### **7. set_model()** - Trocar Modelo

```python
async def set_model(self, model: str | None = None) -> None
```

**Modelos disponíveis:**
- `"claude-sonnet-4-5"` - Rápido e balanceado
- `"claude-opus-4"` - Mais poderoso
- `"claude-haiku-4"` - Mais rápido e barato

**Uso:**
```python
async with ClaudeSDKClient() as client:
    # Começa com Sonnet
    await client.query("Resuma este documento")

    # Muda para Opus para tarefa complexa
    await client.set_model("claude-opus-4")
    await client.query("Agora escreva código complexo")
```

### **8. get_server_info()** - Info do Servidor

```python
async def get_server_info(self) -> dict[str, Any] | None
```

**Retorna:**
- Comandos disponíveis (slash commands)
- Estilos de output
- Capabilities do servidor

**Uso:**
```python
async with ClaudeSDKClient() as client:
    info = await client.get_server_info()
    print(f"Comandos: {info.get('commands', [])}")
    print(f"Output style: {info.get('output_style')}")
```

### **9. disconnect()** - Desconectar

```python
async def disconnect(self) -> None
```

**Uso:**
```python
client = ClaudeSDKClient()
await client.connect()
# ... usar client ...
await client.disconnect()
```

**Nota:** Se usar `async with`, desconecta automaticamente.

## Padrões de Uso

### **Padrão 1: Context Manager (Recomendado)**

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("Pergunta")
    async for msg in client.receive_response():
        process(msg)
# Desconecta automaticamente
```

**Vantagens:**
- ✅ Desconexão automática
- ✅ Cleanup garantido mesmo com exceções
- ✅ Código mais limpo

### **Padrão 2: Manual (Mais Controle)**

```python
client = ClaudeSDKClient(options=options)
try:
    await client.connect()
    await client.query("Pergunta")
    async for msg in client.receive_response():
        process(msg)
finally:
    await client.disconnect()
```

**Vantagens:**
- ✅ Controle explícito de lifecycle
- ✅ Útil para debugging
- ⚠️ Precisa garantir disconnect

### **Padrão 3: Stream de Input (Avançado)**

```python
async def user_input_stream():
    """Simula input do usuário em tempo real."""
    yield {"type": "user", "message": {"role": "user", "content": "Oi"}}
    await asyncio.sleep(2)
    yield {"type": "user", "message": {"role": "user", "content": "Continue"}}

async with ClaudeSDKClient() as client:
    await client.connect(user_input_stream())
    async for msg in client.receive_messages():
        print(msg)
```

## Limitações Conhecidas

### **⚠️ Async Runtime Context**

**Problema:** Não pode usar client em contextos async diferentes.

```python
# ❌ ERRADO
async with trio.open_nursery() as nursery:
    client = ClaudeSDKClient()
    await client.connect()
    # Não pode passar client para task em outro nursery

# ✅ CORRETO
async with ClaudeSDKClient() as client:
    # Toda interação no mesmo contexto
    await client.query("...")
    async for msg in client.receive_response():
        pass
```

## Comparação: ClaudeSDKClient vs query()

| Aspecto | ClaudeSDKClient | query() |
|---------|----------------|---------|
| **Estado** | Stateful | Stateless |
| **Turnos** | Multi-turn | Single-turn |
| **Controle** | Total (interrupt, set_model) | Limitado |
| **Complexidade** | Média | Baixa |
| **Uso Recomendado** | ✅ Sempre | ❌ Deprecado |
| **Context Manager** | ✅ Sim | ❌ Não |
| **Streaming** | ✅ Sim | ✅ Sim |

## Exemplo Completo

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
        system_prompt="Você é um assistente Python expert",
        model="claude-sonnet-4-5",
        max_turns=5,
        permission_mode="acceptEdits",
    )

    # Executar conversa
    async with ClaudeSDKClient(options=options) as client:
        # Primeira pergunta
        await client.query("Analise este código: print('hello')")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

            elif isinstance(msg, ResultMessage):
                print(f"Custo: ${msg.total_cost_usd:.4f}")

        # Segunda pergunta (mantém contexto)
        await client.query("Agora otimize esse código")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

anyio.run(main)
```

## Ver Também

- `03_HOOKS_SISTEMA.md` - Interceptar execuções
- `04_MCP_TOOLS.md` - Criar ferramentas
- `05_PERMISSOES.md` - Sistema de permissões
- `06_PADROES_USO.md` - Best practices
