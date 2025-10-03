# 🧠 Claude SDK Knowledge Graph

## Modelo de Grafo para Aprendizado sobre Claude Agent SDK

### Categorias de Nós (Label: Learning)

```
┌─────────────────────────────────────────────────────────┐
│ CATEGORY            │ DESCRIÇÃO                          │
├─────────────────────┼────────────────────────────────────┤
│ sdk_pattern         │ Padrões de uso do SDK              │
│ sdk_concept         │ Conceitos fundamentais             │
│ code_example        │ Exemplos de código                 │
│ validation          │ Testes e validações                │
└─────────────────────────────────────────────────────────┘
```

## Relacionamentos Principais

### **1. IMPLEMENTS** (Exemplo implementa Padrão)
```cypher
(Exemplo)-[:IMPLEMENTS {quality: "excellent"}]->(Pattern)
```

**Exemplo:**
```
┌────────────────────────────┐
│  CODE_EXAMPLE              │
│  "validator.py"            │
│  demonstrates: "async ctx" │
└──────────┬─────────────────┘
           │
           │[:IMPLEMENTS {quality: "excellent"}]
           │
           ▼
┌────────────────────────────┐
│  SDK_PATTERN               │
│  "ClaudeSDKClient async"   │
│  success_rate: 0.95        │
└────────────────────────────┘
```

### **2. DEMONSTRATES** (Exemplo demonstra Conceito)
```cypher
(Exemplo)-[:DEMONSTRATES {clarity_score: 9.5}]->(Conceito)
```

**Exemplo:**
```
┌────────────────────────────┐
│  CODE_EXAMPLE              │
│  "streaming_chat.py"       │
│  complexity: "medium"      │
└──────────┬─────────────────┘
           │
           │[:DEMONSTRATES {clarity: 9.5}]
           │
           ▼
┌────────────────────────────┐
│  SDK_CONCEPT               │
│  "Streaming Responses"     │
│  use_cases: "chat,live"    │
└────────────────────────────┘
```

### **3. VALIDATES** (Validação valida Padrão)
```cypher
(Validation)-[:VALIDATES {passed: true, edge_cases: 5}]->(Pattern)
```

**Exemplo:**
```
┌────────────────────────────┐
│  VALIDATION                │
│  "test_async_context.py"   │
│  passes: true              │
└──────────┬─────────────────┘
           │
           │[:VALIDATES {passed: true, edge_cases: 5}]
           │
           ▼
┌────────────────────────────┐
│  SDK_PATTERN               │
│  "ClaudeSDKClient async"   │
│  success_rate: 0.95        │
└────────────────────────────┘
```

## Relacionamentos Secundários

### **4. REQUIRES** (Padrão requer Conceito)
```cypher
(Pattern)-[:REQUIRES {importance: "required"}]->(Conceito)
```

**Exemplo:**
```
┌────────────────────────────┐
│  SDK_PATTERN               │
│  "Multi-turn conversation" │
└──────────┬─────────────────┘
           │
           │[:REQUIRES {importance: "required"}]
           │
           ▼
┌────────────────────────────┐
│  SDK_CONCEPT               │
│  "Session Management"      │
└────────────────────────────┘
```

### **5. EXTENDS** (Conceito estende Conceito)
```cypher
(ConceitoAvançado)-[:EXTENDS]->(ConceitoBase)
```

**Exemplo:**
```
┌────────────────────────────┐
│  SDK_CONCEPT               │
│  "Streaming with Hooks"    │
└──────────┬─────────────────┘
           │
           │[:EXTENDS]
           │
           ▼
┌────────────────────────────┐
│  SDK_CONCEPT               │
│  "Basic Streaming"         │
└────────────────────────────┘
```

### **6. SUPERSEDES** (Padrão substitui Padrão)
```cypher
(PatternNovo)-[:SUPERSEDES {reason: "Better performance"}]->(PatternAntigo)
```

**Exemplo:**
```
┌────────────────────────────┐
│  SDK_PATTERN               │
│  "ClaudeSDKClient"         │
└──────────┬─────────────────┘
           │
           │[:SUPERSEDES {reason: "Simplified API"}]
           │
           ▼
┌────────────────────────────┐
│  SDK_PATTERN               │
│  "query() function"        │
│  success_rate: 0.75        │
└────────────────────────────┘
```

## Grafo Completo: Exemplo Real

```
         ┌─────────────────┐
         │  SDK_CONCEPT    │
         │  "Async Context"│
         └────────┬────────┘
                  │
         [:EXTENDS]│
                  │
         ┌────────▼────────┐
         │  SDK_CONCEPT    │
         │  "Session Mgmt" │
         └────────┬────────┘
                  │
                  │[:REQUIRES]
                  │
         ┌────────▼────────────────┐
         │  SDK_PATTERN            │
         │  "ClaudeSDKClient async"│
         │  success_rate: 0.95     │
         └──────┬──────────▲───────┘
                │          │
    [:IMPLEMENTS]│          │[:VALIDATES]
                │          │
                │          │
    ┌───────────▼──┐  ┌───┴──────────────┐
    │ CODE_EXAMPLE │  │  VALIDATION      │
    │ validator.py │  │  test_async.py   │
    │ complexity:  │  │  passes: true    │
    │   "medium"   │  │  edge_cases: 5   │
    └──────┬───────┘  └──────────────────┘
           │
           │[:DEMONSTRATES {clarity: 9.5}]
           │
    ┌──────▼──────────┐
    │  SDK_CONCEPT    │
    │  "Streaming"    │
    │  use_cases: ... │
    └─────────────────┘
```

