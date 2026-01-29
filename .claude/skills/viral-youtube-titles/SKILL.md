---
name: viral-youtube-titles
description: |
  Gera pacote completo de SEO para YouTube: título viral, descrição otimizada,
  tags, sugestão de thumbnail e hook de abertura. Usar quando precisar:
  (1) Gerar títulos virais para vídeos
  (2) Criar descrição SEO-otimizada
  (3) Montar pacote completo para upload
  Triggers: título viral, youtube title, gerar título, seo youtube, descrição youtube
---

# Viral YouTube Titles

Skill para geração de pacote SEO para YouTube.

## Quick Start

1. Consultar Neo4j para contexto histórico
2. Validar potencial da ideia (score 0-10)
3. Gerar 3 títulos + tags + hashtags + hook
4. Salvar resultado em `outputs/Lista de ideias/`

## Workflow Completo

### 1. Consultar Neo4j (Contexto)

```javascript
mcp__neo4j-memory__search_memories("{ideia}")
```

### 2. Validar Potencial (Score 0-10)

| Critério | Peso | O que avaliar |
|----------|------|---------------|
| Viral Potential | 30% | Clickbait ético + thumbnail impactante |
| Technical Value | 25% | Resolve problema real |
| Audience Fit | 20% | Nível adequado + timing |
| Uniqueness | 25% | Ângulo original |

### 3. Gerar Pacote SEO

#### 3.1 Títulos (3 variações)

**Fórmulas Virais:**

1. **Comparação Brutal**: `X vs Y - Um é Z vezes MELHOR`
2. **Transformação Rápida**: `Do ZERO ao RESULTADO em X MIN`
3. **Segredo Revelado**: `O que NINGUÉM te conta sobre X`
4. **Lista Específica**: `X Truques de Y que TODO Z precisa`
5. **Urgência**: `APRENDA X ANTES que vire mainstream`

**Regras:**
- Máximo 70 caracteres
- Emoji estratégico no início
- Números concretos
- Cada título usa fórmula DIFERENTE
- CTR mínimo: 8/10

#### 3.2 Tags (lista separada por vírgula)

**Regras:**
- Máximo 500 caracteres total
- Mix de tags curtas e longas (long-tail)
- Incluir variações com/sem acento
- Tag principal = título exato

#### 3.3 Hashtags

**Regras:**
- Máximo 3 hashtags
- Usar na descrição do YouTube
- Palavras-chave principais

#### 3.4 Hook de Abertura (primeiros 30 segundos)

**Estrutura:**
1. **Provocação** (0-5s): Pergunta ou afirmação impactante
2. **Promessa** (5-15s): O que o viewer vai ganhar
3. **Credibilidade** (15-30s): Por que você pode ensinar isso

### 4. Salvar Resultado

**Caminho**: `outputs/Lista de ideias/[TÍTULO_SLUG].md`

**Template:**

```markdown
# 🎬 [IDEIA ORIGINAL]

**Score**: X/10 | **Data**: YYYY-MM-DD

---

## 🎯 TÍTULOS

1. [EMOJI] Título opção 1 (CTR: X.X) - Fórmula: [nome]
2. [EMOJI] Título opção 2 (CTR: X.X) - Fórmula: [nome]
3. [EMOJI] Título opção 3 (CTR: X.X) - Fórmula: [nome]

---

## 🏷️ TAGS
tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8

---

## #️⃣ HASHTAGS
#hashtag1 #hashtag2 #hashtag3

---

## 🎬 HOOK (primeiros 30s)

"[Script do hook de abertura - estrutura: provocação + promessa + credibilidade]"
```

### 5. Persistir no Neo4j

```javascript
mcp__neo4j-memory__create_entities([{
  name: "TítuloViral:{titulo}",
  entityType: "video_title",
  observations: ["ctr:{score}", "formula:{formula}", "keywords:{keywords}"]
}])
```

## Output Final para Usuário

```
✅ Pacote SEO gerado!

Score: 8.5/10

📄 outputs/Lista de ideias/[slug].md
```

## Contexto Importante

### Sobre COWORK (Anthropic)
COWORK é uma feature da Anthropic (não coworking físico):
- Modo do Claude Desktop para automação de tarefas
- Permite executar código, manipular arquivos, navegar web
- Funciona como "funcionário de IA" pessoal
- Concorrente: Claude Code (mais técnico, linha de comando)

### Audiência-Alvo
- Desenvolvedores brasileiros
- Interessados em IA e automação
- Nível: Iniciante a avançado
- Preferência: Tutoriais práticos com resultado rápido

## Recursos

### references/
- `viral_formulas.md` - Database de fórmulas virais
- `power_words.md` - Palavras de impacto
- `scoring_criteria.md` - Critérios de validação
