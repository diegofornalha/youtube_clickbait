# 🤖 Sistema Autônomo com Claude Agent SDK

Sistema autônomo que usa **agents especializados** e **hooks inteligentes** para processar tarefas de forma independente.

## 🎯 Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA AUTÔNOMO                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Queue      │───▶│ Orchestrator │───▶│   Agents     │  │
│  │  Manager     │    │              │    │  Especial.   │  │
│  └──────────────┘    └──────┬───────┘    └──────────────┘  │
│         │                   │                    │          │
│         │                   ▼                    │          │
│         │            ┌──────────────┐            │          │
│         │            │    Hooks     │            │          │
│         │            │  (Auto-      │            │          │
│         │            │  Approval)   │            │          │
│         │            └──────────────┘            │          │
│         │                   │                    │          │
│         └───────────────────┴────────────────────┘          │
│                             │                               │
│                             ▼                               │
│                      ┌──────────────┐                       │
│                      │    Neo4j     │                       │
│                      │ (Learning &  │                       │
│                      │  Analytics)  │                       │
│                      └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Componentes

### 1. **Queue Manager**
- Monitora fila de tarefas (arquivo, banco, message queue)
- Prioriza tarefas por urgência/importância
- Detecta deadlocks e tarefas travadas

### 2. **Orchestrator**
- Despacha tarefas para agents especializados
- Gerencia ciclo de vida dos agents
- Coordena execução paralela quando possível
- Implementa circuit breaker para falhas

### 3. **Specialized Agents**
- **Validator Agent**: Valida ideias automaticamente
- **Creator Agent**: Gera títulos virais
- **Researcher Agent**: Busca contexto no Neo4j
- **Reporter Agent**: Cria relatórios de resultados

### 4. **Hooks (Auto-Approval)**
- **PreToolUse**: Valida permissões automaticamente
- **PostToolUse**: Registra resultados no Neo4j
- **UserPromptSubmit**: Filtra/enriquece prompts
- **Stop**: Decide se deve continuar ou parar

### 5. **Neo4j Learning**
- Registra padrões de sucesso/falha
- Aprende melhores práticas ao longo do tempo
- Sugere otimizações baseadas em histórico

## 🔄 Fluxo Autônomo

```python
# 1. Nova tarefa chega na fila
task = {
    "type": "generate_titles",
    "input": "streaming do claude sdk",
    "priority": "high"
}

# 2. Orchestrator seleciona agents
orchestrator.process(task)
  ├─ Validator Agent: valida ideia
  ├─ Researcher Agent: busca contexto Neo4j
  └─ Creator Agent: gera títulos

# 3. Hooks automáticos
PreToolUse Hook:
  - Auto-aprova tools seguros (Read, Grep)
  - Bloqueia tools perigosos (Write em paths críticos)

PostToolUse Hook:
  - Registra aprendizado no Neo4j
  - Atualiza métricas de performance

# 4. Resultado salvo automaticamente
output/
  ├─ titulo_gerado.md
  └─ analytics/
      └─ task_123_metrics.json
```

## 🎛️ Configuração

```python
from autonomous_system import AutonomousSystem

# Criar sistema
system = AutonomousSystem(
    queue_path="queue/tasks",
    output_path="outputs",
    neo4j_enabled=True,
    auto_approve_tools=["Read", "Grep", "Bash"],
    max_concurrent_agents=5,
    learning_mode="continuous"
)

# Iniciar monitoramento
await system.start()

# Sistema roda indefinidamente:
# - Processa tarefas da fila
# - Aprende com resultados
# - Self-heals em caso de falhas
```

## 🧠 Auto-Learning

O sistema aprende automaticamente:

1. **Padrões de sucesso**: Quais prompts geram melhores resultados
2. **Configurações ótimas**: Qual system_prompt funciona melhor
3. **Estratégias de retry**: Quando tentar novamente vs. desistir
4. **Detecção de anomalias**: Identifica padrões incomuns

## 🛡️ Self-Healing

- **Circuit Breaker**: Para de usar agents que falham muito
- **Auto-restart**: Reinicia agents travados
- **Fallback Strategies**: Usa alternativas quando falha
- **Rate Limiting**: Previne sobrecarga

## 📊 Monitoramento

Dashboard em tempo real:
```
┌─────────────────────────────────────┐
│  AUTONOMOUS SYSTEM - DASHBOARD      │
├─────────────────────────────────────┤
│  Tasks Processed: 1,234             │
│  Success Rate: 94.5%                │
│  Avg Processing Time: 12.3s         │
│  Active Agents: 3/5                 │
│  Queue Size: 12 tasks               │
│                                     │
│  Agents Status:                     │
│  ✅ Validator: Healthy (152 tasks)  │
│  ✅ Creator: Healthy (148 tasks)    │
│  ⚠️  Researcher: Slow (avg 25s)     │
└─────────────────────────────────────┘
```

## 🚀 Uso

### Modo CLI
```bash
# Iniciar sistema
python -m src.autonomous start

# Adicionar tarefa
python -m src.autonomous task add --type generate_titles --input "hooks do claude"

# Ver status
python -m src.autonomous status

# Ver métricas
python -m src.autonomous metrics --last 24h
```

### Modo Programático
```python
import anyio
from src.autonomous_system import AutonomousSystem

async def main():
    system = AutonomousSystem()

    # Adicionar tarefas
    await system.add_task({
        "type": "generate_titles",
        "input": "multi agents claude"
    })

    # Processar
    await system.start()

anyio.run(main)
```

## 🎯 Casos de Uso

1. **Batch Processing**: Processar 1000 ideias overnight
2. **Continuous Integration**: Validar PRs automaticamente
3. **Content Pipeline**: Gerar títulos → thumbnails → scripts
4. **A/B Testing**: Testar variações de prompts automaticamente
5. **Quality Assurance**: Validar outputs antes de publicar

## 🔐 Segurança

- ✅ Hooks validam todas as operações
- ✅ Whitelist de tools permitidas
- ✅ Rate limiting por agent
- ✅ Logs auditáveis de todas as ações
- ✅ Sandboxing de execução

## 📝 Próximos Passos

1. ✅ Implementar Queue Manager
2. ✅ Criar Orchestrator
3. ✅ Configurar Hooks automáticos
4. ✅ Integrar Neo4j learning
5. ⏳ Dashboard web em tempo real
6. ⏳ API REST para controle externo
