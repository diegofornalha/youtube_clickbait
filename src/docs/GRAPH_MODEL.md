# 🧠 Modelo de Grafo - Claude SDK Knowledge Base

## Categorias de Nós (Label: Learning)

### 1. **Padrões de Conteúdo**
```
category: "formula_pattern"
├─ name: "Choque + Número"
├─ pattern: "🚨 [NÚMERO] [COISA] que [AÇÃO]"
├─ avg_ctr: 9.2
└─ usage_count: 15

category: "psychological_trigger"
├─ name: "FOMO"
├─ description: "Medo de perder oportunidade"
└─ effectiveness_score: 8.7

category: "angle_pattern"
├─ name: "comparação técnica"
├─ best_for_topics: "streaming,performance,benchmark"
└─ avg_score: 8.5

category: "format_pattern"
├─ name: "speedrun"
├─ retention_rate: "85%"
└─ ideal_duration: "8-12min"
```

### 2. **Conteúdo Gerado**
```
category: (sem categoria - conteúdo específico)
├─ raw_idea: "streaming do claude sdk"
├─ validation_score: 8.5
├─ angle: "comparação técnica"
└─ estimated_views: "30K-60K"

(título)
├─ name: "🚨 5 ERROS que MATAM seu Claude SDK"
├─ ctr_score: 9.3
├─ formula: "Choque + Número"
└─ triggers: "FOMO + Curiosidade"
```

### 3. **Tópicos**
```
category: "topic"
└─ name: "streaming"
```

## Relacionamentos

### **Padrões de Sucesso**
```cypher
(Título)-[:USED_FORMULA {ctr_achieved: 9.3}]->(Formula)
(Título)-[:USED_TRIGGER {effectiveness: "alta"}]->(Gatilho)
(Ideia)-[:HAS_ANGLE {validation_score: 8.5}]->(Ângulo)
(Ideia)-[:RECOMMENDED_FORMAT]->(Formato)
```

### **Co-ocorrência e Combinações**
```cypher
(Formula1)-[:WORKS_WELL_WITH {combined_ctr: 9.5}]->(Formula2)
(Tópico1)-[:SIMILAR_TO {similarity_score: 0.85}]->(Tópico2)
```

### **Hierarquia de Conhecimento**
```cypher
(Ideia)-[:GENERATED]->(Título)
(Título)-[:ABOUT]->(Tópico)
(Ângulo)-[:WORKS_FOR]->(Tópico)
```

## Grafo Visual

```
┌─────────────────┐
│   IDEA          │
│ "streaming SDK" │
│  score: 8.5     │
└────┬──────┬─────┘
     │      │
     │      └─────────[:HAS_ANGLE]──────────┐
     │                                       │
     └─[:GENERATED]──┐                      ▼
                     │              ┌──────────────┐
                     │              │    ANGLE     │
                     ▼              │ "comparação" │
            ┌──────────────┐        │  avg: 8.5    │
            │    TITLE     │        └──────────────┘
            │ "🚨 5 ERROS" │
            │  CTR: 9.3    │
            └──┬────┬──────┘
               │    │
     [:USED_FORMULA]│
               │    └─[:USED_TRIGGER]──┐
               │                        │
               ▼                        ▼
      ┌──────────────┐        ┌──────────────┐
      │   FORMULA    │        │   TRIGGER    │
      │"Choque+Num"  │        │    "FOMO"    │
      │ avg_ctr: 9.2 │        │  score: 8.7  │
      └──────┬───────┘        └──────────────┘
             │
             │[:WORKS_WELL_WITH]
             ▼
      ┌──────────────┐
      │   FORMULA    │
      │ "Segredo"    │
      │ avg_ctr: 8.8 │
      └──────────────┘
```

## Queries Úteis

### 1. Encontrar fórmulas de alto CTR
```python
neo4j_client.buscar_melhores_formulas(min_ctr=8.5, limit=5)
# Retorna: Fórmulas com avg_ctr >= 8.5
```

### 2. Descobrir ângulos para tópico
```python
neo4j_client.buscar_angulos_por_topico("streaming", limit=3)
# Retorna: Ângulos testados com sucesso para "streaming"
```

### 3. Analisar combinações de fórmulas
```cypher
MATCH (f1:Learning {category: "formula_pattern"})
     -[r:WORKS_WELL_WITH]->(f2:Learning)
WHERE r.combined_ctr > 9.0
RETURN f1.name, f2.name, r.combined_ctr
ORDER BY r.combined_ctr DESC
```

### 4. Rastrear performance de gatilhos
```cypher
MATCH (titulo:Learning)-[r:USED_TRIGGER]->(gatilho:Learning)
WHERE gatilho.category = "psychological_trigger"
RETURN gatilho.name,
       avg(titulo.ctr_score) as avg_performance,
       count(r) as usage_count
ORDER BY avg_performance DESC
```

## Evolução Automática

O sistema aprende automaticamente:
1. **Toda vez que gera título** → atualiza `avg_ctr` da fórmula
2. **Quando combina fórmulas** → cria relacionamento `WORKS_WELL_WITH`
3. **Ao validar ideia** → fortalece conexão `HAS_ANGLE`
4. **Análise de tópicos** → descobre similaridade entre tópicos

## Exemplo de Uso Completo

```python
# 1. Criar padrões base (uma vez)
client = Neo4jClient()

# Criar fórmulas
formula1 = client.criar_memoria_formula(
    formula_name="Choque + Número",
    pattern="🚨 [NUM] [COISA] que [AÇÃO]",
    avg_ctr=9.2,
    usage_count=15
)

# Criar gatilhos
gatilho1 = client.criar_memoria_gatilho(
    trigger_name="FOMO",
    description="Medo de perder oportunidade",
    effectiveness_score=8.7
)

# 2. Ao gerar conteúdo
ideia = client.criar_memoria_ideia(...)
titulo = client.criar_memoria_titulo(...)

# 3. Criar relacionamentos
client.conectar_titulo_usa_formula(titulo_id, formula1_id, ctr_achieved=9.3)
client.conectar_titulo_usa_gatilho(titulo_id, gatilho1_id, effectiveness="alta")

# 4. Buscar insights
best_formulas = client.buscar_melhores_formulas(min_ctr=8.5)
# Usar essas fórmulas no próximo título!
```

## Próximos Passos

- [ ] Implementar análise de temporal patterns (qual fórmula funciona melhor em cada época)
- [ ] Adicionar embeddings semânticos para similaridade de ideias
- [ ] Criar dashboard visual do grafo (Cypher queries → visualization)
- [ ] Auto-discovery de novas fórmulas baseado em títulos de sucesso
