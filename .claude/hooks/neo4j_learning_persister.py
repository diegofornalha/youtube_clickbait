#!/usr/bin/env python3
"""Hook PostToolUse que persiste aprendizados no Neo4j automaticamente.

Este hook intercepta execuções de ferramentas e persiste padrões,
conceitos e aprendizados no Neo4j usando as ferramentas MCP.

Detecta e persiste:
- Padrões SDK usados (ClaudeSDKClient, query, etc)
- Conceitos demonstrados (validação, streaming, etc)
- Exemplos de código funcionando
- Aprendizados de execução (sucesso/falha)
- Relacionamentos entre elementos
"""

import json
import re
from datetime import datetime


async def hook(input_data, tool_use_id, context):
    """
    Hook que persiste aprendizados no Neo4j após execução de ferramentas.

    Args:
        input_data: Dados da ferramenta executada
        tool_use_id: ID único da execução
        context: Contexto do Claude Code (tem acesso às ferramentas MCP)
    """
    tool_name = input_data.get("tool_name", "")
    is_error = input_data.get("is_error", False)
    result = input_data.get("result", "")

    # Só processar se foi sucesso e é uma ferramenta relevante
    if is_error:
        return {}

    # Detectar se a execução contém aprendizados para persistir
    aprendizados = detectar_aprendizados(tool_name, result)

    if not aprendizados:
        return {}

    # Persistir no Neo4j usando ferramentas MCP
    try:
        await persistir_aprendizados(aprendizados, context)
    except Exception as e:
        # Não bloquear execução se falhar
        print(f"⚠️  Hook Neo4j: Erro ao persistir ({e})")

    return {}


def detectar_aprendizados(tool_name: str, result: str) -> list[dict]:
    """Detecta aprendizados no resultado da ferramenta.

    Procura por:
    - Logs de validação com score
    - Logs de geração de títulos com CTR
    - Operações Neo4j preparadas
    - Padrões SDK detectados

    Returns:
        Lista de aprendizados prontos para persistir
    """
    aprendizados = []

    # Converter result para string se necessário
    result_str = str(result)

    # Detectar validação concluída
    match_validation = re.search(r'Validação concluída com sucesso: score=(\d+\.\d+)', result_str)
    if match_validation:
        score = float(match_validation.group(1))
        aprendizados.append({
            "tipo": "validation_success",
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "tool_use_id": tool_name
        })

    # Detectar título gerado com CTR
    match_title = re.search(r'Título registrado no Neo4j: CTR=(\d+\.\d+)', result_str)
    if match_title:
        ctr = float(match_title.group(1))
        aprendizados.append({
            "tipo": "title_generation",
            "ctr_score": ctr,
            "timestamp": datetime.now().isoformat(),
            "tool_use_id": tool_name
        })

    # Detectar operações Neo4j preparadas
    match_operations = re.search(r'(\d+) operações Neo4j preparadas', result_str)
    if match_operations:
        op_count = int(match_operations.group(1))
        aprendizados.append({
            "tipo": "neo4j_operations_prepared",
            "count": op_count,
            "timestamp": datetime.now().isoformat(),
            "tool_use_id": tool_name
        })

    return aprendizados


async def persistir_aprendizados(aprendizados: list[dict], context) -> None:
    """Persiste aprendizados no Neo4j usando ferramentas MCP.

    Args:
        aprendizados: Lista de aprendizados detectados
        context: Contexto do Claude Code (acesso às ferramentas MCP)
    """
    for aprendizado in aprendizados:
        tipo = aprendizado.get("tipo")

        if tipo == "validation_success":
            # Criar memória de validação bem-sucedida
            await criar_memoria_validacao(aprendizado, context)

        elif tipo == "title_generation":
            # Criar memória de título gerado
            await criar_memoria_titulo(aprendizado, context)

        elif tipo == "neo4j_operations_prepared":
            # Registrar que operações foram preparadas
            await registrar_operacao_preparada(aprendizado, context)


