# 📚 Padrões de Uso - Best Practices

## Padrões Fundamentais

### **Padrão 1: Async Context Manager (SEMPRE use isso)**

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("Pergunta")
    async for msg in client.receive_response():
        process(msg)
```

**Por quê:**
- ✅ Cleanup automático
- ✅ Desconexão garantida
- ✅ Exception-safe
- ✅ Código mais limpo

### **Padrão 2: Separar Opções de Cliente**

```python
# ✅ BOM
options = ClaudeAgentOptions(
    system_prompt="Especialista em Python",
    model="claude-sonnet-4-5",
    max_turns=5,
)

async with ClaudeSDKClient(options=options) as client:
    # Reutilizar options em múltiplos clients
    pass

# ❌ RUIM
async with ClaudeSDKClient(
    options=ClaudeAgentOptions(
        system_prompt="...",
        model="...",
        # ... muitos parâmetros inline
    )
) as client:
    pass
```

### **Padrão 3: Processar Mensagens por Tipo**

```python
from claude_agent_sdk import AssistantMessage, TextBlock, ResultMessage

async with ClaudeSDKClient() as client:
    await client.query("Análise este código...")

    async for msg in client.receive_response():
        # Pattern matching por tipo
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"Texto: {block.text}")
                elif isinstance(block, ThinkingBlock):
                    print(f"Pensamento: {block.thinking}")

        elif isinstance(msg, ResultMessage):
            print(f"Custo: ${msg.total_cost_usd:.4f}")
            print(f"Turnos: {msg.num_turns}")
```

## Padrões de Conversa

### **Padrão 4: Multi-Turn Context**

```python
async with ClaudeSDKClient(options=options) as client:
    # Turno 1: Análise
    await client.query("Analise este código: print('hello')")
    async for msg in client.receive_response():
        pass  # Processar

    # Turno 2: Otimização (mantém contexto do turno 1!)
    await client.query("Agora otimize esse código")
    async for msg in client.receive_response():
        pass

    # Turno 3: Teste
    await client.query("Escreva testes para o código otimizado")
    async for msg in client.receive_response():
        pass
```

### **Padrão 5: Coletar Resposta Completa**

```python
# Coletar todas as mensagens em lista
await client.query("Pergunta")

messages = [msg async for msg in client.receive_response()]

# Última mensagem é sempre ResultMessage
result = messages[-1]
assert isinstance(result, ResultMessage)

# Filtrar apenas texto
text_blocks = []
for msg in messages:
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                text_blocks.append(block.text)

full_text = "\n".join(text_blocks)
```

### **Padrão 6: Streaming com Callback**

```python
async def process_stream(message):
    """Callback para processar cada mensagem."""
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text, end="", flush=True)  # Streaming visual

await client.query("Conte uma história longa")

async for msg in client.receive_response():
    await process_stream(msg)
```

## Padrões de Erro

### **Padrão 7: Try-Except com Cleanup**

```python
client = ClaudeSDKClient(options=options)

try:
    await client.connect()
    await client.query("Tarefa complexa...")

    async for msg in client.receive_response():
        if isinstance(msg, ResultMessage) and msg.is_error:
            print("Erro na execução!")
            break

except Exception as e:
    print(f"Erro: {e}")

finally:
    await client.disconnect()  # Sempre desconectar
```

### **Padrão 8: Retry com Backoff**

```python
import asyncio
from claude_agent_sdk import CLIConnectionError

async def query_with_retry(prompt, max_retries=3):
    """Query com retry exponencial."""
    for attempt in range(max_retries):
        try:
            async with ClaudeSDKClient() as client:
                await client.query(prompt)

                messages = []
                async for msg in client.receive_response():
                    messages.append(msg)

                return messages

        except CLIConnectionError as e:
            if attempt == max_retries - 1:
                raise  # Última tentativa, propagar erro

            wait_time = 2 ** attempt  # 1s, 2s, 4s
            print(f"Retry {attempt + 1}/{max_retries} em {wait_time}s...")
            await asyncio.sleep(wait_time)
```

## Padrões de Performance

### **Padrão 9: Batch Processing**

```python
async def process_batch(prompts: list[str]):
    """Processa múltiplos prompts em sequência."""
    results = []

    async with ClaudeSDKClient() as client:
        for i, prompt in enumerate(prompts):
            print(f"[{i+1}/{len(prompts)}] Processando...")

            await client.query(prompt)

            response_text = []
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            response_text.append(block.text)

            results.append("\n".join(response_text))

    return results

