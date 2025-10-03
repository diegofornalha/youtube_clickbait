# 🛡️ Sistema de Permissões e Segurança

## Permission Modes

```python
PermissionMode = Literal[
    "default",            # Pede permissão para tools perigosas
    "acceptEdits",        # Auto-aceita edições de arquivo
    "plan",               # Modo planejamento (sem executar)
    "bypassPermissions"   # Permite tudo (⚠️ perigoso)
]
```

## Configurar Modo de Permissão

### **Via ClaudeAgentOptions:**

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

# Modo seguro (padrão)
options = ClaudeAgentOptions(permission_mode="default")

# Auto-aceita edições
options = ClaudeAgentOptions(permission_mode="acceptEdits")

# Permite tudo (cuidado!)
options = ClaudeAgentOptions(permission_mode="bypassPermissions")

async with ClaudeSDKClient(options=options) as client:
    await client.query("...")
```

### **Mudar Durante Conversa:**

```python
async with ClaudeSDKClient() as client:
    # Começa em modo seguro
    await client.query("Analise este código")

    # Análise concluída, aceitar edições
    await client.set_permission_mode("acceptEdits")
    await client.query("Agora conserte os bugs")

    # Voltar ao modo seguro
    await client.set_permission_mode("default")
```

## Sistema can_use_tool

**Controle programático** de permissões via callback.

### **Anatomia:**

```python
from claude_agent_sdk import (
    CanUseTool,
    ToolPermissionContext,
    PermissionResult,
    PermissionResultAllow,
    PermissionResultDeny,
)

async def my_permission_callback(
    tool_name: str,                    # Nome da ferramenta
    tool_input: dict[str, Any],        # Input da ferramenta
    context: ToolPermissionContext     # Contexto
) -> PermissionResult:                 # Allow ou Deny

    # Decidir se permitir
    if tool_name == "Read":
        return PermissionResultAllow()  # Permitir

    if tool_name == "Bash" and "rm" in str(tool_input):
        return PermissionResultDeny(
            message="⚠️ Comando rm bloqueado",
            interrupt=False  # Não interromper conversa
        )

    # Permitir por padrão
    return PermissionResultAllow()
```

### **Configurar:**

```python
options = ClaudeAgentOptions(
    can_use_tool=my_permission_callback
)

async with ClaudeSDKClient(options=options) as client:
    # Callback será chamado antes de CADA ferramenta
    await client.query("Delete todos os arquivos")
    # Se callback bloquear, Claude receberá erro
```

## PermissionResultAllow - Permitir Ferramenta

```python
from claude_agent_sdk import PermissionResultAllow

# Permitir sem modificações
return PermissionResultAllow()

# Permitir mas modificar input
return PermissionResultAllow(
    updated_input={
        "command": "ls -la",  # Substitui comando original
    }
)

# Permitir e atualizar permissões permanentemente
return PermissionResultAllow(
    updated_permissions=[
        PermissionUpdate(
            type="addRules",
            behavior="allow",
            rules=[PermissionRuleValue(tool_name="Bash")]
        )
    ]
)
```

## PermissionResultDeny - Bloquear Ferramenta

```python
from claude_agent_sdk import PermissionResultDeny

# Bloquear com mensagem
return PermissionResultDeny(
    message="❌ Ferramenta não permitida",
    interrupt=False  # Conversa continua
)

# Bloquear e interromper conversa
return PermissionResultDeny(
    message="❌ Operação perigosa detectada!",
    interrupt=True  # Para conversa imediatamente
)
```

## PermissionUpdate - Atualizar Regras

```python
from claude_agent_sdk import PermissionUpdate, PermissionRuleValue

# Adicionar regra
update = PermissionUpdate(
    type="addRules",
    behavior="allow",
    rules=[
        PermissionRuleValue(tool_name="Bash", rule_content="ls|pwd|echo")
    ],
    destination="session"  # Ou "userSettings", "projectSettings"
)

# Remover regras
update = PermissionUpdate(
    type="removeRules",
    rules=[PermissionRuleValue(tool_name="Bash")]
)

# Mudar modo
update = PermissionUpdate(
    type="setMode",
    mode="acceptEdits"
)

# Adicionar diretórios permitidos
update = PermissionUpdate(
    type="addDirectories",
    directories=["/safe/path"]
)
```

## Exemplos Práticos

### **Exemplo 1: Whitelist de Comandos Bash**

```python
ALLOWED_BASH_COMMANDS = ["ls", "pwd", "echo", "cat", "grep", "find"]

