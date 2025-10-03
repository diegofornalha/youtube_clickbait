# 🪝 Sistema de Hooks - Referência Completa

## O que são Hooks?

**Hooks** permitem interceptar e modificar o comportamento do Claude Code em pontos específicos da execução.

## Tipos de Hooks

```python
HookEvent = (
    "PreToolUse"           # Antes de usar ferramenta
    | "PostToolUse"        # Depois de usar ferramenta
    | "UserPromptSubmit"   # Quando usuário envia prompt
    | "Stop"               # Quando conversa termina
    | "SubagentStop"       # Quando subagent termina
    | "PreCompact"         # Antes de compactar contexto
)
```

## Anatomia de um Hook

```python
from claude_agent_sdk import HookCallback, HookContext

async def my_hook(
    input_data: dict[str, Any],      # Dados do evento
    tool_use_id: str | None,         # ID da ferramenta (se aplicável)
    context: HookContext             # Contexto da execução
) -> dict[str, Any]:                 # Output do hook
    """Meu hook customizado."""

    # Processar input_data
    tool_name = input_data.get("tool_name", "")

    # Decidir se bloquear
    if tool_name == "Bash" and "rm -rf" in str(input_data):
        return {
            "decision": "block",
            "systemMessage": "⚠️ Comando perigoso bloqueado"
        }

    # Permitir (retornar dict vazio)
    return {}
```

## Hook Matcher

```python
from claude_agent_sdk import HookMatcher

matcher = HookMatcher(
    matcher="Bash|Write|Edit",  # Regex de ferramentas
    hooks=[my_hook, another_hook]  # Lista de callbacks
)
```

### **Sintaxe do Matcher:**

| Matcher | Matches |
|---------|---------|
| `"Bash"` | Apenas ferramenta Bash |
| `"Write\|Edit"` | Write OU Edit |
| `".*"` | Todas ferramentas |
| `None` | Todas (sem filtro) |

## Configurar Hooks

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(
                matcher="Bash",
                hooks=[validate_bash_command]
            )
        ],
        "PostToolUse": [
            HookMatcher(
                matcher="Write|Edit",
                hooks=[log_file_changes]
            )
        ],
        "UserPromptSubmit": [
            HookMatcher(
                matcher=None,  # Sem matcher = sempre executa
                hooks=[validate_user_input]
            )
        ],
    }
)

async with ClaudeSDKClient(options=options) as client:
    # Hooks ativos durante toda a conversação
    await client.query("...")
```

## Tipos de Hooks Detalhados

### **1. PreToolUse** - Antes de Usar Ferramenta

**Quando executado:**
Antes do Claude executar qualquer ferramenta (Read, Write, Bash, etc).

**Input Data:**
```python
{
    "tool_name": "Bash",
    "tool_input": {"command": "ls -la"},
    "tool_use_id": "toolu_abc123"
}
```

**Output Options:**
```python
# Permitir
return {}

# Bloquear
return {
    "decision": "block",
    "systemMessage": "Comando bloqueado por segurança"
}

# Modificar input
return {
    "hookSpecificOutput": {
        "updated_input": {"command": "ls"}  # Modifica comando
    }
}
```

**Exemplo:**
```python
async def validate_bash_commands(input_data, tool_use_id, context):
    """Bloqueia comandos perigosos."""
    if input_data.get("tool_name") == "Bash":
        command = input_data.get("tool_input", {}).get("command", "")

        # Lista de padrões perigosos
        dangerous = ["rm -rf", "dd if=", "mkfs", "> /dev"]

        for pattern in dangerous:
            if pattern in command:
                return {
                    "decision": "block",
                    "systemMessage": f"⚠️ Comando perigoso bloqueado: {pattern}"
                }

    return {}  # Permitir
```

### **2. PostToolUse** - Depois de Usar Ferramenta

**Quando executado:**
Após execução de ferramenta (sucesso ou erro).

**Input Data:**
```python
{
    "tool_name": "Bash",
    "tool_use_id": "toolu_abc123",
    "result": "arquivo1.txt\ndir/",
    "is_error": False
}
```

**Output Options:**
```python
# Apenas logar (não modifica nada)
return {}

