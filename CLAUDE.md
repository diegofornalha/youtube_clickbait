# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão Geral do Projeto

Sistema automatizado para validação e geração de títulos virais para YouTube, utilizando **Claude Agents**, **Neo4j MCP** (memória persistente) e **hooks personalizados**.

### Resumo Executivo

**Propósito**: Gerar títulos virais otimizados para YouTube com validação de potencial e aprendizado contínuo.

**Como funciona**:
1. Usuário fornece ideia via `/youtube [ideia]`
2. Sistema consulta Neo4j para contexto histórico
3. Agents validam potencial viral e geram 3 variações de título
4. Título vencedor + métricas são salvos em arquivo minimalista
5. Aprendizados persistem no Neo4j para melhorias futuras

**Tech Stack**:
- **Claude Code** - Orquestração via Task tool
- **Neo4j MCP** - Grafo de conhecimento (padrões virais, histórico de CTR)
- **Python Hooks** - Automação pós-execução
- **Agents** - 3 especialistas (orchestrator, validator, creator)

**Output**: 4 linhas com título vencedor, CTR score, keywords e path do arquivo.

## Arquitetura

### Sistema de Agentes (`.claude/agents/`)

O projeto usa 3 agentes especializados invocados via Task tool:

1. **autonomous_orchestrator** (`.claude/agents/autonomous_orchestrator.md`)
   - Gera 3 variações de títulos virais diretamente
   - Aplica 3 fórmulas virais diferentes (Comparação Brutal, Transformação Rápida, Segredo Revelado, etc.)
   - Retorna JSON com array de títulos ranqueados por CTR score
   - **Quando usar**: Para gerar títulos rapidamente sem validação prévia

2. **idea_validator** (`.claude/agents/idea_validator.md`)
   - Valida potencial viral antes da geração de títulos
   - Consulta Neo4j para contexto histórico (`search_memories`)
   - Avalia 4 critérios: Viral Potential (30%), Technical Value (25%), Audience Fit (20%), Uniqueness (25%)
   - Retorna: `{score: 8.5, best_angle: "...", views_estimate: "20K-50K"}`
   - Persiste validação no Neo4j automaticamente

3. **video_title_creator** (`.claude/agents/video_title_creator.md`)
   - Gera 3 títulos otimizados usando fórmulas virais
   - Consulta Neo4j para patterns que funcionaram anteriormente
   - Gera keywords SEO e hashtags
   - Retorna: `{titles: [{title, ctr_score, formula}], keywords, hashtags}`
   - Salva títulos vencedores no Neo4j

### Slash Commands (`.claude/commands/`)

**`/youtube [ideia]`** (`.claude/commands/youtube.md`) - Interface principal do sistema

**Workflow automatizado**:
1. Buscar contexto no Neo4j (`mcp__neo4j-memory__search_memories`)
2. Validar ideia (Task tool → `idea_validator`)
3. Gerar títulos (Task tool → `video_title_creator`)
4. Salvar em `outputs/Lista de ideias/[slug].md` usando template minimalista

**Output minimalista para usuário**:
```
✅ [TÍTULO COM EMOJI]

CTR: 9.8/10 | Score: 8.5/10
Keywords: keyword1, keyword2, keyword3
📄 outputs/Lista de ideias/titulo-slug.md
```

**Regras críticas**:
- ❌ NÃO mostrar JSON bruto dos agentes
- ❌ NÃO explicar cada etapa do processo
- ✅ Apenas resultado final limpo (máximo 4 linhas)

### Neo4j MCP Integration

**Ferramentas pré-aprovadas** (`.claude/settings.local.json`):
- `mcp__neo4j-memory__search_memories` - Buscar ideias/padrões históricos
- `mcp__neo4j-memory__create_entities` - Criar nós (VideoIdea, Title, Pattern)
- `mcp__neo4j-memory__add_observations` - Adicionar aprendizados a entidades existentes

**Modelo de dados do grafo**:
```cypher
(VideoIdea:Learning {name, type, observations[]})
  -[GENERATED]->
(Title:Learning {name, type, observations[]})
  -[USES_PATTERN]->
(Pattern:Learning {name: "Comparação Brutal", type: "viral_formula", observations[]})
```

**Regra crítica**: Todos os agentes DEVEM consultar Neo4j antes de processar e salvar resultados depois.

### Hooks (`.claude/hooks/`)

**Hooks ativos** (configurados em `.claude/settings.json`):

1. **auto_save_output.py** (PostToolUse → Write)
   - Salva automaticamente outputs gerados pelo Write tool
   - Evita perda de conteúdo gerado

2. **log_agent_execution.py** (PostToolUse → Task)
   - Registra execuções de agentes para debugging
   - Útil para rastrear chamadas ao idea_validator e video_title_creator

