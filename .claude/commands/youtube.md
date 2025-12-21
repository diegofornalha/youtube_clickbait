# /youtube - Títulos Virais Simples

Gera título viral + keywords SEO usando agents e Neo4j.

## Uso

```bash
/youtube [sua ideia]
```

## Workflow (100% Automático)

1. 🧠 **Neo4j** → Buscar aprendizados anteriores
2. ✅ **idea_validator** → Validar potencial viral
3. 🎯 **video_title_creator** → Gerar título otimizado
4. 💾 **Salvar** → Arquivo minimalista em `outputs/`

## Instruções para Claude

Quando o usuário executar `/youtube [ideia]`:

### Passo 1: Consultar Neo4j
```javascript
mcp__neo4j-memory__search_memories("{ideia}")
```

### Passo 2: Validar via Agent
```javascript
Task(subagent_type="idea_validator", prompt="Validar: {ideia}")
```

### Passo 3: Gerar Título via Agent
```javascript
Task(subagent_type="video_title_creator", prompt="Gerar título viral para: {ideia}")
```

### Passo 4: Salvar Arquivo Minimalista

**Caminho**: `outputs/Lista de ideias/[TÍTULO_SLUG].md`

**Template**:
```markdown
# [EMOJI] [TÍTULO VENCEDOR]

**CTR**: X.X/10 | **Score**: X/10 | **Data**: YYYY-MM-DD

## Ideia
"{ideia original}"

## Sugestões
1. [EMOJI] Título opção 1 (CTR: X.X/10)
2. [EMOJI] Título opção 2 (CTR: X.X/10)
3. [EMOJI] Título opção 3 (CTR: X.X/10)

## Keywords
principal, keywords, aqui, separadas, por, virgula

## Hashtags
#tag1 #tag2 #tag3 #tag4 #tag5
```

## Output para Usuário (MINIMALISTA)

```
✅ [TÍTULO COM EMOJI]

CTR: 9.8/10 | Score: 8.5/10
Keywords: keyword1, keyword2, keyword3
📄 outputs/Lista de ideias/titulo-slug.md
```

**Regras**:
- ❌ NÃO explicar cada etapa
- ❌ NÃO mostrar JSON dos agents
- ✅ Apenas resultado final limpo
- ✅ Sempre usar Neo4j + agents
- ✅ Arquivo MD minimalista (< 15 linhas)