# Usar
prompts = ["Análise 1", "Análise 2", "Análise 3"]
results = await process_batch(prompts)
```

### **Padrão 10: Sessões Paralelas**

```python
async def parallel_queries():
    """Múltiplas queries em paralelo (mesma conexão)."""
    async with ClaudeSDKClient() as client:
        # Enviar queries em paralelo
        await client.query("Tarefa 1", session_id="session_1")
        await client.query("Tarefa 2", session_id="session_2")
        await client.query("Tarefa 3", session_id="session_3")

        # Receber todas as respostas
        session_results = {"session_1": [], "session_2": [], "session_3": []}

        async for msg in client.receive_messages():
            if isinstance(msg, ResultMessage):
                session_id = msg.session_id
                session_results[session_id].append(msg)

                # Parar quando todas sessões terminarem
                if all(len(results) > 0 for results in session_results.values()):
                    break

        return session_results
```

## Padrões de Hooks

### **Padrão 11: Hook de Persistência**

```python
async def persist_hook(input_data, tool_use_id, context):
    """Persiste operações importantes."""
    result = input_data.get("result", "")

    # Detectar padrões importantes
    import re
    patterns = {
        "validation": r'score=(\d+\.\d+)',
        "generation": r'CTR=(\d+\.\d+)',
        "completion": r'Pipeline concluído',
    }

    for pattern_type, pattern_regex in patterns.items():
        match = re.search(pattern_regex, str(result))
        if match:
            # Persistir no Neo4j
            await context.mcp_call(
                "mcp__neo4j-memory__learn_from_result",
                {
                    "task": f"Operation: {pattern_type}",
                    "result": match.group(0),
                    "success": True,
                    "category": pattern_type
                }
            )

    return {}
```

### **Padrão 12: Auto-Enhancement**

```python
async def enhance_prompts_hook(input_data, tool_use_id, context):
    """Aprimora prompts automaticamente."""
    prompt = input_data.get("prompt", "")

    enhancements = {
        "escrever código": "\n\nInclua docstrings e type hints.",
        "criar teste": "\n\nUse pytest e cubra edge cases.",
        "analisar": "\n\nSeja específico e dê exemplos.",
    }

    for trigger, enhancement in enhancements.items():
        if trigger in prompt.lower():
            enhanced = prompt + enhancement

            return {
                "hookSpecificOutput": {
                    "modified_prompt": enhanced
                },
                "systemMessage": f"✨ Prompt aprimorado: {trigger}"
            }

    return {}
```

## Padrões de Tools Customizadas

### **Padrão 13: Tool com Estado**

```python
class Counter:
    def __init__(self):
        self.value = 0

counter = Counter()

@tool("increment", "Incrementar contador", {})
async def increment(args):
    counter.value += 1
    return {"content": [{"type": "text", "text": f"Contador: {counter.value}"}]}

@tool("reset", "Resetar contador", {})
async def reset(args):
    counter.value = 0
    return {"content": [{"type": "text", "text": "Contador resetado"}]}

# Tools compartilham estado!
```

### **Padrão 14: Tool com Dependências**

```python
import httpx
from pathlib import Path

@tool("download_file", "Baixar arquivo", {"url": str, "filename": str})
async def download_file(args):
    """Tool que depende de httpx."""
    url = args["url"]
    filename = args["filename"]

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        # Salvar arquivo
        Path(filename).write_bytes(response.content)

        size_kb = len(response.content) / 1024

        return {"content": [{"type": "text", "text": f"Baixado: {filename} ({size_kb:.1f} KB)"}]}
```

### **Padrão 15: Tool com Validação**

```python
@tool("create_user", "Criar usuário", {"email": str, "age": int})
async def create_user(args):
    """Tool com validação completa."""
    email = args["email"]
    age = args["age"]

    # Validação 1: Email
    if "@" not in email or "." not in email:
        return {
            "content": [{"type": "text", "text": "❌ Email inválido"}],
            "is_error": True
        }

    # Validação 2: Idade
    if age < 0 or age > 150:
        return {
            "content": [{"type": "text", "text": "❌ Idade inválida (0-150)"}],
            "is_error": True
        }

    # Criar usuário
    user_id = len(users_db) + 1
    users_db.append({"id": user_id, "email": email, "age": age})

    return {"content": [{"type": "text", "text": f"✅ Usuário #{user_id} criado"}]}