**Hooks disponíveis mas inativos**:
- `neo4j_auto_persist.py` - Auto-persistência no Neo4j após validações/títulos
- `neo4j_learning_persister.py` - Registro automático de padrões aprendidos
- `post_tool_use_logger.py` - Logger genérico de ferramentas
- `pre_tool_use_auto_approve.py` - Auto-aprovação de ferramentas específicas

### Skills (`.claude/skills/`)

**viral-youtube-titles** (`.claude/skills/viral-youtube-titles/SKILL.md`)

Base de conhecimento para geração de títulos virais:

**Fórmulas principais**:
1. Number + Adjective + Keyword + Promise
2. Question Hook + Unexpected Answer
3. Transformation/Journey
4. Controversy & Hot Takes
5. Lists & Rankings

**Power Words por categoria**:
- Emotional: Shocking, Insane, Mind-Blowing, Revolutionary, Secret
- Value: Free, Easy, Simple, Fast, Ultimate, Complete
- Urgency: Now, Today, Finally, New, Breaking
- Credibility: Proven, Scientific, Expert, Professional

**Guidelines técnicas**:
- Comprimento ideal: 50-60 caracteres (máx 70)
- Primeiros 40 chars devem conter info crítica (mobile)
- 1-2 emojis estratégicos máximo
- Incluir números concretos quando possível

## Configuração e Permissões

### Auto-aprovação de Ferramentas Neo4j

O arquivo `.claude/settings.local.json` define permissões pré-aprovadas:

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

Estas ferramentas executam sem pedir confirmação ao usuário, essencial para workflow automatizado.

### Hooks Ativos

O arquivo `.claude/settings.json` define hooks ativos:

```json
{
  "hooks": [
    {
      "matcher": "Write",
      "hooks": [{"type": "PostToolUse", "script": ".claude/hooks/auto_save_output.py"}]
    },
    {
      "matcher": "Task",
      "hooks": [{"type": "PostToolUse", "script": ".claude/hooks/log_agent_execution.py"}]
    }
  ],
  "permissionMode": "acceptEdits"
}
```

**Importante**: `permissionMode: "acceptEdits"` permite que Claude faça edições sem aprovação constante.

## Como Usar o Sistema

### Comando principal
```bash
/youtube [sua ideia de vídeo]
```

Este comando executa todo o workflow automaticamente: valida → gera títulos → salva arquivo.

### Invocar agentes individualmente

Para usar agentes de forma isolada via Task tool:

```python
# Gerar apenas títulos (sem validação)
Task(
  subagent_type="autonomous_orchestrator",
  prompt="Gerar títulos para: streaming do claude sdk"
)

# Apenas validar ideia
Task(
  subagent_type="idea_validator",
  prompt="Validar: hooks do claude sdk"
)

# Apenas gerar títulos com contexto prévio
Task(
  subagent_type="video_title_creator",
  prompt="Gerar título viral para: multi-agents no claude code"
)
```

### Consultar Neo4j diretamente

```python
# Buscar padrões relacionados
mcp__neo4j-memory__search_memories("claude sdk streaming")

# Ver todo o grafo
mcp__neo4j-memory__read_graph()

# Criar entidade manualmente
mcp__neo4j-memory__create_entities({
  "entities": [{
    "name": "Título Teste",
    "type": "title",
    "observations": ["CTR alto", "Fórmula de comparação"]
  }]
})
```

## Estrutura do Projeto

```
.claude/
├── agents/                         # Agentes especializados
│   ├── autonomous_orchestrator.md  # Gera títulos diretamente (3 variações)
│   ├── idea_validator.md           # Valida potencial viral (score 0-10)
│   ├── video_title_creator.md      # Gera títulos otimizados (3 variações)
│   └── test_hybrid.md              # Agente de teste
│
├── commands/                       # Slash commands
│   ├── youtube.md                  # /youtube - Workflow completo
│   └── update_doc.md               # /update_doc - Atualizar documentação
│
├── hooks/                          # Hooks Python
│   ├── auto_save_output.py         # ✅ ATIVO - Auto-save após Write
│   ├── log_agent_execution.py      # ✅ ATIVO - Log de agents
│   ├── neo4j_auto_persist.py       # 🔒 Inativo - Persistência Neo4j
│   ├── neo4j_learning_persister.py # 🔒 Inativo - Aprendizado contínuo
│   └── ...                         # Outros hooks disponíveis
│
├── skills/                         # Skills de conhecimento
│   ├── viral-youtube-titles/       # Base de fórmulas virais
│   │   ├── SKILL.md                # Documentação principal
│   │   └── references/             # Power words, formulas, case studies
│   └── excel-analysis/             # Skill de análise Excel
│
├── settings.json                   # Config de hooks ativos
└── settings.local.json             # Permissões Neo4j (auto-approve)

outputs/
└── Lista de ideias/                # Arquivos .md gerados (< 15 linhas cada)
    ├── [titulo-slug-1].md
    └── [titulo-slug-2].md

.agent/                             # Sistema de documentação adicional
├── system/                         # Arquitetura e workflows
├── SOPs/                           # Standard Operating Procedures
└── tasks/                          # Tasks de desenvolvimento
```

