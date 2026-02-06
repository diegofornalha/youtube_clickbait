# /youtube - Gerador de Pacote SEO Completo

Gera pacote completo para YouTube: 5 títulos virais (1 por pilar emocional), tags, hashtags e hook.

## Uso

```bash
/youtube [sua ideia]
```

## Instruções para Claude

Quando o usuário executar `/youtube [ideia]`:

### 1. Carregar Skill e References

Ler todos os arquivos para contexto completo:
```
.claude/skills/viral-youtube-titles/SKILL.md
.claude/skills/viral-youtube-titles/references/psicologia_clique.md
.claude/skills/viral-youtube-titles/references/viral_formulas.md
.claude/skills/viral-youtube-titles/references/power_words.md
.claude/skills/viral-youtube-titles/references/scoring_criteria.md
```

### 2. Validar Ideia

**Checklist Obrigatório (6 pontos):**
- [ ] Máximo 55 caracteres?
- [ ] Frontloading aplicado?
- [ ] Open Loop identificado?
- [ ] Gatilho emocional definido?
- [ ] Alinhamento Browse/Search?
- [ ] Título entrega promessa?

**Score mínimo: 7/10**

### 3. Gerar 5 Títulos (1 por Pilar Emocional)

| # | Pilar | Objetivo |
|---|-------|----------|
| 1 | CURIOSIDADE | Gap de informação |
| 2 | MEDO/URGÊNCIA | Instinto de preservação |
| 3 | DESEJO/RECOMPENSA | Ganho tangível |
| 4 | SURPRESA/NOVIDADE | Desafiar status quo |
| 5 | FOMO | Sensação de perda |

**Regras:**
- Máximo **55 caracteres** por título
- Power word nas **primeiras 3 palavras**
- **Open Loop** em todos os títulos

### 4. Completar Pacote SEO

- Tags (máx 500 chars)
- Hashtags (máx 3)
- Hook de 30 segundos

### 5. Salvar Arquivo

**Caminho**: `outputs/Lista de ideias/[TÍTULO_SLUG].md`

## Output para Usuário

```
✅ Pacote SEO gerado!

Score: 8.5/10 | Estratégia: Browse

📄 outputs/Lista de ideias/[slug].md
```

## Regras

- ❌ NÃO mostrar conteúdo completo do arquivo
- ❌ NÃO explicar cada etapa
- ❌ NÃO exceder 55 caracteres por título
- ✅ Apenas confirmação + score + path
- ✅ Usuário abre arquivo para ver detalhes
