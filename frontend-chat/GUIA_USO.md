# 📖 Guia de Uso - Claude Chat

## 🚀 Início Rápido (30 segundos)

```bash
# 1. Instalar
cd frontend-chat
pip install -r requirements.txt
pip install -e ../claude-agent-sdk-python

# 2. Iniciar
./start.sh

# 3. Abrir
open frontend/index.html
```

Pronto! Chat funcionando! 🎉

## 💬 Usando o Chat

### **Enviar Mensagem:**
1. Digite no campo de input
2. Pressione **Enter** para enviar
3. **Shift+Enter** para nova linha
4. Veja resposta aparecer em tempo real ⚡

### **Navegação Básica:**
- **Scroll automático** acompanha novas mensagens
- **Click para focar** no input
- **Esc** limpa o campo de input

## ⌨️ Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| **Ctrl+K** | Abrir templates de prompts |
| **Ctrl+E** | Exportar conversa em MD |
| **Ctrl+/** | Mostrar lista de atalhos |
| **Ctrl+1/2/3** | Templates rápidos |
| **Ctrl+Shift+C** | Limpar todo o chat |
| **Ctrl+Shift+D** | Toggle debug panel |
| **Ctrl+F** | Buscar mensagens |
| **Escape** | Limpar input / Fechar modais |

## 📋 Copiar Conteúdo

### **Copiar Mensagem Inteira:**
- Click no botão **📋** no header da mensagem do Claude

### **Copiar Code Block:**
- Click no botão **📋 Copiar** acima do código

### **Copiar Múltiplos:**
1. Selecionar texto manualmente
2. **Ctrl+C** normal do navegador

## 📥 Exportar Conversa

### **Método 1: Via Botão**
1. Click em **📥 Exportar MD** no footer
2. Arquivo `.md` baixado automaticamente

### **Método 2: Via Atalho**
1. Pressionar **Ctrl+E**
2. Download automático

### **Conteúdo do Export:**
```markdown
# 💬 Conversa com Claude

**Data:** 2025-10-03T02:15:30
**ID:** 058d5792
**Mensagens:** 10

---

## 👤 Você (02:15)

Olá! Como você funciona?

---

## 🤖 Claude (02:15)

Olá! Eu funciono com streaming real...

---
```

## 📝 Templates de Prompts

### **Ativar Templates:**
- Pressionar **Ctrl+K**

### **Categorias:**
1. **💻 Código** - API REST, Algoritmos, Refatoração, Debug
2. **📚 Documentação** - README, Docstrings, Tutoriais
3. **🔍 Análise** - Code review, Comparações, Arquitetura
4. **🎓 Aprendizado** - Explicações, Exercícios, Roadmaps
5. **⚡ Produtividade** - Scripts, CI/CD, Docker

### **Usar Template:**
1. Abrir com **Ctrl+K**
2. Click no template desejado
3. Prompt aparece no input
4. Editar e enviar

### **Templates Rápidos:**
- **Ctrl+1:** "Explique de forma simples: "
- **Ctrl+2:** "Escreva código Python para: "
- **Ctrl+3:** "Analise este código: "

## 🔍 Buscar nas Conversas

### **Ativar Busca:**
- Pressionar **Ctrl+F**
- Campo de busca aparece no topo

### **Usar:**
1. Digite termo de busca
2. Resultados highlighted em amarelo
3. **Enter** para próximo resultado
4. **Esc** para fechar busca

### **Features da Busca:**
- Busca em tempo real (debounce 300ms)
- Highlight visual dos matches
- Navegação com Enter
- Contador de resultados
- Scroll automático para resultado

## 🔔 Notificações Desktop

### **Ativar:**
1. Click em **🔔 Notificações** no footer
2. Permitir quando navegador pedir

### **Comportamento:**
- Notifica apenas se janela NÃO estiver em foco
- Auto-close após 5s
- Click na notificação = focar janela

### **Desativar:**
- Revogar permissão nas configurações do navegador

## 💾 Autosave

### **Como Funciona:**
- Salva conversa automaticamente a cada **10 segundos**
- Armazena no **localStorage** do navegador
- Válido por **24 horas**

### **Restaurar:**
- Ao abrir chat novamente, aparece prompt:
  ```
  💾 Encontrei uma conversa salva de 2h atrás.
  5 mensagens | $0.0150

  Deseja restaurar?
  ```
- Click **OK** para restaurar
- Click **Cancelar** para nova conversa

### **Limpar Autosave:**
```javascript
// No console do navegador
localStorage.removeItem('claude_chat_conversations')
```

## 🔍 Debug System

### **Ativar:**
```javascript
// Console do navegador
enableDebug()
// Página recarrega com debug ativado
```

### **Features do Debug:**
- **📝 Logs** - Todos os eventos do sistema
- **📊 Métricas** - Performance em tempo real
- **🌐 Network** - Chamadas WebSocket
- **⚡ Performance** - Tempos de resposta

### **Ações:**
- **🗑️ Limpar** - Limpa logs
- **📥 Export** - Baixa logs em JSON
- **📋 Copy** - Copia para clipboard

### **Atalhos:**
- **Ctrl+Shift+D** - Toggle panel

### **Desativar:**
```javascript
disableDebug()
```

## 🏃 Code Runner

### **Executar Python:**
```
Mensagem para Claude:
"Escreva código Python para calcular fibonacci"

Claude responde com código

Click no botão "▶️ Executar" (se disponível)
ou copie e rode localmente
```

### **Via API:**
```bash
curl -X POST http://localhost:8000/execute/code \
  -H "Content-Type: application/json" \
  -d '{"code": "print(2 + 2)", "language": "python"}'
```

### **Segurança:**
- ✅ Sandboxing ativado
- ✅ Módulos limitados
- ✅ Sem acesso a arquivos
- ✅ Timeout de 5s
- ✅ Namespace restrito

## 🧠 Neo4j Integration

### **O que é Salvo:**
- Cada conversa
- Padrões de código detectados
- Tópicos discutidos
- Métricas de performance

### **Verificar Queue:**
```bash
curl http://localhost:8000/neo4j/pending
```

### **Executar Manualmente:**
```bash
# Rodar worker em background
python neo4j_worker.py

# Persiste automaticamente a cada 5s
```

## 🎨 Personalização

### **Mudar Modelo do Claude:**
```python
# backend/server.py linha ~240
options = ClaudeAgentOptions(
    model="claude-opus-4",  # ← Trocar aqui
)
```

### **Mudar System Prompt:**
```python
# backend/server.py linha ~237
system_prompt=(
    "Você é um expert em..."  # ← Customizar
),
```

### **Mudar Cores:**
```css
/* frontend/style.css linha 12 */
:root {
    --primary: #ff6b6b;  /* Vermelho ao invés de roxo */
}
```

### **Ajustar Autosave:**
```javascript
// frontend/autosave.js linha 10
this.saveInterval = 30000; // 30s ao invés de 10s
```

## 🐛 Troubleshooting

### **WebSocket não conecta:**
```bash
# Verificar se backend está rodando
curl http://localhost:8000/
# Deve retornar: {"status":"ok"}
```

### **Streaming não funciona:**
- Recarregar página (F5)
- Verificar console do navegador (F12)
- Verificar logs do backend

### **Erro ao exportar:**
- Certifique-se que enviou ao menos 1 mensagem
- Conversa precisa ter ID válido

### **Debug panel não aparece:**
```javascript
// Ativar debug primeiro
enableDebug()
```

## 📊 Monitoramento

### **Ver Logs do Backend:**
```bash
tail -f /tmp/chat_server.log
```

### **Ver Console do Frontend:**
```
F12 → Console
```

### **Verificar Performance:**
```javascript
// Console
window.performanceMetrics.metrics
// Mostra todas as métricas
```

## 💡 Dicas de Uso

### **Para Produtividade:**
1. Use **Ctrl+K** para templates prontos
2. Use **Ctrl+1/2/3** para templates frequentes
3. Ative **notificações** para trabalhar em background
4. Use **Ctrl+E** para salvar conversas importantes

### **Para Desenvolvimento:**
1. Ative **debug mode** para ver internals
2. Rode **neo4j_worker.py** para persistência
3. Use **code runner** para testar snippets
4. **Export MD** para documentação

### **Para Apresentações:**
1. Abra **fullscreen** (F11)
2. Aumente **zoom** (Ctrl++)
3. Use prompts de **templates** para demo
4. **Screenshot** com Ctrl+Shift+S

## 🎬 Para o Vídeo

### **Sequência de Demo:**

```
1. Abrir chat (já conectado 🟢)
2. Enviar: "Olá! Explique como você funciona"
3. Mostrar: streaming em tempo real
4. Enviar: "Escreva código Python para criar API"
5. Mostrar: syntax highlighting
6. Click: botão copiar código
7. Pressionar: Ctrl+K (templates)
8. Mostrar: 15+ templates prontos
9. Pressionar: Ctrl+E (export)
10. Mostrar: arquivo MD baixado
11. Pressionar: Ctrl+Shift+D (debug)
12. Mostrar: métricas e logs
```

**Tempo de demo:** ~2 minutos
**Impressão:** "WOW, isso é profissional!" 🔥

---

**Criado autonomamente pelo Claude Code Agent** 🤖⚡