async def whitelist_bash(tool_name, tool_input, context):
    """Só permite comandos na whitelist."""
    if tool_name != "Bash":
        return PermissionResultAllow()

    command = tool_input.get("command", "")

    # Extrair primeiro comando
    first_cmd = command.split()[0] if command else ""

    if first_cmd not in ALLOWED_BASH_COMMANDS:
        return PermissionResultDeny(
            message=f"❌ Comando '{first_cmd}' não está na whitelist",
            interrupt=False
        )

    return PermissionResultAllow()
```

### **Exemplo 2: Proteção de Arquivos Críticos**

```python
PROTECTED_FILES = [".env", "secrets.json", "credentials.yaml"]
PROTECTED_DIRS = [".git", ".ssh", "node_modules"]

async def protect_critical_files(tool_name, tool_input, context):
    """Protege arquivos e diretórios críticos."""
    if tool_name not in ["Write", "Edit", "Bash"]:
        return PermissionResultAllow()

    # Verificar file_path
    file_path = tool_input.get("file_path", "")

    # Proteger arquivos específicos
    for protected in PROTECTED_FILES:
        if protected in file_path:
            return PermissionResultDeny(
                message=f"🔒 Arquivo protegido: {protected}",
                interrupt=False
            )

    # Proteger diretórios
    for protected_dir in PROTECTED_DIRS:
        if f"/{protected_dir}/" in file_path or file_path.startswith(protected_dir):
            return PermissionResultDeny(
                message=f"🔒 Diretório protegido: {protected_dir}",
                interrupt=False
            )

    return PermissionResultAllow()
```

### **Exemplo 3: Rate Limiting**

```python
from datetime import datetime, timedelta
from collections import defaultdict

tool_call_history = defaultdict(list)

async def rate_limit_tools(tool_name, tool_input, context):
    """Limita chamadas por ferramenta."""
    now = datetime.now()

    # Limpar histórico antigo (>1 minuto)
    tool_call_history[tool_name] = [
        t for t in tool_call_history[tool_name]
        if now - t < timedelta(minutes=1)
    ]

    # Limites por ferramenta
    limits = {
        "Bash": 20,        # 20 comandos/minuto
        "WebFetch": 5,     # 5 requests/minuto
        "Write": 10,       # 10 writes/minuto
    }

    limit = limits.get(tool_name, 100)  # Padrão: 100/minuto

    if len(tool_call_history[tool_name]) >= limit:
        return PermissionResultDeny(
            message=f"⚠️ Rate limit: máximo {limit} {tool_name}/minuto",
            interrupt=False
        )

    # Registrar chamada
    tool_call_history[tool_name].append(now)

    return PermissionResultAllow()
```

### **Exemplo 4: Modificar Inputs Automaticamente**

```python
async def sanitize_bash_commands(tool_name, tool_input, context):
    """Remove flags perigosas de comandos Bash."""
    if tool_name != "Bash":
        return PermissionResultAllow()

    command = tool_input.get("command", "")

    # Remover flags perigosas
    dangerous_flags = ["--no-preserve-root", "-f", "--force"]

    modified_command = command
    for flag in dangerous_flags:
        if flag in modified_command:
            modified_command = modified_command.replace(flag, "")
            print(f"⚠️ Flag perigosa removida: {flag}")

    if modified_command != command:
        return PermissionResultAllow(
            updated_input={"command": modified_command.strip()}
        )

    return PermissionResultAllow()
```

### **Exemplo 5: Audit Log Completo**

```python
import json
from datetime import datetime

