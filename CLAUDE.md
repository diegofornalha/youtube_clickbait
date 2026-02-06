# CLAUDE.md

Guia para Claude Code ao trabalhar neste repositório.

## Visão Geral

Sistema para geração de títulos virais para YouTube usando **Skills** e **Hooks**.

### Como Funciona

1. Usuário executa `/youtube [ideia]`
2. Skill valida potencial e gera 3 variações de título
3. Resultado salvo em `outputs/Lista de ideias/`

### Tech Stack

- **Claude Code** - Orquestração
- **Skills** - Conhecimento especializado em títulos virais
- **Hooks** - Automação pós-execução

## Estrutura do Projeto

```
.claude/
├── commands/
│   └── youtube.md              # /youtube - Comando principal
│
├── skills/
│   └── viral-youtube-titles/   # Skill de títulos virais
│       ├── SKILL.md            # Instruções e workflow
│       ├── scripts/            # Scripts Python
│       └── references/         # Fórmulas, power words, scoring
│
├── hooks/                      # Hooks de automação
│   ├── auto_save_output.py     # Auto-save após Write
│   └── log_agent_execution.py  # Log de execuções
│
└── settings.local.json        

outputs/
└── Lista de ideias/            # Arquivos gerados
```

## Comando Principal

```bash
/youtube [sua ideia]
```

Executa o workflow completo automaticamente.

### Output

```
✅ [TÍTULO COM EMOJI]

CTR: 9.8/10 | Score: 8.5/10
Keywords: keyword1, keyword2, keyword3
📄 outputs/Lista de ideias/titulo-slug.md
```

## Skill: viral-youtube-titles

A skill centraliza todo o conhecimento para geração de títulos:

### Workflow

1. Validar potencial (score 0-10)
2. Gerar 3 títulos com fórmulas diferentes
3. Salvar arquivo minimalista

### Fórmulas Virais

1. **Comparação Brutal**: `X vs Y - Um é Z vezes MELHOR`
2. **Transformação Rápida**: `Do ZERO ao RESULTADO em X MIN`
3. **Segredo Revelado**: `O que NINGUÉM te conta sobre X`
4. **Lista Específica**: `X Truques de Y que TODO Z precisa`
5. **Urgência**: `APRENDA X ANTES que vire mainstream`

### Recursos

- `references/viral_formulas.md` - Database de fórmulas
- `references/power_words.md` - Palavras de impacto
- `references/scoring_criteria.md` - Critérios de validação



## Regras de Operação

### SEMPRE

1. Gerar 3 variações com fórmulas diferentes
2. Manter output minimalista (máx 4 linhas)

### NUNCA

1. Mostrar JSON intermediário
2. Explicar cada etapa
3. Usar mesma fórmula em múltiplos títulos
4. Output verboso
