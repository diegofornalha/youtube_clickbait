# /youtube - Gerador de Títulos Virais

Gera títulos virais para vídeos sobre Claude SDK com validação e memória Neo4j.

## Uso

```
/youtube [sua ideia]
```

## Exemplos

```
/youtube streaming do claude sdk
/youtube multi agents com claude
/youtube produtividade com agentes
```

## Workflow Automático

Quando você executar este comando, o sistema irá:

1. **🧠 CONSULTAR NEO4J** - Buscar aprendizados anteriores
2. **📊 VALIDAR IDEIA** - Usar idea_validator agent
3. **🎯 GERAR TÍTULOS** - Criar 10 títulos virais
4. **💾 SALVAR NEO4J** - Criar memórias e conexões
5. **📄 SALVAR ARQUIVO** - Criar .md na Lista de ideias

## Instruções para Claude

Execute o seguinte workflow quando o usuário usar `/youtube [ideia]`:

### ETAPA 1: Consultar Neo4j (OBRIGATÓRIO)
```
1. Buscar contexto: get_context_for_task("Gerar títulos virais sobre {ideia}")
2. Buscar memórias: search_memories("{palavras-chave da ideia}", label="Learning", limit=5)
3. Obter sugestões: suggest_best_approach("Criar título sobre {ideia}")
```

### ETAPA 2: Validar Ideia (OBRIGATÓRIO)
Usar o agente `idea_validator` para analisar a ideia e obter:
- Score (0-10)
- Ângulo recomendado
- Fatores virais
- Views estimadas
- Melhorias sugeridas

### ETAPA 3: Gerar Títulos
Criar 10 títulos virais usando:
- Insights da validação
- Histórico do Neo4j
- Fórmulas comprovadas (do agent video_title_creator.md)
- Gatilhos psicológicos

### ETAPA 4: Salvar no Neo4j (OBRIGATÓRIO)
```
1. create_memory(VideoIdea)
2. create_memory(Title recomendado)
3. create_connection(ideia GENERATED título)
4. create_memory(Topics) + create_connection(ideia ABOUT topics)
5. learn_from_result(tarefa, resultado, success=true)
```

### ETAPA 5: Salvar Arquivo
Criar arquivo em `/Users/2a/Desktop/youtube_clickbait/outputs/Lista de ideias/[TÍTULO].md` com:
```markdown
# [EMOJI] [TÍTULO RECOMENDADO]

**Data**: [HOJE]
**CTR**: X.X/10
**Status**: 📌 Pendente

## Ideia Original
"[IDEIA DO USUÁRIO]"

## 🧠 Insights do Neo4j
- **Memórias Relacionadas**: [memórias encontradas]
- **Aprendizados**: [aprendizados relevantes]
```

## Output Esperado

Mostrar ao usuário:
1. ✅ Título recomendado (com CTR)
2. 📊 Score da validação
3. 🧠 Insights do Neo4j (se houver)
4. 📄 Caminho do arquivo salvo

**Formato de resposta:**
```
🎬 Título Gerado!

🏆 Recomendado (CTR: 9.8/10):
[TÍTULO COM EMOJI]

📊 Validação: Score 8.5/10, Views estimadas: 20K-50K

🧠 Neo4j: Fórmula X funcionou bem em tópicos similares

📄 Salvo em: Lista de ideias/[NOME].md
```

## Regras Importantes

1. ⚠️ **NUNCA** pular a etapa de Neo4j
2. ⚠️ **SEMPRE** validar a ideia primeiro
3. ⚠️ **SEMPRE** salvar no Neo4j E em arquivo
4. ✅ Usar fórmulas de títulos do agent video_title_creator.md
5. ✅ Manter formato minimalista no arquivo .md
6. ✅ Resposta concisa ao usuário (não explicar cada etapa)

## Atalhos

Se o usuário não fornecer ideia:
```
/youtube
→ Perguntar: "Qual é sua ideia de vídeo?"
```

Se a ideia for muito vaga (< 3 palavras):
```
/youtube agents
→ Sugerir: "Pode detalhar? Ex: 'multi agents com claude', 'agents para produtividade'"
```
