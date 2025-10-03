# 📋 Queue Manager - Explicação Simples

## 🎯 O que é?

**Queue Manager** = **Gerente de Projetos** da sua equipe de agents.

## 💼 Analogia: Gerente de Projetos Real

### Sem Queue Manager:
```
Você → Agent 1: "Faz isso agora!"
Você → Agent 2: "Faz aquilo agora!"
Você → Agent 3: "Espera, faz isso primeiro!"

😓 Você gerenciando tudo manualmente
⏰ Tarefas desorganizadas
❌ Sem priorização
```

### Com Queue Manager:
```
Você → Queue Manager: "Tenho 10 tarefas"
Queue Manager → Organiza por prioridade
Queue Manager → Despacha para agents disponíveis
Queue Manager → Monitora execução

😌 Você delega e relaxa
✅ Tarefas organizadas
🎯 Prioridades respeitadas
```

---

## 🏢 Como Funciona na Prática

### Cenário Real:

```python
# Você joga 10 ideias de vídeo na fila:
queue/tasks/
├─ ideia_1.json  (priority: 1 - URGENTE)
├─ ideia_2.json  (priority: 5 - NORMAL)
├─ ideia_3.json  (priority: 1 - URGENTE)
├─ ideia_4.json  (priority: 10 - BAIXA)
├─ ...
```

**Queue Manager trabalha sozinho:**

```
⏰ 09:00 - Detecta 10 arquivos novos na fila
📊 09:00 - Ordena por prioridade: 1, 1, 5, 5, 10...
▶️  09:01 - Despacha ideia_1 (priority 1) → Validator Agent
▶️  09:01 - Despacha ideia_3 (priority 1) → Creator Agent
⏳ 09:02 - Aguarda agents finalizarem
✅ 09:02 - ideia_1 concluída
▶️  09:02 - Despacha ideia_2 (priority 5) → Validator Agent
✅ 09:03 - ideia_3 concluída
▶️  09:03 - Despacha ideia_5 (priority 5) → Creator Agent
...
✅ 09:10 - Todas as 10 ideias processadas!
```

---

## 🔄 O que o Queue Manager faz

### 1️⃣ **Monitora Continuamente**
```python
while sistema_rodando:
    # A cada 2 segundos
    verificar_fila()
    processar_novos_arquivos()
    sleep(2)
```

**Analogia:** Gerente checando o Trello a cada 2 segundos

---

### 2️⃣ **Prioriza Tarefas**
```python
tarefas = [
    Task(priority=10),  # Baixa
    Task(priority=1),   # Alta ← ESSA VAI PRIMEIRO!
    Task(priority=5),   # Normal
]

queue_manager.ordenar()
# Resultado: [1, 5, 10]
```

**Analogia:** Gerente falando "Isso é urgente, faz primeiro!"

---

### 3️⃣ **Despacha para Agents Disponíveis**
```python
# Max 3 agents em paralelo
agents_livres = 3

# Despacha até encher
while agents_livres > 0 and tem_tarefas:
    agent = pegar_proximo_agent_livre()
    tarefa = pegar_proxima_tarefa()
    agent.executar(tarefa)
    agents_livres -= 1
```

**Analogia:** Gerente distribuindo tasks pro time

---

### 4️⃣ **Detecta Arquivos Automaticamente**
```python
# Você cria arquivo:
echo '{"type": "validator", "ideia": "teste"}' > queue/tasks/task_1.json

# Queue Manager detecta SOZINHO (2s depois):
"📄 Novo arquivo detectado: task_1.json"
"📥 Adicionando à fila..."
"▶️  Despachando para Validator Agent..."
```

**Analogia:** Gerente checando pasta "Inbox" constantemente

---

## 📊 Exemplo Visual

```
FILA DE TAREFAS (queue/tasks/)
┌─────────────────────────────────────┐
│ 🔴 [1] Validar: "hooks security"    │ ← URGENTE
│ 🔴 [1] Validar: "streaming errors"  │ ← URGENTE
│ 🟡 [5] Criar: "multi-agents"        │ ← NORMAL
│ 🟡 [5] Criar: "performance"         │ ← NORMAL
│ 🟢 [10] Pesquisar: "contexto"       │ ← BAIXA
└─────────────────────────────────────┘
         │
         ▼
  QUEUE MANAGER
  ├─ Ordena por priority
  ├─ Monitora agents disponíveis
  └─ Despacha tarefas
         │
         ▼
┌──────────────────────┐
│ 3 AGENTS TRABALHANDO │
├──────────────────────┤
│ Agent 1: Task [1]    │ ✅
│ Agent 2: Task [1]    │ ⏳
│ Agent 3: Task [5]    │ ⏳
│                      │
│ Aguardando: [5, 10]  │
└──────────────────────┘
```

---

## 💡 Por que é Importante?

### ❌ Sem Queue Manager:
```
- Você executa 1 tarefa por vez
- Ordem aleatória
- Sem priorização
- Manual

⏰ 10 tarefas = 3 horas
```

### ✅ Com Queue Manager:
```
- 5 tarefas em paralelo
- Ordem por prioridade
- Automático 24/7
- Detecta automaticamente

⏰ 10 tarefas = 30 minutos
```

**Ganho: 6x mais rápido!**

---

## 🔧 Como Adicionar Tarefas

### Opção 1: Via Python
```python
system = AutonomousSystem()

await system.add_task(
    task_type="validator",
    input_data={"ideia": "hooks security"},
    priority=1  # URGENTE
)
```

### Opção 2: Via Arquivo JSON
```bash
# Criar arquivo na fila
echo '{
  "type": "validator",
  "input_data": {"ideia": "streaming errors"},
  "priority": 1
}' > queue/tasks/task_urgente.json

# Queue Manager detecta AUTOMATICAMENTE em 2s!
```

### Opção 3: Via API (futuro)
```bash
curl -X POST http://localhost:8000/tasks \
  -d '{"type": "validator", "ideia": "multi-agents", "priority": 5}'
```

---

## 🎭 Analogia Completa

**Queue Manager = Gerente de Projetos que:**

✅ **Monitora:** Inbox de tarefas a cada 2 segundos
✅ **Organiza:** Prioriza por urgência (1=alta, 10=baixa)
✅ **Distribui:** Despacha para agents disponíveis
✅ **Controla:** Max 5 agents em paralelo (configurável)
✅ **Reporta:** Status a cada 30 segundos
✅ **Nunca dorme:** Trabalha 24/7

---

## 📝 No Seu Sistema

**Localização:** `src/autonomous_system.py` (linhas 128-156)

**Funcionalidades:**
- 👀 Monitora `queue/tasks/` a cada 2 segundos
- 📄 Detecta arquivos `.json` novos
- 📥 Adiciona automaticamente ao orchestrator
- 🎯 Respeita prioridades
- ♾️ Loop infinito até você parar

**Uso:**
```python
# Adicionar 100 tarefas
for ideia in ideias:
    await system.add_task("validator", {"ideia": ideia})

# Queue Manager processa TUDO sozinho
await system.start()  # Roda até você parar
```

---

## 🎯 Resumo em 3 Palavras

**Gerente. Organiza. Automaticamente.** 🚀