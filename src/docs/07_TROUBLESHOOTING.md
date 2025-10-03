# 🔧 Troubleshooting - Problemas Comuns e Soluções

## Erros de Conexão

### **Problema: CLINotFoundError**

```
CLINotFoundError: Claude Code CLI not found
```

**Causa:** Claude Code CLI não está instalado ou não está no PATH.

**Solução:**
```bash
# Instalar Claude Code CLI
npm install -g @anthropics/claude-code

# Verificar instalação
claude --version
```

### **Problema: CLIConnectionError**

```
CLIConnectionError: Failed to connect to Claude Code
```

**Causas possíveis:**
1. Claude Code CLI crashou ao iniciar
2. Permissões incorretas
3. Python versão incompatível

**Soluções:**
```bash
# Verificar se CLI funciona standalone
claude query "hello"

# Verificar permissões
which claude
ls -la $(which claude)

# Verificar Python version (precisa 3.10+)
python --version
```

### **Problema: Timeout ao conectar**

```python
# Timeout após 30s de espera
```

**Causa:** CLI está travado ou não está respondendo.

**Solução:**
```python
# Adicionar timeout menor para fail-fast
import asyncio

try:
    async with asyncio.timeout(10):  # 10s timeout
        async with ClaudeSDKClient() as client:
            await client.connect()
except asyncio.TimeoutError:
    print("❌ Timeout ao conectar")
```

## Erros de Runtime

### **Problema: "can't be used in 'await' expression"**

```
TypeError: object _AsyncGeneratorContextManager can't be used in 'await' expression
```

**Causa:** Tentou `await` em async context manager.

**Solução:**
```python
# ❌ ERRADO
async with await stdio_client(params) as (read, write):
    ...

# ✅ CORRETO
async with stdio_client(params) as (read, write):
    ...

# Ou
context = stdio_client(params)
read, write = await context.__aenter__()
```

### **Problema: Deadlock em ClaudeSDKClient Aninhado**

```python
# Cliente trava infinitamente
```

**Causa:** ClaudeSDKClient dentro de outro ClaudeSDKClient.

**Solução:**
```python
# ❌ ERRADO
async with ClaudeSDKClient() as client1:
    # Dentro de client1, criar outro client = DEADLOCK
    async with ClaudeSDKClient() as client2:
        ...

# ✅ CORRETO
# Cliente 1
async with ClaudeSDKClient() as client:
    await client.query("Tarefa 1")
    ...

# Cliente 2 (sequencial, não aninhado)
async with ClaudeSDKClient() as client:
    await client.query("Tarefa 2")
    ...
```

### **Problema: JSON parsing falha**

```python
# Esperava JSON, recebeu texto
json.JSONDecodeError: Expecting value: line 1 column 1
```

**Causa:** Claude retornou texto ao invés de JSON.

**Solução:**
```python
async def extract_json_safe(response_text):
    """Extrai JSON mesmo se tiver texto antes/depois."""
    import json
    import re

    # Procurar por JSON na resposta
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

    if not json_match:
        # Fallback: retornar estrutura padrão
        return {"error": "No JSON found", "raw": response_text}

    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError as e:
        return {"error": str(e), "raw": response_text}

# Usar
full_response = "... texto antes ... {\"result\": \"ok\"} ... texto depois ..."
data = await extract_json_safe(full_response)
```

## Erros de Configuração

### **Problema: Tool não é chamada**

**Sintomas:**
- Claude não usa sua tool customizada
- Tool é ignorada

**Causas:**
1. Tool não está em `allowed_tools`
2. Description não é clara
3. Tool name tem conflito

**Soluções:**
```python
# 1. Verificar allowed_tools
options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["add", "multiply"],  # ← OBRIGATÓRIO!
)

# 2. Melhorar description
@tool("add", "Somar dois números e retornar o resultado", {"a": float, "b": float})
#           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#           Description clara ajuda Claude a decidir quando usar

# 3. Evitar conflitos de nome
# ❌ RUIM: "read" (conflita com ferramenta Read do Claude Code)
# ✅ BOM: "read_user_data"
```

### **Problema: Hook não é chamado**

**Sintomas:**
- Hook nunca executa
- Sem logs do hook

**Causas:**
1. Matcher incorreto
2. Hook não configurado corretamente
3. Hook retorna antes de executar lógica