# Adicionar mensagem ao sistema
return {
    "systemMessage": "Operação logada com sucesso"
}
```

**Exemplo:**
```python
async def log_operations(input_data, tool_use_id, context):
    """Loga todas as operações em arquivo."""
    import json
    from datetime import datetime

    log_entry = {
        "tool": input_data.get("tool_name"),
        "timestamp": datetime.now().isoformat(),
        "success": not input_data.get("is_error", False),
        "result_size": len(str(input_data.get("result", "")))
    }

    with open("operations.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {}  # Não modifica comportamento
```

### **3. UserPromptSubmit** - Quando Usuário Envia Prompt

**Quando executado:**
Quando um novo prompt do usuário é enviado.

**Input Data:**
```python
{
    "prompt": "Crie um servidor web",
    "session_id": "default"
}
```

**Output Options:**
```python
# Validar e permitir
return {}

# Bloquear prompt
return {
    "decision": "block",
    "systemMessage": "Prompt inválido"
}

# Modificar prompt
return {
    "hookSpecificOutput": {
        "modified_prompt": "Crie um servidor web usando FastAPI"
    }
}
```

**Exemplo:**
```python
async def enhance_prompts(input_data, tool_use_id, context):
    """Adiciona contexto automaticamente aos prompts."""
    prompt = input_data.get("prompt", "")

    # Detectar tipo de tarefa
    if "criar" in prompt.lower() and "web" in prompt.lower():
        enhanced = f"{prompt}\n\nUse FastAPI com async/await e inclua testes."

        return {
            "hookSpecificOutput": {
                "modified_prompt": enhanced
            },
            "systemMessage": "✨ Prompt aprimorado automaticamente"
        }

    return {}
```

### **4. Stop** - Quando Conversa Termina

**Quando executado:**
Ao final de uma conversa (após ResultMessage).

**Input Data:**
```python
{
    "result": {
        "total_cost_usd": 0.0123,
        "num_turns": 5,
        "duration_ms": 12500,
        "session_id": "default"
    }
}
```

**Exemplo:**
```python
async def log_conversation_stats(input_data, tool_use_id, context):
    """Loga estatísticas da conversa."""
    result = input_data.get("result", {})

    print(f"🎯 Conversa finalizada:")
    print(f"  - Custo: ${result.get('total_cost_usd', 0):.4f}")
    print(f"  - Turnos: {result.get('num_turns')}")
    print(f"  - Duração: {result.get('duration_ms')}ms")

    return {}
```

### **5. SubagentStop** - Quando Subagent Termina

**Quando executado:**
Quando um agent filho (Task tool) termina.

**Input Data:**
```python
{
    "subagent_type": "general-purpose",
    "result": {...},
    "success": True
}
```

**Exemplo:**
```python
async def track_subagent_performance(input_data, tool_use_id, context):
    """Rastreia performance de subagents."""
    subagent_type = input_data.get("subagent_type")
    success = input_data.get("success", False)

    # Salvar estatística
    stats[subagent_type]["count"] += 1
    if success:
        stats[subagent_type]["success"] += 1

    return {}
```

### **6. PreCompact** - Antes de Compactar Contexto

**Quando executado:**
Antes do Claude Code compactar o histórico (quando contexto fica muito grande).

**Input Data:**
```python
{
    "message_count": 50,
    "total_tokens": 180000,
    "will_compact": True
}
```

**Exemplo:**
```python
async def save_before_compact(input_data, tool_use_id, context):
    """Salva histórico completo antes de compactar."""
    msg_count = input_data.get("message_count")

    if msg_count > 40:
        # Exportar histórico completo
        await export_conversation_history()

        return {
            "systemMessage": f"📦 {msg_count} mensagens salvas antes de compactação"
        }

    return {}
```

## Hook Output Schema

### **Campos Comuns:**

```python
{
    # Bloquear ação
    "decision": "block",  # Opcional

    # Mensagem de sistema (não visível ao Claude, mas salva no transcript)
    "systemMessage": "Mensagem aqui",  # Opcional

    # Output específico do hook
    "hookSpecificOutput": {
        # Varia por tipo de hook
    }
}
```

### **Hook-Specific Outputs:**

#### **PreToolUse:**
```python
{
    "hookSpecificOutput": {
        "updated_input": {"command": "comando modificado"}
    }
}
```

#### **UserPromptSubmit:**
```python
{
    "hookSpecificOutput": {
        "modified_prompt": "Prompt modificado"
    }
}
```

## Casos de Uso Práticos

### **Caso 1: Auto-aprovação Inteligente**

```python
async def auto_approve_safe_tools(input_data, tool_use_id, context):
    """Auto-aprova ferramentas seguras, pede confirmação para outras."""
    safe_tools = ["Read", "Grep", "Glob", "WebFetch"]
    tool_name = input_data.get("tool_name", "")

    if tool_name in safe_tools:
        return {}  # Permitir automaticamente

    if tool_name in ["Write", "Edit"]:
        # Verificar se é arquivo de teste
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        if "test_" in file_path or "/tests/" in file_path:
            return {}  # Permitir edições em testes

    # Caso contrário, padrão (pedir permissão)
    return {}
```

### **Caso 2: Logging Completo**

```python
import json
from datetime import datetime

async def log_all_operations(input_data, tool_use_id, context):
    """Loga TODAS as operações para auditoria."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": input_data.get("tool_name"),
        "tool_use_id": tool_use_id,
        "input": str(input_data.get("tool_input", ""))[:200],
        "result": str(input_data.get("result", ""))[:500],
        "is_error": input_data.get("is_error", False),
    }

    # Salvar em JSONL
    with open("audit.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {}
```

### **Caso 3: Persistir no Neo4j (Nosso Caso!)**

```python
async def persist_to_neo4j(input_data, tool_use_id, context):
    """Persiste aprendizados no Neo4j após cada operação."""
    import re

    result_str = str(input_data.get("result", ""))

    # Detectar validação concluída
    match = re.search(r'score=(\d+\.\d+)', result_str)
    if match:
        score = float(match.group(1))

        # Chamar ferramenta MCP diretamente
        await context.mcp_call(
            "mcp__neo4j-memory__create_memory",
            {
                "label": "Learning",
                "properties": {
                    "name": f"Validation - score {score}",
                    "category": "execution",
                    "score": score,
                }
            }
        )

    return {}
```

## Múltiplos Hooks na Mesma Ferramenta

```python
async def hook1(input_data, tool_use_id, context):
    print("Hook 1 executado")
    return {}

async def hook2(input_data, tool_use_id, context):
    print("Hook 2 executado")
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(
                matcher="Bash",
                hooks=[hook1, hook2]  # Ambos executam em ordem
            )
        ]
    }
)
```

**Ordem de execução:**
1. hook1 executa
2. hook2 executa
3. Se AMBOS retornarem `{}`, ferramenta executa
4. Se QUALQUER UM retornar `{"decision": "block"}`, ferramenta é bloqueada

## Hooks em Arquivos

Você pode criar hooks em arquivos `.py` no diretório `.claude/hooks/`:

```python
# .claude/hooks/my_hook.py

async def hook(input_data, tool_use_id, context):
    """Hook carregado automaticamente."""
    # Sua lógica aqui
    return {}
```

**Claude Code carrega automaticamente:**
- Arquivos `.py` em `.claude/hooks/`
- Função deve se chamar `hook`
- Arquivo deve ser executável (`chmod +x`)

## Context Object

```python
@dataclass
class HookContext:
    signal: Any | None = None  # Futuro: abort signals
```

**Uso futuro:**
```python
async def my_hook(input_data, tool_use_id, context):
    # Cancelar hook se signal for ativado
    if context.signal and context.signal.is_set():
        return {"decision": "block"}

    return {}
```

## Exemplos Práticos

### **Exemplo 1: Rate Limiting**

```python
from datetime import datetime, timedelta

call_history = []

async def rate_limit_bash(input_data, tool_use_id, context):
    """Limita chamadas Bash a 10 por minuto."""
    if input_data.get("tool_name") != "Bash":
        return {}

    now = datetime.now()

    # Limpar histórico antigo (>1 minuto)
    call_history[:] = [t for t in call_history if now - t < timedelta(minutes=1)]

    if len(call_history) >= 10:
        return {
            "decision": "block",
            "systemMessage": "⚠️ Rate limit: máximo 10 comandos Bash por minuto"
        }

    call_history.append(now)
    return {}
```

### **Exemplo 2: Sanitização de Dados**

```python
async def sanitize_file_writes(input_data, tool_use_id, context):
    """Remove informações sensíveis antes de escrever arquivos."""
    if input_data.get("tool_name") not in ["Write", "Edit"]:
        return {}

    tool_input = input_data.get("tool_input", {})
    content = tool_input.get("content", "")

    # Remover padrões sensíveis
    import re
    sanitized = re.sub(r'API_KEY=\S+', 'API_KEY=***REDACTED***', content)
    sanitized = re.sub(r'password:\s*\S+', 'password: ***', sanitized)

    if sanitized != content:
        return {
            "hookSpecificOutput": {
                "updated_input": {
                    **tool_input,
                    "content": sanitized
                }
            },
            "systemMessage": "🔒 Dados sensíveis removidos do arquivo"
        }

    return {}
```

### **Exemplo 3: Coleta de Métricas**

```python
metrics = {"tool_calls": {}, "errors": 0, "total_duration_ms": 0}

async def collect_metrics_post(input_data, tool_use_id, context):
    """Coleta métricas de performance."""
    tool_name = input_data.get("tool_name", "unknown")
    is_error = input_data.get("is_error", False)

    # Contar chamadas por ferramenta
    metrics["tool_calls"][tool_name] = metrics["tool_calls"].get(tool_name, 0) + 1

    # Contar erros
    if is_error:
        metrics["errors"] += 1

    return {}

async def report_metrics_on_stop(input_data, tool_use_id, context):
    """Reporta métricas ao final da conversa."""
    print("\n📊 Métricas da Conversa:")
    print(f"  - Total de erros: {metrics['errors']}")
    print(f"  - Chamadas por ferramenta:")
    for tool, count in metrics["tool_calls"].items():
        print(f"    - {tool}: {count}x")

    return {}

# Configurar
options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [HookMatcher(hooks=[collect_metrics_post])],
        "Stop": [HookMatcher(hooks=[report_metrics_on_stop])],
    }
)
```

### **Exemplo 4: Auto-Save de Outputs**

```python
async def auto_save_outputs(input_data, tool_use_id, context):
    """Salva outputs importantes automaticamente."""
    tool_name = input_data.get("tool_name", "")
    result = input_data.get("result", "")

    # Salvar outputs de ferramentas específicas
    if tool_name in ["Bash", "WebFetch", "Grep"]:
        from pathlib import Path
        from datetime import datetime

        # Criar diretório
        output_dir = Path(".claude/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Salvar com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{tool_name}_{timestamp}.txt"

        (output_dir / filename).write_text(str(result))

        return {
            "systemMessage": f"💾 Output salvo em {filename}"
        }

    return {}
```

## Debugging de Hooks

### **Verificar se hook está sendo chamado:**

```python
async def debug_hook(input_data, tool_use_id, context):
    """Hook de debug."""
    import json

    print("🔍 HOOK CHAMADO!")
    print(f"  Tool: {input_data.get('tool_name')}")
    print(f"  Input: {json.dumps(input_data, indent=2)[:200]}")

    return {}
```

### **Logar todos os inputs:**

```python
async def log_all_inputs(input_data, tool_use_id, context):
    """Loga TUDO que passa pelo hook."""
    with open("hook_debug.log", "a") as f:
        import json
        f.write(json.dumps(input_data, default=str) + "\n")

    return {}
```

## Limitações

### **⚠️ Hooks não disponíveis no Python SDK:**

- ❌ `SessionStart` - Ao iniciar sessão
- ❌ `SessionEnd` - Ao terminar sessão
- ❌ `Notification` - Notificações gerais

**Motivo:** Limitações de setup do SDK Python.

### **⚠️ Outputs não suportados:**

- ❌ `"continue"` - Não suportado
- ❌ `"stopReason"` - Não suportado
- ❌ `"suppressOutput"` - Não suportado

## Ver Também

- `01_CONCEITOS_FUNDAMENTAIS.md` - Introdução ao SDK
- `02_CLAUDESDKCLIENT_COMPLETO.md` - API do cliente
- `05_PERMISSOES.md` - Sistema de permissões
- `06_PADROES_USO.md` - Padrões com hooks
