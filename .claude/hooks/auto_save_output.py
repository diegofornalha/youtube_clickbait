#!/usr/bin/env python3
"""
Auto Save Output Hook
Salva automaticamente outputs gerados pelos agentes
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def main():
    """Hook PostToolUse que salva outputs automaticamente"""

    # Ler input do hook via stdin
    hook_input = json.loads(sys.stdin.read())

    tool_name = hook_input.get('tool', '')
    file_path = hook_input.get('input', {}).get('file_path', '')
    content = hook_input.get('input', {}).get('content', '')

    # Só processar se for escrita de arquivo
    if tool_name == 'Write' and file_path and content:
        # Verificar se é output de agente (em outputs/)
        if 'outputs/' in file_path:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Log da operação
            log_entry = {
                'timestamp': timestamp,
                'file': file_path,
                'size': len(content),
                'type': 'agent_output'
            }

            # Salvar log em outputs/execution_log.jsonl
            log_file = Path('outputs/execution_log.jsonl')
            log_file.parent.mkdir(exist_ok=True)

            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            # Criar backup em outputs/backups/ se for importante
            if any(keyword in file_path for keyword in ['final', 'script', 'analysis']):
                backup_dir = Path('outputs/backups')
                backup_dir.mkdir(exist_ok=True)

                original_path = Path(file_path)
                backup_name = f"{original_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{original_path.suffix}"
                backup_path = backup_dir / backup_name

                backup_path.write_text(content)

                print(f"✅ Output salvo: {file_path}", file=sys.stderr)
                print(f"💾 Backup criado: {backup_path}", file=sys.stderr)

    # Retornar output padrão do hook
    output = {
        "decision": "continue"
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
