"""Sistema Autônomo - Integração completa de Orchestrator + Hooks + Queue."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from autonomous.hooks import AutoApprovalHooks
from autonomous.orchestrator import AgentOrchestrator, AgentType, TaskStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("autonomous_system")


class AutonomousSystem:
    """
    Sistema Autônomo Completo.

    Combina:
    - Orchestrator: Coordena agents especializados
    - Hooks: Auto-aprovação e registro automático
    - Queue Manager: Monitora fila de tarefas
    - Auto-learning: Aprende com resultados (Neo4j)
    """

    def __init__(
        self,
        queue_path: str | Path = "queue/tasks",
        output_path: str | Path = "outputs/autonomous",
        max_concurrent_agents: int = 5,
        enable_hooks: bool = True,
        enable_neo4j: bool = True,
        auto_approve_tools: list[str] | None = None,
    ):
        """
        Inicializa o sistema autônomo.

        Args:
            queue_path: Path para fila de tarefas (JSON files)
            output_path: Path para outputs
            max_concurrent_agents: Máximo de agents em paralelo
            enable_hooks: Ativar hooks automáticos
            enable_neo4j: Ativar aprendizado no Neo4j
            auto_approve_tools: Tools para auto-aprovar
        """
        self.queue_path = Path(queue_path)
        self.output_path = Path(output_path)
        self.max_concurrent_agents = max_concurrent_agents
        self.enable_hooks = enable_hooks
        self.enable_neo4j = enable_neo4j

        # Criar diretórios
        self.queue_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Componentes
        self.orchestrator = AgentOrchestrator(max_concurrent=max_concurrent_agents)
        self.hooks = AutoApprovalHooks(auto_approve_tools=auto_approve_tools)

        self._running = False
        self._queue_monitor_task: asyncio.Task | None = None
        self._status_monitor_task: asyncio.Task | None = None

        logger.info("🤖 Sistema Autônomo inicializado")
        logger.info(f"📁 Queue: {self.queue_path}")
        logger.info(f"📁 Output: {self.output_path}")

    async def add_task(
        self,
        task_type: str,
        input_data: dict[str, Any],
        priority: int = 5,
    ) -> str:
        """
        Adiciona tarefa ao sistema.

        Args:
            task_type: Tipo da tarefa (validator, creator, etc.)
            input_data: Dados de entrada
            priority: Prioridade (1=alta, 10=baixa)

        Returns:
            Task ID
        """
        # Mapear string para AgentType
        agent_type_map = {
            "validator": AgentType.VALIDATOR,
            "creator": AgentType.CREATOR,
            "researcher": AgentType.RESEARCHER,
            "reporter": AgentType.REPORTER,
        }

        agent_type = agent_type_map.get(task_type)
        if not agent_type:
            raise ValueError(f"Tipo de tarefa inválido: {task_type}")

        # Submeter ao orchestrator
        task_id = await self.orchestrator.submit_task(
            agent_type=agent_type,
            input_data=input_data,
            priority=priority,
        )

        # Salvar também como arquivo JSON na fila
        task_file = self.queue_path / f"{task_id}.json"
        task_file.write_text(
            json.dumps(
                {
                    "id": task_id,
                    "type": task_type,
                    "input_data": input_data,
                    "priority": priority,
                    "created_at": datetime.now().isoformat(),
                    "status": "pending",
                },
                indent=2,
            )
        )

        logger.info(f"📥 Tarefa adicionada: {task_id}")
        return task_id

    async def _monitor_queue(self) -> None:
        """Monitora fila de arquivos JSON e adiciona tarefas automaticamente."""
        logger.info("👀 Iniciando monitoramento de fila")

        processed_files = set()

        while self._running:
            # Escanear arquivos JSON na fila
            for task_file in self.queue_path.glob("*.json"):
                if task_file in processed_files:
                    continue

                try:
                    task_data = json.loads(task_file.read_text())

                    # Adicionar tarefa ao orchestrator
                    await self.add_task(
                        task_type=task_data["type"],
                        input_data=task_data["input_data"],
                        priority=task_data.get("priority", 5),
                    )

                    processed_files.add(task_file)
                    logger.info(f"📄 Arquivo processado: {task_file.name}")

                except Exception as e:
                    logger.error(f"❌ Erro ao processar {task_file.name}: {e}")

            await asyncio.sleep(2)  # Checar a cada 2s

    async def _monitor_status(self) -> None:
        """Monitora status do sistema e imprime periodicamente."""
        logger.info("📊 Iniciando monitoramento de status")

        while self._running:
            await asyncio.sleep(30)  # A cada 30s

            # Imprimir status
            self.orchestrator.print_status()
            self.hooks.print_statistics()

    async def start(self) -> None:
        """Inicia o sistema autônomo."""
        logger.info("🚀 Iniciando sistema autônomo")

        self._running = True

        # Iniciar tasks de monitoramento
        self._queue_monitor_task = asyncio.create_task(self._monitor_queue())
        self._status_monitor_task = asyncio.create_task(self._monitor_status())

        # Iniciar processamento de fila
        await self.orchestrator.process_queue()

    async def stop(self) -> None:
        """Para o sistema autônomo gracefully."""
        logger.info("🛑 Parando sistema autônomo")

        self._running = False

        # Cancelar tasks de monitoramento
        if self._queue_monitor_task:
            self._queue_monitor_task.cancel()
        if self._status_monitor_task:
            self._status_monitor_task.cancel()

        # Parar orchestrator
        await self.orchestrator.shutdown()

        logger.info("✅ Sistema autônomo parado")

    def get_status(self) -> dict[str, Any]:
        """Retorna status completo do sistema."""
        return {
            "running": self._running,
            "orchestrator": self.orchestrator.get_metrics(),
            "hooks_enabled": self.enable_hooks,
            "neo4j_enabled": self.enable_neo4j,
            "queue_path": str(self.queue_path),
            "output_path": str(self.output_path),
        }

    def print_dashboard(self) -> None:
        """Imprime dashboard do sistema."""
        status = self.get_status()

        print("\n" + "=" * 50)
        print("🤖  AUTONOMOUS SYSTEM DASHBOARD")
        print("=" * 50)
        print(f"Status: {'🟢 RUNNING' if status['running'] else '🔴 STOPPED'}")
        print(f"Hooks: {'✅ Enabled' if status['hooks_enabled'] else '❌ Disabled'}")
        print(f"Neo4j: {'✅ Enabled' if status['neo4j_enabled'] else '❌ Disabled'}")
        print()

        # Orchestrator status
        self.orchestrator.print_status()

        # Hooks statistics
        self.hooks.print_statistics()

        print("=" * 50 + "\n")


# Exemplo de uso
async def example_usage():
    """Exemplo de uso do sistema autônomo."""
    # Criar sistema
    system = AutonomousSystem(
        queue_path="queue/tasks",
        output_path="outputs/autonomous",
        max_concurrent_agents=3,
        enable_hooks=True,
        auto_approve_tools=["Read", "Grep", "Glob"],
    )

    # Adicionar algumas tarefas
    await system.add_task(
        task_type="validator",
        input_data={"ideia": "streaming do claude sdk"},
        priority=1,
    )

    await system.add_task(
        task_type="creator",
        input_data={
            "ideia": "hooks do claude sdk",
            "validacao": {"score": 8.5},
        },
        priority=2,
    )

    # Processar por 60 segundos
    logger.info("▶️  Processando por 60 segundos...")

    async def run_for_time():
        await asyncio.sleep(60)
        await system.stop()

    # Executar sistema e timer em paralelo
    await asyncio.gather(
        system.start(),
        run_for_time(),
    )

    # Dashboard final
    system.print_dashboard()


if __name__ == "__main__":
    import anyio

    anyio.run(example_usage)
