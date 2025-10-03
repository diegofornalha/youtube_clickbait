# 🤖 Guia do Sistema Autônomo

## 📁 Estrutura

```
.claude/
├── agents/                    # Subagents especializados
│   ├── idea_validator.md      # Valida ideias de vídeo
│   └── video_title_creator.md # Gera títulos virais
│
└── hooks/                     # Hooks de controle
    └── auto_approval.json     # Config de auto-aprovação

src/
├── autonomous/
│   ├── orchestrator.py        # Coordena agents
│   └── hooks.py              # Implementação de hooks
│
├── autonomous_system.py       # Sistema principal
├── agent_loader.py           # Carrega agents de .claude/
└── error_handler.py          # Tratamento de erros
```

## 🎯 Como Funciona

### 1. **Agents (.claude/agents/)**

Agents são definidos como arquivos `.md` que o Claude Code carrega automaticamente:

```markdown
# My Custom Agent

**Role**: Descrição do agent

## Workflow
1. Fazer X
2. Fazer Y
3. Retornar resultado
```

**Uso via Python SDK:**
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

options = ClaudeAgentOptions(
    allowed_tools=["Task"],  # Permite invocar subagents
)

async with ClaudeSDKClient(options=options) as client:
    # Claude invoca o agent automaticamente quando mencionar o nome
    await client.query("Use o agent idea_validator para validar: 'minha ideia'")

    async for msg in client.receive_response():
        print(msg)
```

### 2. **Hooks (.claude/hooks/)**

Hooks controlam o comportamento do Claude Code:

**Em Python (via SDK):**
```python
async def auto_approve_hook(input_data, tool_use_id, context):
    tool_name = input_data.get("tool_name")

    # Auto-aprovar Task tool (para subagents)
    if tool_name == "Task":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Task", hooks=[auto_approve_hook])
        ]
    }
)
```

### 3. **Sistema Autônomo Completo**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher

class AutonomousSystem:
    def __init__(self):
        self.hooks = self._setup_hooks()

    def _setup_hooks(self):
        """Configura hooks de auto-aprovação."""
        async def auto_approve(input_data, tool_use_id, context):
            tool_name = input_data.get("tool_name", "")

            # Lista de tools auto-aprovadas
            safe_tools = ["Task", "Read", "Grep", "Glob"]

            if tool_name in safe_tools:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow"
                    }
                }
            return {}

        return {
            "PreToolUse": [HookMatcher(matcher=None, hooks=[auto_approve])]
        }

    async def process_with_agents(self, ideia: str):
        """Processa ideia usando agents de .claude/agents/"""

        options = ClaudeAgentOptions(
            allowed_tools=["Task", "Read", "Grep"],
            hooks=self.hooks,
        )

        async with ClaudeSDKClient(options=options) as client:
            # Claude automaticamente usa agents de .claude/agents/
            prompt = f\"\"\"Execute:
            1. Valide a ideia "{ideia}" com idea_validator
            2. Gere títulos com video_title_creator
            3. Retorne resumo
            \"\"\"

            await client.query(prompt)

            async for msg in client.receive_response():
                # Processar resposta
                pass

# Usar
system = AutonomousSystem()
await system.process_with_agents("streaming do claude sdk")
```

## 🔑 Pontos-Chave

### ✅ Agents são Automáticos
Quando você tem agents em `.claude/agents/`, o Claude Code os carrega automaticamente. Você só precisa:
1. Permitir `Task` tool em `allowed_tools`
2. Mencionar o nome do agent no prompt

### ✅ Hooks Controlam Permissões
- **PreToolUse**: Decide se permite tool ANTES de executar
- **PostToolUse**: Registra/valida DEPOIS de executar
- **Stop**: Decide se continua ou para

### ✅ Orchestrator Coordena
O orchestrator:
- Gerencia fila de tarefas
- Despacha para agents apropriados
- Coleta métricas
- Implementa circuit breaker

## 📋 Workflow Completo

```
Tarefa Nova
    │
    ├──> Queue Manager detecta
    │
    ├──> Orchestrator despacha
    │
    ├──> Hook PreToolUse: auto-aprova Task tool
    │
    ├──> Claude invoca subagent (idea_validator)
    │
    ├──> Subagent executa e retorna resultado
    │
    ├──> Hook PostToolUse: registra no Neo4j
    │
    └──> Resultado final salvo
```

## 🚀 Exemplo Prático

Veja `src/autonomous_v2.py` para implementação completa.

Execute:
```bash
python src/autonomous_v2.py
```

## 📊 Métricas

O sistema coleta automaticamente:
- Número de tasks processadas
- Taxa de sucesso por agent
- Tempo médio de execução
- Auto-aprovações vs bloqueios
- Erros e retries

## 🛡️ Segurança

Hooks garantem:
- ✅ Apenas tools seguras são auto-aprovadas
- ✅ Paths sensíveis são protegidos
- ✅ Comandos perigosos são bloqueados
- ✅ Todas as operações são logadas