```

## Padrões de Arquitetura

### **Padrão 16: Pipeline com Múltiplos Agents**

```python
async def pipeline_com_agents():
    """Pipeline usando múltiplos clients em sequência."""

    # Etapa 1: Análise
    options_analise = ClaudeAgentOptions(
        system_prompt="Você é um analisador de código",
        max_turns=3,
    )

    async with ClaudeSDKClient(options=options_analise) as client:
        await client.query("Analise este código...")
        analise_result = [msg async for msg in client.receive_response()]

    # Etapa 2: Implementação (usa resultado da análise)
    options_impl = ClaudeAgentOptions(
        system_prompt="Você é um desenvolvedor",
        permission_mode="acceptEdits",
        max_turns=10,
    )

    async with ClaudeSDKClient(options=options_impl) as client:
        await client.query(f"Implemente melhorias baseadas nesta análise: {analise_result}")
        impl_result = [msg async for msg in client.receive_response()]

    return {"analise": analise_result, "implementacao": impl_result}
```

### **Padrão 17: Agent com Tools Customizadas**

```python
# 1. Criar tools
@tool("get_context", "Obter contexto do Neo4j", {"query": str})
async def get_context(args):
    # Buscar contexto relevante
    context = await search_neo4j(args["query"])
    return {"content": [{"type": "text", "text": context}]}

# 2. Criar servidor
context_server = create_sdk_mcp_server("context", tools=[get_context])

