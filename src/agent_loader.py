"""Carrega agents de .claude/agents/ para usar no sistema autônomo."""

import sys
from pathlib import Path
from typing import Any

# Adicionar SDK ao path
sdk_path = Path(__file__).parent.parent / "claude-agent-sdk-python"
sys.path.insert(0, str(sdk_path))

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, ClaudeSDKClient


def load_agents_from_directory(agents_dir: str | Path = ".claude/agents") -> dict[str, AgentDefinition]:
    """
    Carrega agents de arquivos .md no diretório.

    Args:
        agents_dir: Diretório com arquivos .md dos agents

    Returns:
        Dict com nome_agent -> AgentDefinition
    """
    agents_path = Path(agents_dir)
    agents: dict[str, AgentDefinition] = {}

    if not agents_path.exists():
        return agents

    for agent_file in agents_path.glob("*.md"):
        agent_name = agent_file.stem  # nome sem .md
        prompt_content = agent_file.read_text()

        # Extrair descrição (primeira linha após # título)
        lines = prompt_content.split("\n")
        description = "Agent especializado"

        for line in lines:
            if line.startswith("**Role**:") or line.startswith("**Quando usar**:"):
                description = line.split(":", 1)[1].strip()
                break

        # Criar AgentDefinition
        agent_def = AgentDefinition(
            description=description,
            prompt=prompt_content,
            tools=None,  # Herda tools do pai
            model="inherit",  # Herda modelo do pai
        )

        agents[agent_name] = agent_def

    return agents


async def invoke_subagent(
    agent_name: str,
    prompt: str,
    agents: dict[str, AgentDefinition],
    parent_options: ClaudeAgentOptions | None = None,
) -> str:
    """
    Invoca um subagent e retorna a resposta.

    Args:
        agent_name: Nome do agent (ex: 'idea_validator')
        prompt: Prompt para o agent
        agents: Dict com definições dos agents
        parent_options: Opções do cliente pai

    Returns:
        Resposta completa do agent
    """
    from claude_agent_sdk import AssistantMessage, TextBlock

    # Configurar opções incluindo agents
    options = parent_options or ClaudeAgentOptions()
    options.agents = agents

    # Prompt para invocar o subagent
    # O Claude Code usa a Task tool internamente para invocar subagents
    subagent_prompt = f"""Use o agent {agent_name} para processar:

{prompt}

IMPORTANTE: Execute completamente o agent e retorne o resultado.
"""

    full_response = ""

    async with ClaudeSDKClient(options=options) as client:
        await client.query(subagent_prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        full_response += block.text

    return full_response


# Exemplo de uso
async def example_usage():
    """Exemplo de como usar agents carregados."""
    import anyio

    # 1. Carregar agents de .claude/agents/
    agents = load_agents_from_directory(".claude/agents")

    print("📁 Agents carregados:")
    for name, agent in agents.items():
        print(f"  - {name}: {agent.description[:60]}...")
    print()

    # 2. Usar idea_validator
    if "idea_validator" in agents:
        print("🔍 Invocando idea_validator...\n")

        result = await invoke_subagent(
            agent_name="idea_validator",
            prompt="streaming do claude sdk",
            agents=agents,
        )

        print(f"Resultado:\n{result[:200]}...\n")


if __name__ == "__main__":
    import anyio
    anyio.run(example_usage)