**Soluções:**
```python
# 1. Verificar matcher
options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [
            HookMatcher(
                matcher="Bash",  # ← Deve ser nome exato da tool
                hooks=[my_hook]
            )
        ]
    }
)

# 2. Debug do hook
async def debug_hook(input_data, tool_use_id, context):
    print("🔍 HOOK EXECUTADO!")  # Se não aparecer, hook não está sendo chamado
    print(f"   Tool: {input_data.get('tool_name')}")
    return {}

# 3. Verificar que hook é async
# ❌ ERRADO
def my_hook(input_data, tool_use_id, context):  # Sync!
    return {}

# ✅ CORRETO
async def my_hook(input_data, tool_use_id, context):  # Async!
    return {}
```

## Erros de Mensagens

### **Problema: AssistantMessage sem content**

```python
# msg.content está vazio
```

**Causa:** Claude ainda está processando ou esperando tool result.

**Solução:**
```python
async for msg in client.receive_response():
    if isinstance(msg, AssistantMessage):
        if not msg.content:
            print("⏳ Claude está processando...")
            continue

        for block in msg.content:
            print(block)
```

### **Problema: Streaming nunca termina**

**Sintomas:**
- `receive_response()` nunca para
- Loop infinito

**Causa:** Usando `receive_messages()` ao invés de `receive_response()`.

**Solução:**
```python
# ❌ ERRADO - nunca termina sozinho
async for msg in client.receive_messages():
    print(msg)
# Loop infinito!

# ✅ CORRETO - para após ResultMessage
async for msg in client.receive_response():
    print(msg)
# Termina automaticamente
```

## Erros de Performance

### **Problema: Cliente muito lento**

**Sintomas:**
- Demora muito para receber primeira mensagem
- Alto uso de CPU

**Causas:**
1. System prompt muito longo
2. Muito contexto no histórico
3. max_turns muito alto

**Soluções:**
```python
# 1. System prompt conciso
options = ClaudeAgentOptions(
    system_prompt="Expert em Python. Seja conciso."  # Curto!
)

# 2. Limitar max_turns
options = ClaudeAgentOptions(
    max_turns=5  # Limitar iterações
)

# 3. Não acumular histórico infinito
# Use sessões novas periodicamente
for i, prompt in enumerate(prompts):
    # Nova sessão a cada 10 prompts
    session_id = f"session_{i // 10}"

    async with ClaudeSDKClient() as client:
        await client.query(prompt, session_id=session_id)
```

### **Problema: Memory leak**

**Sintomas:**
- Uso de memória cresce continuamente
- Aplicação fica lenta ao longo do tempo

**Causa:** Não está fechando connections ou acumulando mensagens.

**Solução:**
```python
# ✅ Sempre usar context manager
async with ClaudeSDKClient() as client:
    # Conexão fecha automaticamente

# ✅ Não acumular mensagens infinitamente
messages = []
async for msg in client.receive_response():
    messages.append(msg)

    # Limitar tamanho
    if len(messages) > 100:
        messages = messages[-50:]  # Manter apenas 50 últimas
```

## Erros de MCP Tools

### **Problema: Tool retorna erro mas não marca is_error**

**Sintomas:**
- Claude acha que tool funcionou
- Erro não é tratado

**Solução:**
```python
@tool("divide", "...", {"a": float, "b": float})
async def divide(args):
    if args["b"] == 0:
        return {
            "content": [{"type": "text", "text": "Erro: divisão por zero"}],
            "is_error": True  # ← IMPORTANTE!
        }

    return {"content": [{"type": "text", "text": f"Result: {args['a'] / args['b']}"}]}
```

### **Problema: Tool não aparece em list_tools**

**Causa:** Tool não foi incluída em `tools=[]` ao criar servidor.

**Solução:**
```python
@tool("my_tool", "...", {})
async def my_tool(args):
    return {"content": [{"type": "text", "text": "ok"}]}

# ❌ ERRADO - esqueceu de incluir
server = create_sdk_mcp_server("server", tools=[])

# ✅ CORRETO
server = create_sdk_mcp_server("server", tools=[my_tool])
```

### **Problema: Tool recebe args incorretos**

**Sintomas:**
- KeyError ao acessar args
- Tipos incorretos