async def audit_all_tools(tool_name, tool_input, context):
    """Loga TODAS as tentativas de uso de ferramenta."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool_name": tool_name,
        "input": str(tool_input)[:500],  # Truncar
        "decision": "pending",
    }

    # Decisão de permissão
    if tool_name == "Bash" and "rm" in str(tool_input):
        log_entry["decision"] = "denied"
        decision = PermissionResultDeny(message="Comando rm bloqueado")
    else:
        log_entry["decision"] = "allowed"
        decision = PermissionResultAllow()

    # Salvar log
    with open("audit.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return decision
```

## ToolPermissionContext

```python
@dataclass
class ToolPermissionContext:
    signal: Any | None = None
    suggestions: list[PermissionUpdate] = field(default_factory=list)
```

**`suggestions`** - Sugestões de permissão do CLI:

```python
async def use_suggestions(tool_name, tool_input, context):
    """Usa sugestões do CLI para atualizar permissões."""

    # CLI pode sugerir adicionar regra
    if context.suggestions:
        print(f"💡 CLI sugeriu {len(context.suggestions)} mudanças de permissão")

        # Auto-aceitar sugestões do CLI
        return PermissionResultAllow(
            updated_permissions=context.suggestions
        )

    return PermissionResultAllow()
```

## Allowed vs Disallowed Tools

### **Whitelist (allowed_tools):**

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Bash"]  # APENAS essas
)

# Claude só pode usar Read, Grep, Bash
# Qualquer outra ferramenta será negada
```

### **Blacklist (disallowed_tools):**

```python
options = ClaudeAgentOptions(
    disallowed_tools=["SlashCommand", "KillShell"]  # PROIBIDAS
)

# Claude pode usar todas EXCETO essas
```

### **Combinar:**

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Grep", "Bash"],
    disallowed_tools=["Write"]  # Write na allowed mas denied = nega
)

# Resultado: Read, Grep, Bash permitidos
# Write negado (disallowed tem prioridade)
```

## Estratégias de Segurança

### **Estratégia 1: Ambientes Sandbox**

```python
import os

options = ClaudeAgentOptions(
    cwd="/safe/sandbox",  # Diretório isolado
    permission_mode="bypassPermissions",  # Liberado dentro do sandbox
    env={"HOME": "/safe/sandbox"}  # Env isolado
)
```

### **Estratégia 2: Progressiva**

```python
async with ClaudeSDKClient() as client:
    # Fase 1: Análise (modo seguro)
    await client.query("Analise este código e sugira melhorias")

    async for msg in client.receive_response():
        # Revisar sugestões
        pass

    # Fase 2: Implementação (auto-aceitar edições)
    await client.set_permission_mode("acceptEdits")
    await client.query("Implemente as melhorias que sugeriu")

    # Fase 3: Validação (volta ao seguro)
    await client.set_permission_mode("default")
    await client.query("Rode os testes")
```

### **Estratégia 3: Baseada em Confiança**

```python
trust_score = 100  # Começa com 100% de confiança

async def trust_based_permissions(tool_name, tool_input, context):
    """Permissões baseadas em score de confiança."""
    global trust_score

    # Tools sempre permitidas
    if tool_name in ["Read", "Grep", "Glob"]:
        return PermissionResultAllow()

    # Tools perigosas precisam alta confiança
    if tool_name in ["Bash", "Write", "Edit"]:
        if trust_score < 50:
            trust_score -= 10  # Penalizar tentativa
            return PermissionResultDeny(
                message=f"⚠️ Confiança muito baixa ({trust_score}%)",
                interrupt=False
            )

        # Permitir mas reduzir confiança
        trust_score -= 5

    return PermissionResultAllow()

# Hook PostToolUse para restaurar confiança
async def restore_trust_on_success(input_data, tool_use_id, context):
    """Aumenta confiança se ferramenta funcionar."""
    global trust_score

    if not input_data.get("is_error", False):
        trust_score = min(100, trust_score + 2)  # +2% por sucesso

    return {}
```

## Exemplos Avançados

### **Exemplo 1: DryRun Mode**

```python
dry_run = True

async def dry_run_mode(tool_name, tool_input, context):
    """Modo dry-run: simula sem executar."""
    if not dry_run:
        return PermissionResultAllow()

    # Ferramentas de leitura podem executar
    if tool_name in ["Read", "Grep", "Glob", "WebFetch"]:
        return PermissionResultAllow()

    # Ferramentas de escrita são bloqueadas
    if tool_name in ["Write", "Edit", "Bash"]:
        print(f"🔍 [DRY RUN] Bloqueado: {tool_name}")
        print(f"   Input: {tool_input}")

        return PermissionResultDeny(
            message=f"[DRY RUN] {tool_name} bloqueado (modo simulação)",
            interrupt=False
        )

    return PermissionResultAllow()

# Usar
options = ClaudeAgentOptions(can_use_tool=dry_run_mode)

# Desativar dry run
dry_run = False
```

### **Exemplo 2: Aprovação Manual Seletiva**

```python
async def manual_approval_for_critical(tool_name, tool_input, context):
    """Pede aprovação manual para operações críticas."""

    critical_tools = {
        "Bash": ["rm", "mv", "chmod", "chown"],
        "Write": [".env", "config"],
        "Edit": ["package.json", "requirements.txt"]
    }

    if tool_name not in critical_tools:
        return PermissionResultAllow()

    # Verificar se input contém padrão crítico
    tool_input_str = str(tool_input).lower()

    for pattern in critical_tools[tool_name]:
        if pattern in tool_input_str:
            # Pedir aprovação manual
            print(f"\n⚠️  APROVAÇÃO NECESSÁRIA:")
            print(f"   Tool: {tool_name}")
            print(f"   Pattern: {pattern}")
            print(f"   Input: {tool_input}")

            response = input("Permitir? (y/n): ")

            if response.lower() != "y":
                return PermissionResultDeny(
                    message="❌ Negado pelo usuário",
                    interrupt=False
                )

    return PermissionResultAllow()
```

### **Exemplo 3: Budget Control**

```python
total_cost = 0.0
MAX_BUDGET_USD = 1.0  # $1.00 máximo

async def check_budget_on_stop(input_data, tool_use_id, context):
    """Verifica budget ao final de cada conversa."""
    global total_cost

    result = input_data.get("result", {})
    cost = result.get("total_cost_usd", 0.0)

    total_cost += cost

    print(f"💰 Custo desta conversa: ${cost:.4f}")
    print(f"💰 Custo total acumulado: ${total_cost:.4f}")

    if total_cost >= MAX_BUDGET_USD:
        print(f"🚨 BUDGET EXCEDIDO! Máximo: ${MAX_BUDGET_USD}")

    return {}

# Configurar hook no Stop
options = ClaudeAgentOptions(
    hooks={
        "Stop": [HookMatcher(hooks=[check_budget_on_stop])]
    }
)
```

## Integração com can_use_tool + Hooks

**Combine** callback de permissão com hooks para controle total:

```python
# 1. Callback de permissão (antes)
async def permission_callback(tool_name, tool_input, context):
    """Validação inicial."""
    if tool_name == "Bash" and "rm" in str(tool_input):
        return PermissionResultDeny(message="rm bloqueado")
    return PermissionResultAllow()

# 2. Hook PreToolUse (antes, mas depois do callback)
async def pre_hook(input_data, tool_use_id, context):
    """Validação adicional."""
    print(f"🔍 PreToolUse: {input_data.get('tool_name')}")
    return {}

# 3. Hook PostToolUse (depois)
async def post_hook(input_data, tool_use_id, context):
    """Logging após execução."""
    print(f"✅ PostToolUse: {input_data.get('tool_name')}")
    return {}

# Configurar TUDO
options = ClaudeAgentOptions(
    can_use_tool=permission_callback,  # Validação de permissão
    hooks={
        "PreToolUse": [HookMatcher(hooks=[pre_hook])],
        "PostToolUse": [HookMatcher(hooks=[post_hook])],
    }
)
```

**Ordem de execução:**
1. `can_use_tool` callback → Decide se permite
2. `PreToolUse` hook → Validação adicional
3. **Ferramenta executa**
4. `PostToolUse` hook → Logging/cleanup

## Debugging de Permissões

### **Ver sugestões do CLI:**

```python
async def debug_suggestions(tool_name, tool_input, context):
    """Mostra sugestões do CLI."""
    if context.suggestions:
        print(f"💡 CLI sugeriu {len(context.suggestions)} mudanças:")
        for sug in context.suggestions:
            print(f"   - Tipo: {sug.type}")
            print(f"   - Regras: {sug.rules}")

    return PermissionResultAllow()
```

### **Logar todas decisões:**

```python
async def log_all_decisions(tool_name, tool_input, context):
    """Loga todas as decisões de permissão."""
    decision = "allow"  # Decisão padrão

    # Sua lógica aqui
    if tool_name == "Bash":
        decision = "deny"
        result = PermissionResultDeny(message="Bloqueado")
    else:
        result = PermissionResultAllow()

    # Log
    with open("permission_log.txt", "a") as f:
        f.write(f"{datetime.now()} | {tool_name} | {decision}\n")

    return result
```

## Ver Também

- `02_CLAUDESDKCLIENT_COMPLETO.md` - set_permission_mode()
- `03_HOOKS_SISTEMA.md` - Sistema de hooks
- `06_PADROES_USO.md` - Padrões de segurança
- `07_TROUBLESHOOTING.md` - Problemas comuns