## Convenções e Contratos de Dados

### Formato de Resposta dos Agentes

**idea_validator** retorna JSON simples:
```json
{
  "score": 8.5,
  "best_angle": "comparação técnica com números concretos",
  "views_estimate": "20K-50K"
}
```

**video_title_creator** retorna array de títulos:
```json
{
  "titles": [
    {
      "title": "⚡ Claude Code em 15 MIN - Do ZERO ao PRIMEIRO Agent",
      "ctr_score": 9.8,
      "formula": "Transformação Rápida"
    },
    {
      "title": "🔥 Claude vs Cursor - A VERDADE que Devs Escondem",
      "ctr_score": 9.5,
      "formula": "Comparação Brutal"
    },
    {
      "title": "🚀 5 Segredos do Claude Code que NINGUÉM Conta",
      "ctr_score": 9.2,
      "formula": "Segredo Revelado"
    }
  ],
  "keywords": "claude code, tutorial, agents, automação",
  "hashtags": "#claudecode #ai #coding #automation"
}
```

**autonomous_orchestrator** retorna estrutura completa:
```json
{
  "status": "success",
  "ideia": "streaming do claude sdk",
  "titles": [
    {"title": "...", "ctr_score": 9.8, "formula": "..."},
    {"title": "...", "ctr_score": 9.5, "formula": "..."},
    {"title": "...", "ctr_score": 9.2, "formula": "..."}
  ],
  "keywords": "claude sdk, streaming, tutorial, api",
  "hashtags": "#claudesdk #ai #coding"
}
```

### Template de Arquivo de Output

**Caminho**: `outputs/Lista de ideias/[slug].md`
**Tamanho máximo**: 15 linhas
**Formato obrigatório**:

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

**Regras**:
- Nome do arquivo: slug do título vencedor (lowercase, hífens, sem caracteres especiais)
- Sempre incluir data no formato ISO (YYYY-MM-DD)
- Ordem das sugestões: sempre do maior para menor CTR score

### Regras de Output para Usuário

**NUNCA mostrar**:
- ❌ JSON bruto dos agentes
- ❌ Explicações detalhadas de cada etapa
- ❌ Logs de Neo4j
- ❌ Múltiplos títulos (apenas o campeão)

**SEMPRE mostrar**:
- ✅ Título final com emoji
- ✅ CTR + Score (métricas chave)
- ✅ Keywords principais (3-5)
- ✅ Caminho do arquivo salvo

## Princípios de Design

### 1. Minimalismo Extremo
- Output para usuário: máximo 4 linhas
- Arquivos gerados: máximo 15 linhas
- Zero explicações sobre processo interno
- Apenas resultado final e métricas chave

### 2. Automação Completa
- Neo4j persiste automaticamente aprendizados
- Agents consultam histórico antes de processar
- Hooks salvam outputs sem intervenção
- `/youtube` executa todo workflow sem steps manuais

### 3. Aprendizado Contínuo
- Cada execução alimenta o grafo de conhecimento
- Padrões virais são identificados e reutilizados
- Fórmulas que funcionam são priorizadas
- Histórico de CTR score informa decisões futuras

### 4. Fórmulas Data-Driven
- Base de 5 fórmulas virais comprovadas
- Power words categorizados por impacto psicológico
- Guidelines técnicas (length, emojis, keywords)
- A/B testing mindset (sempre 3 variações)

## Regras Críticas de Operação

### Obrigatório para TODOS os agentes:
1. ✅ Consultar Neo4j ANTES de processar (`search_memories`)
2. ✅ Salvar resultados no Neo4j DEPOIS de processar
3. ✅ Retornar JSON estruturado (nunca texto livre)
4. ✅ Gerar exatamente 3 variações de título
5. ✅ Usar fórmulas virais DIFERENTES em cada variação

### Proibido:
1. ❌ Mostrar JSON bruto para usuário final
2. ❌ Executar `/youtube` passo-a-passo manualmente
3. ❌ Gerar títulos sem consultar Neo4j primeiro
4. ❌ Usar mesma fórmula em múltiplos títulos
5. ❌ Output verboso ou explicações detalhadas

## Recursos Adicionais

- **Fórmulas virais completas**: `.claude/skills/viral-youtube-titles/SKILL.md`
- **Documentação AI Fluency**: `AI_Fluency_*.md` (material educacional, não parte do sistema)
- **Simplificação recente**: `.claude/SIMPLIFICACAO.md` (contexto de refatoração)
