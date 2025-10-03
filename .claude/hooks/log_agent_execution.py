#!/usr/bin/env python3
"""
Log Agent Execution Hook
Registra execuções de agentes para tracking de performance
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def main():
    """Hook PostToolUse que loga execuções de agentes"""

    # Ler input do hook via stdin
    hook_input = json.loads(sys.stdin.read())

    tool_name = hook_input.get('tool', '')
    agent_name = hook_input.get('input', {}).get('subagent_type', '')
    prompt = hook_input.get('input', {}).get('prompt', '')

    # Só processar execuções de agentes via Task tool
    if tool_name == 'Task' and agent_name:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Determinar tipo de agente
        agent_type_map = {
            'tech_researcher': '📊 Research',
            'clickbait_specialist': '🎯 Titles',
            'script_writer': '✍️  Script',
            'content_optimizer': '📈 Optimize'
        }

        agent_type = agent_type_map.get(agent_name, '🤖 Agent')

        # Log da execução
        log_entry = {
            'timestamp': timestamp,
            'agent': agent_name,
            'agent_type': agent_type,
            'prompt_preview': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'status': 'started'
        }

        # Salvar log em outputs/agent_executions.jsonl
        log_file = Path('outputs/agent_executions.jsonl')
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        print(f"{agent_type} Agente {agent_name} iniciado", file=sys.stderr)

        # Atualizar métricas
        metrics_file = Path('outputs/metrics/agent_metrics.json')
        metrics_file.parent.mkdir(exist_ok=True)

        if metrics_file.exists():
            metrics = json.loads(metrics_file.read_text())
        else:
            metrics = {
                'total_executions': 0,
                'by_agent': {}
            }

        metrics['total_executions'] += 1
        if agent_name not in metrics['by_agent']:
            metrics['by_agent'][agent_name] = 0
        metrics['by_agent'][agent_name] += 1
        metrics['last_execution'] = timestamp

        metrics_file.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))

    # Retornar output padrão do hook
    output = {
        "decision": "continue"
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