**Solução:**
```python
@tool("my_tool", "...", {"name": str, "age": int})
async def my_tool(args):
    # Validar presença
    if "name" not in args or "age" not in args:
        return {
            "content": [{"type": "text", "text": "❌ Parâmetros faltando"}],
            "is_error": True
        }

    # Validar tipos
    try:
        name = str(args["name"])
        age = int(args["age"])
    except (ValueError, TypeError) as e:
        return {
            "content": [{"type": "text", "text": f"❌ Tipo inválido: {e}"}],
            "is_error": True
        }

    # Processar...
```

## Debugging Checklist

### **Cliente não conecta?**

- [ ] Claude Code CLI instalado? (`claude --version`)
- [ ] Python 3.10+? (`python --version`)
- [ ] Biblioteca instalada? (`pip show claude-agent-sdk`)
- [ ] Timeout adequado? (padrão 30s)

### **Tool não funciona?**

- [ ] Tool em `allowed_tools`?
- [ ] Server registrado em `mcp_servers`?
- [ ] Tool name único (sem conflitos)?
- [ ] Input schema correto?
- [ ] Function é async?
- [ ] Retorna dict com "content"?

### **Hook não executa?**

- [ ] Hook registrado em `hooks={...}`?
- [ ] Matcher correto? (nome exato da tool)
- [ ] Function é async?
- [ ] Retorna dict (não None)?
- [ ] Event type correto? (PreToolUse, PostToolUse, etc)

### **Performance ruim?**

- [ ] System prompt muito longo?
- [ ] max_turns muito alto?
- [ ] Acumulando histórico sem limite?
- [ ] Tools fazendo operações síncronas (bloqueantes)?
- [ ] Memory leak (não fechando connections)?

## Ferramentas de Debug

### **1. Logging Detalhado**

```python
import logging

# Ativar logs do SDK
logging.basicConfig(level=logging.DEBUG)

# Logs do Claude Code CLI também aparecem
async with ClaudeSDKClient() as client:
    # Verá todos os logs internos
    await client.query("...")
```

### **2. Capturar stderr do CLI**

```python
def stderr_callback(line: str):
    """Callback para stderr do Claude Code CLI."""
    print(f"[CLI stderr] {line}")

options = ClaudeAgentOptions(
    stderr=stderr_callback  # Recebe todos os erros do CLI
)

async with ClaudeSDKClient(options=options) as client:
    # Verá erros do CLI em tempo real
    await client.query("...")
```

### **3. Inspect de Mensagens**

```python
import json

async for msg in client.receive_response():
    print(f"📨 Message Type: {type(msg).__name__}")
    print(f"   Content: {json.dumps(msg.__dict__, default=str, indent=2)}")
```

### **4. Verificar Server Info**

```python
async with ClaudeSDKClient() as client:
    info = await client.get_server_info()

    print("📊 Server Info:")
    print(f"   Commands: {len(info.get('commands', []))}")
    print(f"   Output styles: {info.get('output_styles', [])}")
    print(f"   Capabilities: {info.get('capabilities', {})}")
```

## Problemas Conhecidos

### **Limitação: Async Runtime Context**

**Problema:**
```python
# ❌ Cliente não funciona em outro nursery/task group
import trio

async def task_with_client():
    async with ClaudeSDKClient() as client:
        await client.query("...")

async with trio.open_nursery() as nursery:
    nursery.start_soon(task_with_client)  # Pode dar erro
```

**Solução:**
```python
# ✅ Usar no mesmo contexto
async with ClaudeSDKClient() as client:
    # Toda lógica aqui
    await client.query("...")
```

### **Limitação: Hooks não disponíveis**

**Hooks NÃO suportados no Python SDK:**
- ❌ SessionStart
- ❌ SessionEnd
- ❌ Notification

**Workaround:**
```python
# Use PreToolUse + PostToolUse para logging manual
async def simulate_session_start(input_data, tool_use_id, context):
    """Simula SessionStart."""
    # Primeira tool = início de sessão
    global session_started
    if not session_started:
        print("🚀 Sessão iniciada")
        session_started = True
    return {}
```

## Patterns de Recuperação

### **Pattern: Retry com Exponential Backoff**

```python
async def query_with_retry(prompt: str, max_retries: int = 3):
    """Query com retry automático."""
    import asyncio

    for attempt in range(max_retries):
        try:
            async with ClaudeSDKClient() as client:
                await client.query(prompt)

                messages = []
                async for msg in client.receive_response():
                    messages.append(msg)

                # Verificar se teve erro
                if messages and isinstance(messages[-1], ResultMessage):
                    if messages[-1].is_error:
                        raise Exception("Query resultou em erro")

                return messages

        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Última tentativa

            wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
            print(f"⚠️ Erro (tentativa {attempt + 1}/{max_retries}): {e}")
            print(f"   Retry em {wait_time}s...")
            await asyncio.sleep(wait_time)

    return []
```

