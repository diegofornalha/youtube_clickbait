# Critérios de Scoring para Validação de Ideias

## Score Final (0-10)

O score final é calculado com base em 4 critérios ponderados:

```
Score = (Viral × 0.30) + (Technical × 0.25) + (Audience × 0.20) + (Uniqueness × 0.25)
```

---

## 1. Viral Potential (30%)

**O que avaliar:**
- Clickbait ético (promessa que pode ser cumprida)
- Potencial de thumbnail impactante
- Gatilhos emocionais presentes
- Compartilhabilidade

**Pontuação:**

| Score | Descrição |
|-------|-----------|
| 9-10 | Irresistível - impossível não clicar |
| 7-8 | Muito atrativo - alta chance de clique |
| 5-6 | Interessante - clique moderado |
| 3-4 | Genérico - baixo interesse |
| 1-2 | Sem apelo - ninguém clicaria |

**Gatilhos que aumentam score:**
- Curiosidade (gap de informação)
- FOMO (medo de perder algo)
- Transformação (antes/depois)
- Polêmica (opinião contrária)
- Números específicos

---

## 2. Technical Value (25%)

**O que avaliar:**
- Resolve problema real?
- Ensina algo útil?
- Tem profundidade técnica?
- Conteúdo pode ser demonstrado?

**Pontuação:**

| Score | Descrição |
|-------|-----------|
| 9-10 | Resolve dor crítica com solução clara |
| 7-8 | Útil e aplicável imediatamente |
| 5-6 | Informativo mas não essencial |
| 3-4 | Superficial ou óbvio |
| 1-2 | Sem valor prático |

**Para Claude SDK especificamente:**
- +2 pontos: Tutorial passo-a-passo
- +1 ponto: Comparação com alternativas
- +1 ponto: Caso de uso real
- -1 ponto: Conteúdo teórico demais

---

## 3. Audience Fit (20%)

**O que avaliar:**
- Nível adequado para a audiência?
- Timing correto (tendência atual)?
- Linguagem apropriada?
- Duração viável?

**Pontuação:**

| Score | Descrição |
|-------|-----------|
| 9-10 | Perfeito para o público-alvo |
| 7-8 | Muito relevante |
| 5-6 | Relevante mas não ideal |
| 3-4 | Desalinhado com audiência |
| 1-2 | Completamente fora do target |

**Audiência-alvo para Claude SDK:**
- Desenvolvedores brasileiros
- Nível: Intermediário a avançado
- Interesse: Automação, IA, produtividade
- Formato preferido: Tutoriais práticos

---

## 4. Uniqueness (25%)

**O que avaliar:**
- Ângulo original?
- Diferente do que já existe?
- Perspectiva única?
- Informação exclusiva?

**Pontuação:**

| Score | Descrição |
|-------|-----------|
| 9-10 | Nunca visto antes - pioneiro |
| 7-8 | Ângulo novo sobre tema conhecido |
| 5-6 | Abordagem ligeiramente diferente |
| 3-4 | Similar ao que já existe |
| 1-2 | Cópia de conteúdo existente |

**Formas de aumentar uniqueness:**
- Comparações inéditas
- Experimentos próprios
- Dados exclusivos
- Perspectiva contrária popular
- Combinação de temas

---

## Estimativa de Views

Baseado no score final:

| Score | Views Estimadas | Probabilidade |
|-------|-----------------|---------------|
| 9-10 | 50K-100K+ | Viral potencial |
| 7-8 | 20K-50K | Acima da média |
| 5-6 | 10K-20K | Média |
| 3-4 | 5K-10K | Abaixo da média |
| 1-2 | < 5K | Baixo desempenho |

---

## Output Padrão de Validação

```json
{
  "score": 8.5,
  "breakdown": {
    "viral_potential": 9,
    "technical_value": 8,
    "audience_fit": 8,
    "uniqueness": 9
  },
  "best_angle": "comparação técnica com números concretos",
  "views_estimate": "20K-50K",
  "recommendations": [
    "Adicionar números específicos no título",
    "Focar em resultado tangível"
  ]
}
```

---

## Decisão Baseada no Score

| Score | Ação |
|-------|------|
| 8+ | Aprovar e gerar títulos imediatamente |
| 6-7 | Sugerir ajustes no ângulo |
| 4-5 | Refinar ideia antes de prosseguir |
| <4 | Descartar ou pivotar completamente |