# 3. Usar com agent especializado
options = ClaudeAgentOptions(
    system_prompt=(
        "Você é um gerador de títulos virais. "
        "SEMPRE use a tool 'get_context' ANTES de gerar títulos "
        "para aprender com exemplos anteriores."
    ),
    mcp_servers={"context": context_server},
    allowed_tools=["get_context"],
    max_turns=5,
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Gere título sobre streaming")
    # Claude usará get_context automaticamente antes de gerar
```

### **Padrão 18: Retry Inteligente**

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def query_with_fallback(prompt: str, max_retries: int = 3):
    """Query com fallback para modelo mais simples se falhar."""
    models = ["claude-opus-4", "claude-sonnet-4-5", "claude-haiku-4"]

    for attempt, model in enumerate(models):
        try:
            options = ClaudeAgentOptions(model=model)

            async with ClaudeSDKClient(options=options) as client:
                await client.query(prompt)

                messages = []
                async for msg in client.receive_response():
                    messages.append(msg)

                    # Verificar se resultou em erro
                    if isinstance(msg, ResultMessage) and msg.is_error:
                        raise Exception("Query resultou em erro")

                return messages

        except Exception as e:
            print(f"Tentativa {attempt + 1} com {model} falhou: {e}")

            if attempt == len(models) - 1:
                raise  # Última tentativa

            print(f"Tentando próximo modelo...")

    return []
```

## Padrões de Debugging

### **Padrão 19: Debug Completo**

```python
import json

async def debug_conversation():
    """Modo debug com logging completo."""
    options = ClaudeAgentOptions(
        system_prompt="Debug assistant",
        hooks={
            "PreToolUse": [HookMatcher(hooks=[log_pre])],
            "PostToolUse": [HookMatcher(hooks=[log_post])],
        }
    )

    async def log_pre(input_data, tool_use_id, context):
        print(f"🔍 PRE: {input_data.get('tool_name')}")
        print(f"   Input: {json.dumps(input_data.get('tool_input', {}), indent=2)[:200]}")
        return {}

    async def log_post(input_data, tool_use_id, context):
        print(f"✅ POST: {input_data.get('tool_name')}")
        print(f"   Error: {input_data.get('is_error', False)}")
        print(f"   Result: {str(input_data.get('result', ''))[:200]}")
        return {}

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Debug this...")

        async for msg in client.receive_response():
            print(f"📨 Message type: {type(msg).__name__}")
            print(f"   Content: {str(msg)[:200]}")
```

### **Padrão 20: Capturar Erros Específicos**

```python
from claude_agent_sdk import CLIConnectionError, CLINotFoundError

try:
    async with ClaudeSDKClient() as client:
        await client.query("...")

except CLINotFoundError:
    print("❌ Claude Code CLI não encontrado")
    print("   Instale: npm install -g @anthropics/claude-code")

except CLIConnectionError:
    print("❌ Erro ao conectar ao Claude Code CLI")
    print("   Verifique se está instalado e acessível")

except Exception as e:
    print(f"❌ Erro inesperado: {e}")
```

## Padrões de Integração

### **Padrão 21: Integração com FastAPI**

```python
from fastapi import FastAPI
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

app = FastAPI()

# Options compartilhadas
options = ClaudeAgentOptions(
    system_prompt="API assistant",
    permission_mode="acceptEdits",
)

@app.post("/generate")
async def generate_endpoint(prompt: str):
    """Endpoint que usa Claude SDK."""
    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)

        text_blocks = []
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        text_blocks.append(block.text)

        return {"response": "\n".join(text_blocks)}
```

### **Padrão 22: Worker Background**

```python
import asyncio

class BackgroundWorker:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False

    async def start(self):
        """Inicia worker em background."""
        self.running = True

        async with ClaudeSDKClient() as client:
            while self.running:
                # Esperar tarefa
                task = await self.queue.get()

                if task is None:  # Sinal de parada
                    break

                # Processar
                await client.query(task["prompt"])

                result = []
                async for msg in client.receive_response():
                    result.append(msg)

                # Callback com resultado
                if task.get("callback"):
                    await task["callback"](result)

    async def add_task(self, prompt: str, callback=None):
        """Adiciona tarefa à fila."""
        await self.queue.put({"prompt": prompt, "callback": callback})

    async def stop(self):
        """Para worker."""
        self.running = False
        await self.queue.put(None)

# Usar
worker = BackgroundWorker()
asyncio.create_task(worker.start())

# Adicionar tarefas
await worker.add_task("Tarefa 1")
await worker.add_task("Tarefa 2", callback=lambda r: print(f"Done: {r}"))

# Parar
await worker.stop()
```

## Anti-Padrões (Evite!)

### **❌ Anti-Padrão 1: Sem Context Manager**

```python
# ❌ RUIM
client = ClaudeSDKClient()
await client.connect()
await client.query("...")
# Esqueceu de desconectar!

# ✅ BOM
async with ClaudeSDKClient() as client:
    await client.query("...")
# Desconecta automaticamente
```

### **❌ Anti-Padrão 2: Nesting de Clients**

```python
# ❌ RUIM - DEADLOCK!
async with ClaudeSDKClient() as client1:
    await client1.query("Use ClaudeSDKClient para...")

    # Client2 dentro de client1 = DEADLOCK
    async with ClaudeSDKClient() as client2:
        await client2.query("Tarefa aninhada")

# ✅ BOM
async with ClaudeSDKClient() as client:
    await client.query("Primeira tarefa")
    # Processar...

async with ClaudeSDKClient() as client:
    await client.query("Segunda tarefa (sequencial)")
```

### **❌ Anti-Padrão 3: Ignorar ResultMessage**

```python
# ❌ RUIM
await client.query("...")

async for msg in client.receive_response():
    if isinstance(msg, AssistantMessage):
        print(msg)
    # Não verificou ResultMessage! Não sabe custo, se teve erro, etc.

# ✅ BOM
await client.query("...")

async for msg in client.receive_response():
    if isinstance(msg, AssistantMessage):
        print(msg)
    elif isinstance(msg, ResultMessage):
        if msg.is_error:
            print("❌ Erro na execução!")
        print(f"💰 Custo: ${msg.total_cost_usd:.4f}")
```

### **❌ Anti-Padrão 4: Sync em Async**

```python
# ❌ RUIM
async def bad_pattern():
    async with ClaudeSDKClient() as client:
        await client.query("...")

        # Processar com sync (bloqueia event loop!)
        import time
        time.sleep(5)  # BLOQUEIA TUDO!

# ✅ BOM
async def good_pattern():
    async with ClaudeSDKClient() as client:
        await client.query("...")

        # Processar com async
        await asyncio.sleep(5)  # Não bloqueia
```

## Ver Também

- `01_CONCEITOS_FUNDAMENTAIS.md` - Introdução
- `02_CLAUDESDKCLIENT_COMPLETO.md` - API completa
- `03_HOOKS_SISTEMA.md` - Hooks
- `04_MCP_TOOLS_CUSTOMIZADAS.md` - Tools
- `07_TROUBLESHOOTING.md` - Problemas comuns
