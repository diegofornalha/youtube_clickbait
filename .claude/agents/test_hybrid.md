# Test Hybrid Agent - Exemplo de Integração Agente + Skill

## Descrição
Agente de teste que demonstra como usar skills do projeto local.

## Como Funciona

Este agente:
1. Recebe uma ideia de vídeo
2. **USA A SKILL** `viral-youtube-titles` para gerar títulos
3. Adiciona sua própria lógica (validação, Neo4j, etc)

## Workflow

### ETAPA 1: Usar Skill Local
```python
# Chamar script da skill
python /Users/2a/Desktop/youtube_clickbait/.claude/skills/viral-youtube-titles/scripts/test_simple.py "[IDEIA]"
```

### ETAPA 2: Adicionar Lógica do Agente
- Validar títulos gerados
- Calcular CTR score
- Salvar no Neo4j
- Gerar keywords SEO

## Exemplo de Uso

```
User: "Gere títulos sobre React hooks"
Agente:
1. Chama skill → gera títulos base
2. Aplica lógica própria → melhora títulos
3. Persiste no Neo4j → salva aprendizados
```

## Vantagens da Abordagem Híbrida

- **Skill**: Lógica reutilizável (fórmulas de títulos)
- **Agente**: Orquestração complexa (validação, Neo4j, decisões)
- **Modular**: Skill pode ser atualizada independentemente
- **Eficiente**: Scripts executam sem carregar contexto

## Comando para Testar

```bash
# Agente pode executar skill assim:
bash -c "cd /Users/2a/Desktop/youtube_clickbait/.claude/skills/viral-youtube-titles/scripts && python test_simple.py 'React Hooks'"
```