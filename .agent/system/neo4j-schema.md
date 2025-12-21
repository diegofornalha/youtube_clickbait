# Neo4j Schema - YouTube Clickbait Generator

## Configuração de Conexão

```
URL: bolt://localhost:7687
Database: neo4j
Usuário: neo4j
Senha: password
```

## Modelo de Dados

### Entidades (Nodes)

#### VideoIdeia (Label: Learning)
```cypher
{
  name: "VideoIdeia:[nome_único]",  // Identificador único
  type: "video_idea",
  observations: [
    "Ideia original: [texto]",
    "Score de validação: X.X/10",
    "Views estimadas: XK-XK",
    "Público-alvo: [descrição]",
    "Janela de oportunidade: [timeframe]",
    "Data criação: YYYY-MM-DD"
  ]
}
```

#### TítuloViral (Label: Learning)
```cypher
{
  name: "TítuloViral:[título_truncado]",
  type: "video_title",
  observations: [
    "Título completo: [texto]",
    "CTR Score: X.X/10",
    "Fórmula: [nome_fórmula]",
    "Gatilhos: [lista]",
    "Keywords principais: [lista]",
    "Arquivo salvo: [path]"
  ]
}
```

#### FormulaViral (Label: Learning)
```cypher
{
  name: "Formula:[nome]",
  type: "title_formula",
  observations: [
    "Pattern: [estrutura]",
    "Exemplos: [lista]",
    "CTR médio: X.X",
    "Melhor para: [casos_uso]"
  ]
}
```

### Relacionamentos (Relationships)

```cypher
// Ideia gera títulos
(VideoIdeia)-[:GENERATED]->(TítuloViral)

// Título usa fórmula
(TítuloViral)-[:USES_FORMULA]->(FormulaViral)

// Ideia relacionada com outra
(VideoIdeia)-[:RELATED_TO]->(VideoIdeia)

// Título deriva de outro
(TítuloViral)-[:DERIVED_FROM]->(TítuloViral)
```

## Queries Úteis

### Buscar ideias por score
```cypher
MATCH (n:Learning {type: "video_idea"})
WHERE n.observations =~ ".*Score.*[8-9]\\.[0-9].*"
RETURN n
ORDER BY n.name DESC
LIMIT 10
```

### Títulos com melhor CTR
```cypher
MATCH (t:Learning {type: "video_title"})
WHERE t.observations =~ ".*CTR.*9\\.[5-9].*"
RETURN t.name, t.observations
ORDER BY t.name DESC
```

### Fórmulas mais usadas
```cypher
MATCH (f:Learning {type: "title_formula"})<-[:USES_FORMULA]-(t)
RETURN f.name, COUNT(t) as uses
ORDER BY uses DESC
```

### Ideias sem títulos gerados
```cypher
MATCH (i:Learning {type: "video_idea"})
WHERE NOT (i)-[:GENERATED]->()
RETURN i
```

## Comandos MCP

### Criar entidades
```python
mcp__neo4j-memory__create_entities({
  "entities": [{
    "name": "VideoIdeia:Nome",
    "type": "video_idea",
    "observations": [...]
  }]
})
```

### Buscar memórias
```python
mcp__neo4j-memory__search_memories(
  "claude code tutorial viral"
)
```

### Criar relações
```python
mcp__neo4j-memory__create_relations({
  "relations": [{
    "source": "VideoIdeia:X",
    "target": "TítuloViral:Y",
    "relationType": "GENERATED"
  }]
})
```

## Manutenção

### Limpeza de duplicatas
```cypher
// Identificar duplicatas
MATCH (n:Learning)
WITH n.name as name, COLLECT(n) as nodes
WHERE SIZE(nodes) > 1
RETURN name, SIZE(nodes) as count
```

### Backup
```bash
# Executar backup
cd /Users/2a/.claude/memoria-neo4j
python3 backup_mcp.py
```

### Estatísticas
```cypher
// Total de entidades
MATCH (n:Learning)
RETURN n.type, COUNT(n) as count
ORDER BY count DESC
```

## Boas Práticas

1. **Sempre use label "Learning"** (nunca "Memory")
2. **Nome único** para cada entidade
3. **Observations** como array de strings
4. **Timestamps** em formato ISO
5. **Scores** como string "X.X/10"

## Troubleshooting

### Conexão recusada
```bash
# Verificar se Neo4j está rodando
neo4j status

# Reiniciar se necessário
neo4j restart
```

### Query lenta
```cypher
// Criar índice para performance
CREATE INDEX ON :Learning(name)
CREATE INDEX ON :Learning(type)
```