# /update_doc - Gerenciador de Documentação .agent

## Descrição
Comando para gerenciar a documentação estruturada na pasta `.agent`, mantendo o conhecimento do projeto organizado e acessível.

## Uso
```
/update_doc [comando] [parâmetros]
```

## Comandos Disponíveis

### initialize
Inicializa a estrutura completa de documentação do projeto.

```bash
/update_doc initialize
```

**Ações executadas**:
1. Cria estrutura de pastas `.agent/`
2. Analisa projeto e gera `system/architecture.md`
3. Cria `system/workflow.md` e `system/neo4j-schema.md`
4. Gera `readme.md` como índice principal
5. Registra no Neo4j a criação da documentação

### add-task [nome]
Adiciona novo plano de implementação na pasta `tasks/`.

```bash
/update_doc add-task melhorar-validacao-ideias
```

**Workflow**:
1. Criar plano detalhado para a tarefa
2. Salvar em `.agent/tasks/[nome].md`
3. Atualizar `readme.md` com referência
4. Persistir no Neo4j como "TaskPlan:[nome]"

### add-sop [problema]
Documenta solução para problema encontrado.

```bash
/update_doc add-sop fix-neo4j-timeout
```

**Workflow**:
1. Documentar problema e solução
2. Criar arquivo em `.agent/SOPs/[problema].md`
3. Incluir código de exemplo e prevenção
4. Atualizar `readme.md`
5. Criar entidade "SOP:[problema]" no Neo4j

### status
Mostra estatísticas da documentação atual.

```bash
/update_doc status
```

**Output esperado**:
```
📊 Status da Documentação .agent

System docs: 3 arquivos
Tasks: 2 planos (1 completo, 1 em progresso)
SOPs: 4 procedimentos documentados
Última atualização: 2025-10-23

Total de conhecimento: 9 documentos
```

### search [termo]
Busca termo em toda a documentação.

```bash
/update_doc search "neo4j"
```

## Estrutura dos Documentos

### Formato de Task
```markdown
# Task: [Nome da Feature]

## Objetivo
[Descrição clara do que será implementado]

## Requisitos
- [ ] Requisito 1
- [ ] Requisito 2

## Plano de Implementação
1. Passo detalhado 1
2. Passo detalhado 2

## Riscos e Mitigações
- Risco: [descrição]
  Mitigação: [ação]

## Critérios de Sucesso
- Métrica 1
- Métrica 2

## Status
🔄 Em progresso | ✅ Completo | ⏸️ Pausado
```

### Formato de SOP
```markdown
# SOP: [Nome do Problema]

## Problema
[Descrição detalhada do erro/problema]

## Sintomas
- Sintoma 1
- Sintoma 2

## Causa Raiz
[Explicação técnica da causa]

## Solução
### Passo a passo:
1. Ação corretiva 1
2. Ação corretiva 2

### Código:
```[linguagem]
// Código de exemplo
```

## Prevenção
- Medida preventiva 1
- Medida preventiva 2

## Tags
#categoria #ferramenta #severidade

## Data de Criação
YYYY-MM-DD
```

## Integração com Neo4j

### Entidades criadas
```cypher
// Para tasks
CREATE (t:Learning {
  name: "TaskPlan:[nome]",
  type: "task_plan",
  observations: [detalhes]
})

// Para SOPs
CREATE (s:Learning {
  name: "SOP:[problema]",
  type: "standard_procedure",
  observations: [solução]
})
```

## Regras Importantes

1. **SEMPRE ler `.agent/readme.md` primeiro** antes de qualquer implementação
2. **Documentar ANTES de implementar** (tasks)
3. **Documentar APÓS resolver** (SOPs)
4. **Manter readme.md atualizado** após cada adição
5. **Usar nomes descritivos** sem espaços (use hífens)

## Automação

### Hook para auto-documentação
Quando um erro é resolvido com sucesso, o sistema pode automaticamente sugerir:

```
"Detectei que você resolveu um problema com [X].
Deseja documentar como SOP? /update_doc add-sop [nome]"
```

## Exemplos de Uso

### Inicializar projeto novo
```bash
/update_doc initialize
# Sistema cria toda estrutura e documentação inicial
```

### Planejar nova feature
```bash
/update_doc add-task adicionar-cache-redis
# Cria plano detalhado antes de implementar
```

### Documentar bug resolvido
```bash
/update_doc add-sop timeout-youtube-api
# Documenta solução para referência futura
```

## Troubleshooting

### Pasta .agent não existe
```bash
/update_doc initialize
```

### readme.md dessincronizado
```bash
/update_doc rebuild-index
```

### Documentação duplicada
Verificar e mesclar manualmente, mantendo a versão mais completa.