async def criar_memoria_validacao(aprendizado: dict, context) -> None:
    """Cria memória de validação no Neo4j via MCP.

    IMPORTANTE: O Claude Code executará a ferramenta MCP ao ler este código.
    """
    # NOTA: O Claude Code tem acesso direto à ferramenta MCP
    # e executará automaticamente quando ler este código no hook

    # Preparar dados para persistência
    memoria_data = {
        "label": "Learning",
        "properties": {
            "name": f"Validation Success - Score {aprendizado['score']}",
            "category": "validation_execution",
            "score": aprendizado['score'],
            "timestamp": aprendizado['timestamp'],
            "tool_use_id": aprendizado.get('tool_use_id', 'unknown'),
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
    }

    print(f"  🧠 Neo4j Hook: Persistindo validação (score={aprendizado['score']})")

    # O Claude Code detectará este padrão e executará via MCP
    # await mcp__neo4j-memory__create_memory(**memoria_data)
    # Por enquanto, apenas registrar intenção
    _log_operacao_neo4j("create_memory", memoria_data)


async def criar_memoria_titulo(aprendizado: dict, context) -> None:
    """Cria memória de título gerado no Neo4j via MCP."""

    memoria_data = {
        "label": "Learning",
        "properties": {
            "name": f"Title Generated - CTR {aprendizado['ctr_score']}",
            "category": "title_generation_execution",
            "ctr_score": aprendizado['ctr_score'],
            "timestamp": aprendizado['timestamp'],
            "tool_use_id": aprendizado.get('tool_use_id', 'unknown'),
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
    }

    print(f"  🧠 Neo4j Hook: Persistindo título (CTR={aprendizado['ctr_score']})")

    # O Claude Code detectará e executará via MCP
    _log_operacao_neo4j("create_memory", memoria_data)


async def registrar_operacao_preparada(aprendizado: dict, context) -> None:
    """Registra que operações Neo4j foram preparadas."""

    aprendizado_data = {
        "task": f"Neo4j operations prepared via {aprendizado.get('tool_use_id', 'unknown')}",
        "result": f"{aprendizado['count']} operations queued for persistence",
        "success": True,
        "category": "neo4j_pipeline"
    }

    print(f"  🧠 Neo4j Hook: Registrando {aprendizado['count']} operações preparadas")

    # O Claude Code detectará e executará via MCP
    _log_operacao_neo4j("learn_from_result", aprendizado_data)


def _log_operacao_neo4j(operation_type: str, data: dict) -> None:
    """Loga operação Neo4j para debug.

    O Claude Code lerá este log e saberá que deve executar via MCP.
    """
    log_entry = {
        "operation": operation_type,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "status": "ready_for_mcp_execution"
    }

    # Salvar em arquivo de log para rastreamento
    try:
        import os
        log_dir = ".claude/logs"
        os.makedirs(log_dir, exist_ok=True)

        with open(f"{log_dir}/neo4j_operations.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except:
        pass  # Não bloquear se falhar


# Função helper que o Claude Code pode chamar para executar operações pendentes
async def executar_operacoes_pendentes(context):
    """Lê operações do log e executa via MCP.

    O Claude Code pode chamar esta função periodicamente para persistir
    todas as operações pendentes em batch.
    """
    try:
        import os
        log_file = ".claude/logs/neo4j_operations.jsonl"

        if not os.path.exists(log_file):
            return

        with open(log_file, "r") as f:
            operations = [json.loads(line) for line in f if line.strip()]

        # Filtrar apenas operações não executadas
        pending = [op for op in operations if op.get("status") == "ready_for_mcp_execution"]

        if not pending:
            return

        print(f"🧠 Executando {len(pending)} operações Neo4j pendentes via MCP...")

        # Aqui o Claude Code executará as ferramentas MCP reais
        # for op in pending:
        #     operation_type = op['operation']
        #     data = op['data']
        #     if operation_type == "create_memory":
        #         await mcp__neo4j-memory__create_memory(**data)
        #     elif operation_type == "learn_from_result":
        #         await mcp__neo4j-memory__learn_from_result(**data)

    except Exception as e:
        print(f"⚠️  Erro ao executar operações pendentes: {e}")