## Queries Úteis

### 1. Encontrar todos os exemplos que implementam um padrão
```cypher
MATCH (exemplo:Learning {category: "code_example"})
     -[r:IMPLEMENTS]->(pattern:Learning {category: "sdk_pattern"})
WHERE pattern.name = "ClaudeSDKClient async"
RETURN exemplo.name, r.quality
ORDER BY r.quality DESC
```

### 2. Verificar validações de um padrão
```cypher
MATCH (val:Learning {category: "validation"})
     -[r:VALIDATES]->(pattern:Learning)
WHERE pattern.name = "ClaudeSDKClient async"
RETURN val.name, r.passed, r.edge_cases_covered
```

### 3. Descobrir pré-requisitos de um padrão
```cypher
MATCH (pattern:Learning {category: "sdk_pattern"})
     -[r:REQUIRES]->(conceito:Learning {category: "sdk_concept"})
WHERE pattern.name = "Multi-turn conversation"
RETURN conceito.name, r.importance
ORDER BY r.importance
```

### 4. Encontrar conceitos avançados baseados em conceito base
```cypher
MATCH (avancado:Learning)-[:EXTENDS]->(base:Learning)
WHERE base.name = "Basic Streaming"
RETURN avancado.name, avancado.use_cases
```

### 5. Rastrear evolução de padrões
```cypher
MATCH path = (novo:Learning)-[:SUPERSEDES*]->(antigo:Learning)
WHERE novo.category = "sdk_pattern"
RETURN [node IN nodes(path) | node.name] as evolution,
       length(path) as generations
ORDER BY generations DESC
```

## Uso no Código

### Exemplo 1: Registrar novo padrão descoberto

```python
from src.neo4j_client import Neo4jClient

client = Neo4jClient()

# 1. Criar padrão
pattern = client.criar_memoria_pattern(
    pattern_name="ClaudeSDKClient with async context",
    description="Usar async with para gerenciar sessão automaticamente",
    code_snippet='''
async with ClaudeSDKClient(options=options) as client:
    await client.query(prompt)
    async for message in client.receive_response():
        ...
    ''',
    success_rate=0.95
)

# 2. Criar conceito pré-requisito
conceito = client.criar_memoria_conceito(
    concept_name="Async Context Manager",
    explanation="Python async with statement para resource cleanup",
    use_cases=["file handling", "network connections", "sessions"]
)

# 3. Conectar: padrão requer conceito
client.conectar_pattern_requires_conceito(
    pattern_id="pattern_123",
    conceito_id="conceito_456",
    importance="required"
)
```

### Exemplo 2: Registrar exemplo de código

```python
# 1. Criar exemplo
exemplo = client.criar_memoria_exemplo(
    example_name="validator.py - async validation",
    code=open("src/agents/validator.py").read(),
    demonstrates_what="ClaudeSDKClient async pattern",
    complexity="medium"
)

# 2. Conectar: exemplo implementa padrão
client.conectar_exemplo_implementa_pattern(
    exemplo_id="exemplo_789",
    pattern_id="pattern_123",
    implementation_quality="excellent"
)

# 3. Conectar: exemplo demonstra conceito
client.conectar_exemplo_demonstra_conceito(
    exemplo_id="exemplo_789",
    conceito_id="conceito_456",
    clarity_score=9.5
)
```

### Exemplo 3: Registrar validação/teste

```python
# 1. Criar validação
validacao = client.criar_memoria_validacao(
    validation_name="test_async_context_cleanup",
    validates_what="Async context properly cleans up resources",
    test_code='''
async def test_cleanup():
    async with ClaudeSDKClient() as client:
        await client.query("test")
    # Verify resources released
    assert client._session is None
    ''',
    passes=True
)

# 2. Conectar: validação valida padrão
client.conectar_validacao_valida_pattern(
    validacao_id="val_101",
    pattern_id="pattern_123",
    test_passed=True,
    edge_cases_covered=5
)
```

### Exemplo 4: Marcar padrão como obsoleto

```python
# Novo padrão substitui antigo
client.conectar_pattern_supersedes_pattern(
    pattern_novo_id="pattern_new_456",
    pattern_antigo_id="pattern_old_123",
    reason="Simplified API with better error handling"
)
```

## Benefícios do Modelo

1. **Rastreabilidade**: Saber onde cada padrão é usado
2. **Validação**: Garantir que padrões têm testes
3. **Aprendizado**: Descobrir conceitos relacionados
4. **Evolução**: Acompanhar mudanças de padrões ao longo do tempo
5. **Recomendação**: Sugerir exemplos baseados no que usuário está aprendendo

## Próximos Passos

- [ ] Auto-descoberta de padrões analisando código
- [ ] Score automático de qualidade baseado em validações
- [ ] Sugestão de exemplos relacionados durante desenvolvimento
- [ ] Dashboard visual do grafo de conhecimento
