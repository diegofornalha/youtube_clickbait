#!/usr/bin/env python3
"""Hook que REALMENTE persiste aprendizados no Neo4j via MCP tools.

Este hook é executado no contexto principal do Claude Code,
portanto TEM ACESSO DIRETO às ferramentas MCP.
"""

import json
import re
from datetime import datetime


async def hook(input_data, tool_use_id, context):
    """
    Hook PostToolUse que persiste automaticamente no Neo4j.

    Detecta quando:
    - Validação foi concluída → Cria memória de padrão SDK + aprendizado
    - Título foi gerado → Cria memória de fórmula + aprendizado
    - Pipeline completo → Registra execução completa

    E chama as ferramentas MCP diretamente para persistir.
    """
    tool_name = input_data.get("tool_name", "")
    is_error = input_data.get("is_error", False)
    result = input_data.get("result", "")

    # Ignorar erros
    if is_error:
        return {}

    result_str = str(result)

    # ========== DETECÇÃO 1: Validação Concluída ==========
    match_validation = re.search(r'Validação concluída com sucesso: score=(\d+\.\d+)', result_str)
    if match_validation:
        score = float(match_validation.group(1))

        # Extrair ângulo se disponível
        match_angle = re.search(r'Ângulo[:\s]+([^\n]+)', result_str, re.IGNORECASE)
        angle = match_angle.group(1).strip() if match_angle else "desconhecido"

        await persistir_validacao(score, angle, tool_use_id, context)

    # ========== DETECÇÃO 2: Título Gerado ==========
    match_title = re.search(r'Título registrado no Neo4j: CTR=(\d+\.\d+)', result_str)
    if match_title:
        ctr = float(match_title.group(1))

        # Tentar extrair o título
        match_titulo_text = re.search(r'ANTES vs DEPOIS: ([^\n]+)', result_str)
        titulo = match_titulo_text.group(0) if match_titulo_text else f"Título CTR {ctr}"

        await persistir_titulo(titulo, ctr, tool_use_id, context)

    # ========== DETECÇÃO 3: Pipeline Completo ==========
    match_pipeline = re.search(r'(\d+) operações Neo4j preparadas', result_str)
    if match_pipeline and "padrões SDK registrados" in result_str:
        op_count = int(match_pipeline.group(1))
        await persistir_pipeline_execution(op_count, tool_use_id, context)

    return {}


async def persistir_validacao(score: float, angle: str, tool_use_id: str, context):
    """Persiste validação bem-sucedida no Neo4j via MCP."""

    try:
        # IMPORTANTE: context é o objeto do Claude Code
        # Precisamos chamar as ferramentas MCP através dele

        # Criar memória de padrão SDK usado
        pattern_memory = await context.mcp_call(
            "mcp__neo4j-memory__create_memory",
            {
                "label": "Learning",
                "properties": {
                    "name": f"Validation Pattern Executed - Score {score}",
                    "category": "sdk_pattern_execution",
                    "pattern_used": "ClaudeSDKClient async validation",
                    "score_achieved": score,
                    "angle_identified": angle[:100],  # Truncar se muito longo
                    "executed_at": datetime.now().isoformat(),
                    "tool_use_id": tool_use_id,
                }
            }
        )

        # Registrar aprendizado
        await context.mcp_call(
            "mcp__neo4j-memory__learn_from_result",
            {
                "task": f"Validate idea with ClaudeSDKClient",
                "result": f"Score {score}, Angle: {angle[:50]}",
                "success": score >= 7.0,
                "category": "idea_validation"
            }
        )

        print(f"  🧠 Neo4j: Validação persistida (score={score})")

    except Exception as e:
        print(f"  ⚠️  Neo4j: Erro ao persistir validação - {e}")


async def persistir_titulo(titulo: str, ctr: float, tool_use_id: str, context):
    """Persiste título gerado no Neo4j via MCP."""

    try:
        # Criar memória do título
        await context.mcp_call(
            "mcp__neo4j-memory__create_memory",
            {
                "label": "Learning",
                "properties": {
                    "name": titulo[:100],
                    "category": "title_generated",
                    "ctr_score": ctr,
                    "executed_at": datetime.now().isoformat(),
                    "tool_use_id": tool_use_id,
                }
            }
        )

        # Registrar aprendizado
        await context.mcp_call(
            "mcp__neo4j-memory__learn_from_result",
            {
                "task": "Generate viral title with Claude SDK",
                "result": f"CTR {ctr}/10: {titulo[:80]}",
                "success": ctr >= 8.0,
                "category": "title_generation"
            }
        )

        print(f"  🧠 Neo4j: Título persistido (CTR={ctr})")

    except Exception as e:
        print(f"  ⚠️  Neo4j: Erro ao persistir título - {e}")


async def persistir_pipeline_execution(op_count: int, tool_use_id: str, context):
    """Persiste execução completa do pipeline no Neo4j."""

    try:
        # Criar memória de execução do pipeline
        await context.mcp_call(
            "mcp__neo4j-memory__create_memory",
            {
                "label": "Learning",
                "properties": {
                    "name": f"Pipeline Execution - {op_count} operations",
                    "category": "pipeline_execution",
                    "operations_prepared": op_count,
                    "pattern_used": "Multi-step validation + generation pipeline",
                    "executed_at": datetime.now().isoformat(),
                    "tool_use_id": tool_use_id,
                }
            }
        )

        # Registrar aprendizado
        await context.mcp_call(
            "mcp__neo4j-memory__learn_from_result",
            {
                "task": "Execute complete pipeline with Claude SDK",
                "result": f"{op_count} Neo4j operations prepared successfully",
                "success": True,
                "category": "pipeline_orchestration"
            }
        )

        print(f"  🧠 Neo4j: Pipeline persistido ({op_count} ops)")

    except Exception as e:
        print(f"  ⚠️  Neo4j: Erro ao persistir pipeline - {e}")
