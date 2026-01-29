# CLAUDE.md

Guia para Claude Code ao trabalhar neste repositório.

## Visão Geral

Sistema para geração de títulos virais para YouTube usando **Skills**, **Neo4j** e **Hooks**.

### Como Funciona

1. Usuário executa `/youtube [ideia]`
2. Sistema consulta Neo4j para contexto histórico
3. Skill valida potencial e gera 3 variações de título
4. Resultado salvo em `outputs/Lista de ideias/`
5. Aprendizados persistem no Neo4j

### Tech Stack

- **Claude Code** - Orquestração
- **Neo4j MCP** - Memória persistente (padrões virais, histórico)
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
└── settings.local.json         # Permissões Neo4j

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

1. Consultar Neo4j (`search_memories`)
2. Validar potencial (score 0-10)
3. Gerar 3 títulos com fórmulas diferentes
4. Salvar arquivo minimalista
5. Persistir no Neo4j

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

## Neo4j Integration

### Ferramentas Pré-Aprovadas

```json
{
  "permissions": {
    "allow": [
      "mcp__neo4j-memory__search_memories",
      "mcp__neo4j-memory__create_entities",
      "mcp__neo4j-memory__add_observations"
    ]
  }
}
```

### Consultas Comuns

```python
# Buscar padrões
mcp__neo4j-memory__search_memories("claude sdk")

# Ver grafo completo
mcp__neo4j-memory__read_graph()
```

## Regras de Operação

### SEMPRE

1. Consultar Neo4j antes de processar
2. Gerar 3 variações com fórmulas diferentes
3. Salvar no Neo4j após gerar
4. Manter output minimalista (máx 4 linhas)

### NUNCA

1. Mostrar JSON intermediário
2. Explicar cada etapa
3. Usar mesma fórmula em múltiplos títulos
4. Output verboso
