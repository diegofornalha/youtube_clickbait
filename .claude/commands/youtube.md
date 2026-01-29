# /youtube - Gerador de Pacote SEO Completo

Gera pacote completo para YouTube: título viral, descrição, tags, thumbnail e hook.

## Uso

```bash
/youtube [sua ideia]
```

## Instruções para Claude

Quando o usuário executar `/youtube [ideia]`:

### 1. Carregar Skill

Ler a skill `viral-youtube-titles` para contexto completo:
```
.claude/skills/viral-youtube-titles/SKILL.md
```

### 2. Consultar Neo4j

```javascript
mcp__neo4j-memory__search_memories("{ideia}")
```

### 3. Validar Ideia (Score 0-10)

Aplicar critérios de `references/scoring_criteria.md`

### 4. Gerar Pacote SEO Completo

Seguir template da SKILL.md:
- 3 variações de título (fórmulas diferentes)
- Descrição com timestamps
- Tags (máx 500 chars)
- Sugestão de thumbnail
- Script do hook (30s)

### 5. Salvar Arquivo

**Caminho**: `outputs/Lista de ideias/[TÍTULO_SLUG].md`

Usar template SEO Completo da SKILL.md

### 6. Persistir no Neo4j

```javascript
mcp__neo4j-memory__create_entities([...])
```

## Output para Usuário

```
✅ Pacote SEO gerado!

Título: [TÍTULO VENCEDOR]
Score: 8.5/10 | CTR: 9.5/10

📄 outputs/Lista de ideias/[slug].md
```

## Regras

- ❌ NÃO mostrar conteúdo completo do arquivo
- ❌ NÃO explicar cada etapa
- ✅ Apenas confirmação + título + path
- ✅ Usuário abre arquivo para copiar seções