### **Pattern: Fallback para Modelo Mais Simples**

```python
async def query_with_model_fallback(prompt: str):
    """Tenta Opus, fallback para Sonnet, fallback para Haiku."""
    models = ["claude-opus-4", "claude-sonnet-4-5", "claude-haiku-4"]

    for model in models:
        try:
            print(f"🤖 Tentando com {model}...")

            options = ClaudeAgentOptions(model=model, max_turns=5)

            async with ClaudeSDKClient(options=options) as client:
                await client.query(prompt)

                messages = []
                async for msg in client.receive_response():
                    messages.append(msg)

                # Sucesso!
                return {"model": model, "messages": messages}

        except Exception as e:
            print(f"❌ {model} falhou: {e}")
            if model == models[-1]:
                raise  # Último modelo também falhou

    return None
```

## FAQ

### **Q: Como saber se Claude usou uma tool?**

```python
async for msg in client.receive_response():
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, ToolUseBlock):
                print(f"🔧 Claude usou tool: {block.name}")
                print(f"   Input: {block.input}")
```

### **Q: Como cancelar execução?**

```python
import asyncio

async def with_timeout():
    async with ClaudeSDKClient() as client:
        # Criar task de timeout
        async def timeout_interrupt():
            await asyncio.sleep(30)  # 30s
            await client.interrupt()

        asyncio.create_task(timeout_interrupt())

        await client.query("Tarefa longa...")

        async for msg in client.receive_response():
            print(msg)
```

### **Q: Como verificar custo antes de executar?**

**R:** Não é possível saber custo antecipado. Mas você pode:

```python
# Estimar tokens
from tiktoken import encoding_for_model

def estimate_cost(prompt: str, model: str = "claude-sonnet-4-5"):
    """Estima custo baseado em tokens."""
    enc = encoding_for_model("gpt-4")  # Aproximação
    tokens = len(enc.encode(prompt))

    # Preços aproximados (verificar docs atualizadas)
    prices = {
        "claude-opus-4": {"input": 0.015, "output": 0.075},  # $/1K tokens
        "claude-sonnet-4-5": {"input": 0.003, "output": 0.015},
        "claude-haiku-4": {"input": 0.00025, "output": 0.00125},
    }

    price = prices.get(model, prices["claude-sonnet-4-5"])
    estimated_cost = (tokens / 1000) * price["input"]

    return {"tokens": tokens, "estimated_cost_usd": estimated_cost}

# Verificar antes
estimate = estimate_cost("Prompt muito longo...")
if estimate["estimated_cost_usd"] > 0.10:
    print(f"⚠️ Custo estimado alto: ${estimate['estimated_cost_usd']:.4f}")
```

### **Q: Como persistir histórico de conversação?**

```python
import json
from datetime import datetime

async def save_conversation_history():
    """Salva histórico completo."""
    async with ClaudeSDKClient() as client:
        await client.query("Análise complexa...")

        history = []
        async for msg in client.receive_response():
            # Serializar mensagem
            msg_dict = {
                "type": type(msg).__name__,
                "timestamp": datetime.now().isoformat(),
                "content": str(msg)[:500],  # Truncar
            }
            history.append(msg_dict)

        # Salvar em arquivo
        with open("conversation_history.json", "w") as f:
            json.dump(history, f, indent=2)

        return history
```

## Quando Pedir Ajuda

Se ainda está com problemas:

1. ✅ Verifique a versão do SDK: `pip show claude-agent-sdk`
2. ✅ Leia os logs com `logging.DEBUG`
3. ✅ Teste com exemplo mínimo (eliminar variáveis)
4. ✅ Verifique issues no GitHub: https://github.com/anthropics/claude-agent-sdk
5. ✅ Inclua: Python version, SDK version, código mínimo reproduzível, erro completo

## Ver Também

- `01_CONCEITOS_FUNDAMENTAIS.md` - Introdução
- `02_CLAUDESDKCLIENT_COMPLETO.md` - API
- `06_PADROES_USO.md` - Best practices
- README.md - Início rápido
