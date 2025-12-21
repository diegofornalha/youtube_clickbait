# Workflow Completo - Geração de Títulos Virais

## Visão Geral
Este documento detalha o fluxo completo desde receber uma ideia até salvar o título viral otimizado.

## Etapas do Processo

### 1️⃣ Recepção da Ideia
**Comando**: `/youtube [ideia]`

**Entrada esperada**:
- Texto com 3+ palavras
- Relacionado a Claude SDK/Code
- Pode ser vago (será refinado)

**Exemplo**:
```
/youtube "como dominar o claude code iniciantes"
```

### 2️⃣ Consulta ao Neo4j
**Objetivo**: Buscar contexto histórico e aprendizados

**Queries executadas**:
```cypher
// Buscar ideias similares
MATCH (n:Learning)
WHERE n.type = "video_idea"
AND n.name CONTAINS $keywords
RETURN n

// Buscar fórmulas que funcionaram
MATCH (t:Learning {type: "video_title"})
WHERE t.observations CONTAINS "CTR"
AND toFloat(t.ctr_score) > 8
RETURN t
```

### 3️⃣ Validação com idea_validator
**Agent**: `idea_validator.md`

**Critérios avaliados**:
1. **Potencial viral** (0-10)
2. **Valor técnico** (0-10)
3. **Fit com audiência** (0-10)
4. **Viabilidade de produção** (0-10)
5. **Saturação competitiva** (0-10)

**Output**:
```json
{
  "score": 7.8,
  "angle": "tutorial step-by-step",
  "viral_factors": ["baixa concorrência", "timing perfeito"],
  "estimated_views": "15K-40K",
  "improvements": ["adicionar número específico"]
}
```

### 4️⃣ Geração de Títulos
**Agent**: `video_title_creator.md`

**Processo**:
1. Aplicar 10 fórmulas diferentes
2. Gerar variações para cada fórmula
3. Calcular CTR score para cada título
4. Ordenar por potencial

**Fórmulas aplicadas**:
- Comparação Brutal
- Transformação Rápida
- Segredo Revelado
- Lista Específica
- Urgência/FOMO

### 5️⃣ Geração de Keywords SEO
**Categorias**:
- **Principal** (3-5): Tema central
- **Secundárias** (5-8): Variações
- **Long-tail** (3-5): Buscas específicas
- **Hashtags** (5-7): Para descoberta

**Exemplo de output**:
```
Principal: claude code, claude sdk, anthropic claude
Secundárias: claude vs gpt, ai coding, tutorial
Long-tail: como usar claude code tutorial completo
Hashtags: #claudecode #aicoding #tutorial
```

### 6️⃣ Salvamento e Persistência

#### Arquivo Local
**Path**: `outputs/Lista de ideias/[TÍTULO].md`

**Estrutura**:
```markdown
# [EMOJI] [TÍTULO]
**Data**: [HOJE]
**CTR**: X.X/10
**Status**: Pendente

## Ideia Original
## Insights do Neo4j
## Keywords SEO
## Top 10 Títulos
```

#### Persistência Neo4j
```cypher
CREATE (i:Learning {
  name: "VideoIdeia:$nome",
  type: "video_idea",
  observations: [$dados]
})

CREATE (t:Learning {
  name: "TítuloViral:$titulo",
  type: "video_title",
  observations: [$scores]
})

CREATE (i)-[:GENERATED]->(t)
```

## Tempo de Execução

| Etapa | Tempo Médio |
|-------|-------------|
| Consulta Neo4j | 2s |
| Validação | 5s |
| Geração títulos | 10s |
| Keywords SEO | 3s |
| Salvamento | 2s |
| **Total** | **~22s** |

## Pontos de Falha e Recuperação

### Neo4j indisponível
- **Fallback**: Continuar sem contexto histórico
- **Log**: Registrar em SOPs/neo4j-unavailable.md

### Validação falha
- **Fallback**: Usar score default 5.0
- **Action**: Prosseguir com avisos

### Arquivo já existe
- **Action**: Adicionar timestamp ao nome
- **Example**: `titulo-2025-10-23-1430.md`

## Otimizações Futuras

1. **Cache de fórmulas** frequentemente usadas
2. **Batch processing** para múltiplas ideias
3. **A/B testing** automático de títulos
4. **Integração com YouTube API** para métricas reais