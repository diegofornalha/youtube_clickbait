"""Orchestrator - Coordena agents especializados de forma autônoma."""

import asyncio
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable

# Adicionar claude-agent-sdk-python ao path
sdk_path = Path(__file__).parent.parent.parent / "claude-agent-sdk-python"
sys.path.insert(0, str(sdk_path))

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

logger = logging.getLogger("autonomous.orchestrator")


class AgentType(Enum):
    """Tipos de agents disponíveis."""

    VALIDATOR = "validator"
    CREATOR = "creator"
    RESEARCHER = "researcher"
    REPORTER = "reporter"


class TaskStatus(Enum):
    """Estados de uma tarefa."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class Task:
    """Tarefa a ser processada."""

    id: str
    type: AgentType
    input_data: dict[str, Any]
    priority: int = 5  # 1=alta, 10=baixa
    status: TaskStatus = TaskStatus.PENDING
    result: Any | None = None
    error: Exception | None = None
    retries: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def elapsed_time(self) -> float | None:
        """Tempo decorrido em segundos."""
        if not self.started_at:
            return None
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()


@dataclass
class AgentMetrics:
    """Métricas de performance de um agent."""

    agent_type: AgentType
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    success_rate: float = 0.0
    last_used: datetime | None = None

    def update(self, task: Task) -> None:
        """Atualiza métricas após conclusão de tarefa."""
        if task.status == TaskStatus.COMPLETED:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1

        if task.elapsed_time:
            self.total_time += task.elapsed_time
            total_tasks = self.tasks_completed + self.tasks_failed
            self.avg_time = self.total_time / total_tasks if total_tasks > 0 else 0.0

        self.success_rate = (
            self.tasks_completed / (self.tasks_completed + self.tasks_failed)
            if (self.tasks_completed + self.tasks_failed) > 0
            else 0.0
        )
        self.last_used = datetime.now()


class CircuitBreaker:
    """Circuit Breaker para proteger agents com muitas falhas."""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure: datetime | None = None
        self.is_open = False

    def record_success(self) -> None:
        """Registra sucesso."""
        self.failure_count = 0
        self.is_open = False

    def record_failure(self) -> None:
        """Registra falha."""
        self.failure_count += 1
        self.last_failure = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning(
                f"🔴 Circuit Breaker OPEN - {self.failure_count} falhas consecutivas"
            )

    def can_execute(self) -> bool:
        """Verifica se pode executar."""
        if not self.is_open:
            return True

        # Tentar fechar circuit após timeout
        if self.last_failure:
            elapsed = (datetime.now() - self.last_failure).total_seconds()
            if elapsed > self.timeout:
                logger.info("🟡 Circuit Breaker tentando HALF-OPEN")
                self.is_open = False
                self.failure_count = 0
                return True

        return False


class AgentOrchestrator:
    """
    Orquestrador de agents autônomos.

    Coordena execução de agents especializados, gerencia fila de tarefas,
    implementa circuit breaker e coleta métricas de performance.
    """

    def __init__(
        self,
        max_concurrent: int = 5,
        enable_circuit_breaker: bool = True,
    ):
        self.max_concurrent = max_concurrent
        self.tasks: dict[str, Task] = {}
        self.running_tasks: set[str] = set()
        self.metrics: dict[AgentType, AgentMetrics] = {
            agent_type: AgentMetrics(agent_type) for agent_type in AgentType
        }
        self.circuit_breakers: dict[AgentType, CircuitBreaker] = {
            agent_type: CircuitBreaker() for agent_type in AgentType
        }
        self.enable_circuit_breaker = enable_circuit_breaker
        self._shutdown = False

    async def submit_task(
        self,
        agent_type: AgentType,
        input_data: dict[str, Any],
        priority: int = 5,
    ) -> str:
        """
        Submete nova tarefa para processamento.

        Args:
            agent_type: Tipo do agent a executar
            input_data: Dados de entrada
            priority: Prioridade (1=alta, 10=baixa)

        Returns:
            Task ID
        """
        task_id = f"{agent_type.value}_{datetime.now().timestamp()}"
        task = Task(
            id=task_id,
            type=agent_type,
            input_data=input_data,
            priority=priority,
        )
        self.tasks[task_id] = task
        logger.info(f"📥 Tarefa submetida: {task_id} (prioridade={priority})")
        return task_id

    async def _execute_validator(self, input_data: dict[str, Any]) -> Any:
        """Executa Validator Agent."""
        # Import absoluto para evitar problemas de relative import
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from agents.validator import validar_ideia

        ideia = input_data.get("ideia", "")
        return await validar_ideia(ideia)

    async def _execute_creator(self, input_data: dict[str, Any]) -> Any:
        """Executa Creator Agent."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from agents.creator import gerar_titulos

        ideia = input_data.get("ideia", "")
        validacao = input_data.get("validacao")
        return await gerar_titulos(ideia, validacao)

    async def _execute_researcher(self, input_data: dict[str, Any]) -> Any:
        """Executa Researcher Agent (busca contexto Neo4j)."""
        # Placeholder - implementar busca no Neo4j
        logger.info(f"🔍 Researcher: buscando contexto sobre {input_data}")
        await asyncio.sleep(1)  # Simula pesquisa
        return {"context": "Contexto do Neo4j", "sources": ["mem1", "mem2"]}

    async def _execute_reporter(self, input_data: dict[str, Any]) -> Any:
        """Executa Reporter Agent (cria relatório)."""
        # Placeholder - implementar geração de relatório
        logger.info(f"📊 Reporter: gerando relatório para {input_data}")
        await asyncio.sleep(0.5)  # Simula geração
        return {"report": "Relatório gerado", "format": "markdown"}

    async def _execute_task(self, task: Task) -> None:
        """Executa uma tarefa usando o agent apropriado."""
        agent_type = task.type
        circuit_breaker = self.circuit_breakers[agent_type]

        # Verificar circuit breaker
        if self.enable_circuit_breaker and not circuit_breaker.can_execute():
            logger.error(
                f"❌ Circuit Breaker OPEN - não executando {agent_type.value}"
            )
            task.status = TaskStatus.FAILED
            task.error = Exception("Circuit Breaker OPEN")
            return

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self.running_tasks.add(task.id)

        logger.info(f"▶️  Executando: {task.id}")

        try:
            # Despachar para agent específico
            if agent_type == AgentType.VALIDATOR:
                result = await self._execute_validator(task.input_data)
            elif agent_type == AgentType.CREATOR:
                result = await self._execute_creator(task.input_data)
            elif agent_type == AgentType.RESEARCHER:
                result = await self._execute_researcher(task.input_data)
            elif agent_type == AgentType.REPORTER:
                result = await self._execute_reporter(task.input_data)
            else:
                raise ValueError(f"Agent type desconhecido: {agent_type}")

            # Sucesso
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            circuit_breaker.record_success()

            logger.info(
                f"✅ Concluído: {task.id} em {task.elapsed_time:.1f}s"
            )

        except Exception as e:
            logger.error(f"❌ Falha: {task.id} - {e}")
            task.error = e
            circuit_breaker.record_failure()

            # Retry?
            if task.retries < task.max_retries:
                task.status = TaskStatus.RETRY
                task.retries += 1
                logger.info(
                    f"🔄 Agendando retry {task.retries}/{task.max_retries}: {task.id}"
                )
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()

        finally:
            self.running_tasks.discard(task.id)
            self.metrics[agent_type].update(task)

    async def process_queue(self) -> None:
        """Processa fila de tarefas continuamente."""
        logger.info("🚀 Iniciando processamento de fila")

        while not self._shutdown:
            # Pegar tarefas pendentes
            pending = [
                task
                for task in self.tasks.values()
                if task.status in (TaskStatus.PENDING, TaskStatus.RETRY)
            ]

            if not pending:
                await asyncio.sleep(1)  # Aguardar novas tarefas
                continue

            # Ordenar por prioridade
            pending.sort(key=lambda t: t.priority)

            # Executar até max_concurrent
            while len(self.running_tasks) < self.max_concurrent and pending:
                task = pending.pop(0)
                asyncio.create_task(self._execute_task(task))

            await asyncio.sleep(0.5)

        logger.info("🛑 Processamento de fila encerrado")

    async def shutdown(self) -> None:
        """Para o orchestrator gracefully."""
        logger.info("🛑 Shutdown solicitado")
        self._shutdown = True

        # Aguardar tarefas em execução
        while self.running_tasks:
            logger.info(
                f"⏳ Aguardando {len(self.running_tasks)} tarefas finalizarem..."
            )
            await asyncio.sleep(1)

        logger.info("✅ Shutdown concluído")

    def get_metrics(self) -> dict[str, Any]:
        """Retorna métricas de todos os agents."""
        return {
            "agents": {
                agent_type.value: {
                    "completed": metrics.tasks_completed,
                    "failed": metrics.tasks_failed,
                    "success_rate": f"{metrics.success_rate * 100:.1f}%",
                    "avg_time": f"{metrics.avg_time:.2f}s",
                    "total_time": f"{metrics.total_time:.1f}s",
                    "last_used": metrics.last_used.isoformat() if metrics.last_used else None,
                }
                for agent_type, metrics in self.metrics.items()
            },
            "queue": {
                "total_tasks": len(self.tasks),
                "running": len(self.running_tasks),
                "pending": len(
                    [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
                ),
                "completed": len(
                    [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
                ),
                "failed": len(
                    [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
                ),
            },
        }

    def print_status(self) -> None:
        """Imprime status do orchestrator."""
        metrics = self.get_metrics()

        print("\n┌─────────────────────────────────────┐")
        print("│  ORCHESTRATOR STATUS                │")
        print("├─────────────────────────────────────┤")

        # Queue
        q = metrics["queue"]
        print(f"│  Tasks: {q['total_tasks']} total")
        print(f"│  Running: {q['running']}/{self.max_concurrent}")
        print(f"│  Pending: {q['pending']}")
        print(f"│  Completed: {q['completed']}")
        print(f"│  Failed: {q['failed']}")
        print("│")

        # Agents
        print("│  Agents:")
        for agent_name, agent_metrics in metrics["agents"].items():
            status = "✅" if float(agent_metrics["success_rate"].rstrip("%")) > 80 else "⚠️"
            print(
                f"│  {status} {agent_name}: {agent_metrics['completed']} tasks "
                f"({agent_metrics['success_rate']})"
            )

        print("└─────────────────────────────────────┘\n")
