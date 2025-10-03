# 🧪 Exemplos de Mensagens para Testar

## 📝 Testes Básicos

### **1. Saudação**
```
Olá! Como você funciona?
```
**Esperado:** Resposta explicando que usa Claude SDK com streaming

### **2. Pergunta Simples**
```
Qual é a capital da França?
```
**Esperado:** "Paris" (resposta curta e direta)

### **3. Lista**
```
Liste 5 linguagens de programação populares
```
**Esperado:** Lista em markdown com bullets

## 💻 Testes de Código

### **4. Python Básico**
```
Escreva código Python para ler um arquivo CSV
```
**Esperado:**
- Código com syntax highlighting
- Botão "📋 Copiar" aparece
- Cores bonitas (azul, verde, amarelo)

### **5. JavaScript**
```
Mostre código JavaScript para fazer uma requisição HTTP
```
**Esperado:**
- Syntax highlighting de JS
- Uso de fetch() ou axios
- Código copiável

### **6. Multiple Code Blocks**
```
Mostre exemplos de código em Python, JavaScript e SQL
```
**Esperado:**
- 3 blocos de código diferentes
- Cada um com highlighting correto
- Cada um com botão de copiar

## 🎨 Testes de Markdown

### **7. Markdown Completo**
```
Escreva um tutorial markdown com:
- Negrito
- Itálico
- Lista numerada
- Lista não-numerada
- Código inline
- Bloco de código
- Links
```
**Esperado:** Tudo formatado corretamente

### **8. Tabela**
```
Crie uma tabela comparando Python vs JavaScript
```
**Esperado:** Tabela formatada em markdown

### **9. Headers**
```
Escreva uma estrutura de documento com títulos H1, H2 e H3
```
**Esperado:** Headers com tamanhos diferentes

## ⚡ Testes de Streaming

### **10. Texto Longo**
```
Conte uma história de 200 palavras sobre um robô que aprende a programar
```
**Esperado:**
- Palavras aparecem uma por uma
- Efeito typewriter visível
- Smooth scrolling automático

### **11. Código Longo**
```
Escreva uma classe Python completa para gerenciar usuários com CRUD
```
**Esperado:**
- Código aparece linha por linha
- Syntax highlighting atualiza em tempo real
- Auto-scroll acompanha o texto

### **12. Explicação Técnica**
```
Explique como funciona async/await em Python com exemplos
```
**Esperado:**
- Texto explicativo
- Exemplos de código
- Streaming smooth

## 🔥 Testes Avançados

### **13. Multi-Turn (Contexto)**
```
Mensagem 1: "Explique o que é FastAPI"
Mensagem 2: "Agora mostre um exemplo de rota POST"
Mensagem 3: "Adicione validação com Pydantic"
```
**Esperado:** Claude mantém contexto entre mensagens

### **14. Thinking Block (se disponível)**
```
Resolva este problema complexo: Como implementar cache distribuído com Redis?
```
**Esperado:**
- Bloco de "thinking" pode aparecer
- Explicação detalhada depois

### **15. Error Recovery**
```
(Desconectar WiFi)
Enviar: "teste durante desconexão"
(Reconectar WiFi)
```
**Esperado:**
- Mensagem de erro aparece
- WebSocket reconecta automaticamente (3s)
- Status volta para 🟢 Conectado

## 💰 Testes de Cost Tracking

### **16. Custo Simples**
```
Oi
```
**Esperado:** Custo ~$0.003-0.005

### **17. Custo Médio**
```
Escreva código Python para criar servidor HTTP
```
**Esperado:** Custo ~$0.01-0.02

### **18. Custo Alto**
```
Escreva documentação completa para uma API REST com 10 endpoints
```
**Esperado:** Custo ~$0.05-0.10

## 📱 Testes Responsivos

### **19. Mobile View**
```
(Redimensionar janela para mobile: 375px width)
Enviar qualquer mensagem
```
**Esperado:**
- Layout adapta para mobile
- Mensagens ocupam 95% da largura
- Botões são clicáveis

### **20. Tablet View**
```
(Redimensionar para tablet: 768px width)
Enviar mensagem
```
**Esperado:** Layout intermediário funciona

## 🎬 Para Demonstração no Vídeo

### **Sequência Sugerida:**

```
1. "Olá! Você funciona com streaming?"
   → Mostrar efeito typewriter

2. "Escreva código Python para criar uma API REST com FastAPI"
   → Mostrar syntax highlighting

3. (Clicar em copiar código)
   → Mostrar "✅ Copiado!"

4. "Agora adicione autenticação JWT nessa API"
   → Mostrar que mantém contexto

5. (Scroll até o topo)
   → Mostrar histórico completo

6. (Mostrar custo)
   → "$0.0XXX acumulado"
```

## 🔬 Testes de Stress (Opcional)

### **21. Mensagens Simultâneas**
```
Enviar 5 mensagens rápidas seguidas
```
**Esperado:** Todas processadas corretamente em ordem

### **22. Texto Muito Longo**
```
Escreva um artigo de 1000 palavras sobre inteligência artificial
```
**Esperado:**
- Streaming continua funcionando
- Não trava
- Scroll automático funciona

### **23. Múltiplos Code Blocks**
```
Mostre 10 exemplos de código diferentes em Python
```
**Esperado:**
- Todos renderizados corretamente
- Todos com botão copiar
- Performance OK

## ✅ Checklist de Validação

Antes de gravar o vídeo, verificar:

- [ ] **Status:** 🟢 Conectado (não ⚫ Desconectado)
- [ ] **Streaming:** Texto aparece gradualmente
- [ ] **Markdown:** Negrito, itálico, listas renderizam
- [ ] **Code:** Syntax highlighting funciona
- [ ] **Copy:** Botão copiar código funciona
- [ ] **Custo:** Aparece e atualiza
- [ ] **Scroll:** Auto-scroll funciona
- [ ] **Responsive:** Funciona em tamanhos diferentes
- [ ] **Reconnect:** Reconecta se desconectar
- [ ] **Multi-turn:** Mantém contexto

## 🚨 Solução de Problemas Durante Demo

### **Se status ficar ⚫ Desconectado:**
```bash
# Reiniciar backend
Ctrl+C (no terminal do servidor)
./start.sh
```

### **Se WebSocket não conectar:**
```bash
# Verificar se porta está livre
lsof -i :8000
kill -9 [PID]  # Se necessário
./start.sh
```

### **Se frontend não carregar:**
```bash
# Reabrir frontend
open frontend/index.html

# Ou com servidor local
cd frontend && python -m http.server 3000
```

## 🎬 Frases para o Vídeo

### **Abertura:**
```
"Vou te mostrar Claude Code Agent criando
um chat COMPLETO sozinho.

Não é teoria. É PRÁTICA.

Vem comigo!"
```

### **Durante testes:**
```
"Olha isso rodando...
[mostrar streaming]

Palavras aparecendo em tempo real.
Syntax highlighting automático.
Interface profissional.

TUDO criado pelo Claude Code."
```

### **Fechamento:**
```
"450+ linhas de código.
10+ features.
12/12 testes passando.
0 bugs.

Tempo do Claude Code: 20 minutos.
Tempo manual: 3-4 HORAS.

Isso é produtividade 10x! 🚀"
```

---

**Bora gravar esse vídeo!** 🎥🔥
