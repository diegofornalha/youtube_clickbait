"""Sistema robusto de tratamento de erros para Claude Agent SDK."""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, TypeVar

from claude_agent_sdk import (
    CLIConnectionError,
    CLIJSONDecodeError,
    CLINotFoundError,
    ClaudeSDKError,
    ProcessError,
)

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("youtube_agent")


class ErrorSeverity(Enum):
    """Níveis de severidade de erro."""

    CRITICAL = "critical"  # Sistema não pode continuar
    HIGH = "high"  # Operação falhou mas sistema continua
    MEDIUM = "medium"  # Erro recuperável com retry
    LOW = "low"  # Aviso, não impacta funcionalidade


class ErrorCategory(Enum):
    """Categorias de erro para análise."""

    CONNECTION = "connection"  # Problemas de conexão com CLI
    PARSING = "parsing"  # Erros de parse JSON/mensagens
    PROCESS = "process"  # Falhas no processo CLI
    VALIDATION = "validation"  # Dados inválidos
    TIMEOUT = "timeout"  # Timeouts
    UNKNOWN = "unknown"  # Erro desconhecido


class ErrorContext:
    """Contexto detalhado de um erro."""

    def __init__(
        self,
        error: Exception,
        operation: str,
        severity: ErrorSeverity,
        category: ErrorCategory,
        retry_count: int = 0,
        max_retries: int = 3,
        metadata: dict[str, Any] | None = None,
    ):
        self.error = error
        self.operation = operation
        self.severity = severity
        self.category = category
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def should_retry(self) -> bool:
        """Verifica se deve tentar novamente."""
        # Não retry para erros críticos
        if self.severity == ErrorSeverity.CRITICAL:
            return False

        # Não retry se atingiu limite
        if self.retry_count >= self.max_retries:
            return False

        # Retry apenas para categorias recuperáveis
        recoverable = {
            ErrorCategory.CONNECTION,
            ErrorCategory.TIMEOUT,
            ErrorCategory.PROCESS,
        }
        return self.category in recoverable

    def get_backoff_delay(self) -> float:
        """Calcula delay com backoff exponencial."""
        # Base: 1s, 2s, 4s, 8s...
        base_delay = 2**self.retry_count
        # Adicionar jitter (±20%)
        import random

        jitter = random.uniform(0.8, 1.2)
        return min(base_delay * jitter, 30.0)  # Max 30s

    def to_dict(self) -> dict[str, Any]:
        """Serializa contexto para logging."""
        return {
            "error_type": type(self.error).__name__,
            "error_message": str(self.error),
            "operation": self.operation,
            "severity": self.severity.value,
            "category": self.category.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


def categorize_error(error: Exception) -> tuple[ErrorSeverity, ErrorCategory]:
    """Categoriza erro do Claude SDK."""
    if isinstance(error, CLINotFoundError):
        return ErrorSeverity.CRITICAL, ErrorCategory.CONNECTION

    if isinstance(error, CLIConnectionError):
        return ErrorSeverity.HIGH, ErrorCategory.CONNECTION

    if isinstance(error, ProcessError):
        # Exit code 0 não é erro
        if hasattr(error, "exit_code") and error.exit_code == 0:
            return ErrorSeverity.LOW, ErrorCategory.UNKNOWN
        return ErrorSeverity.HIGH, ErrorCategory.PROCESS

    if isinstance(error, CLIJSONDecodeError):
        return ErrorSeverity.MEDIUM, ErrorCategory.PARSING

    if isinstance(error, ClaudeSDKError):
        return ErrorSeverity.MEDIUM, ErrorCategory.UNKNOWN

    if isinstance(error, asyncio.TimeoutError):
        return ErrorSeverity.MEDIUM, ErrorCategory.TIMEOUT

    if isinstance(error, ValueError):
        return ErrorSeverity.MEDIUM, ErrorCategory.VALIDATION

    # Erro genérico
    return ErrorSeverity.HIGH, ErrorCategory.UNKNOWN


async def handle_error_with_retry(
    context: ErrorContext,
    fallback: Callable[[], Any] | None = None,
) -> Any:
    """
    Processa erro com retry automático.

    Args:
        context: Contexto do erro
        fallback: Função fallback se todos os retries falharem

    Returns:
        None se deve fazer retry, resultado do fallback caso contrário
    """
    # Log estruturado
    log_data = context.to_dict()

    if context.retry_count == 0:
        logger.error(f"❌ Erro em {context.operation}", extra=log_data)
    else:
        logger.warning(
            f"🔄 Retry {context.retry_count}/{context.max_retries} - {context.operation}",
            extra=log_data,
        )

    # Verificar se deve retry
    if context.should_retry():
        delay = context.get_backoff_delay()
        logger.info(
            f"⏳ Aguardando {delay:.1f}s antes de retry...",
            extra={"delay": delay, "operation": context.operation},
        )
        await asyncio.sleep(delay)
        return None  # Sinal para fazer retry

    # Esgotou retries
    logger.error(
        f"💥 Falha após {context.retry_count} tentativas - {context.operation}",
        extra=log_data,
    )

    # Executar fallback se disponível
    if fallback:
        logger.info(
            f"🔧 Executando fallback para {context.operation}",
            extra={"operation": context.operation},
        )
        return fallback()

    # Re-raise erro original
    raise context.error


T = TypeVar("T")


def with_retry(
    operation_name: str,
    max_retries: int = 3,
    fallback: Callable[[], Any] | None = None,
):
    """
    Decorator para adicionar retry automático a funções async.

    Args:
        operation_name: Nome da operação (para logging)
        max_retries: Número máximo de retries
        fallback: Função fallback opcional

    Example:
        @with_retry("validar_ideia", max_retries=3)
        async def validar_ideia(ideia: str):
            # código que pode falhar
            pass
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retry_count = 0

            while True:
                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    severity, category = categorize_error(e)

                    context = ErrorContext(
                        error=e,
                        operation=operation_name,
                        severity=severity,
                        category=category,
                        retry_count=retry_count,
                        max_retries=max_retries,
                        metadata={
                            "function": func.__name__,
                            "args_count": len(args),
                            "kwargs_keys": list(kwargs.keys()),
                        },
                    )

                    result = await handle_error_with_retry(context, fallback)

                    # Se result é None, deve fazer retry
                    if result is None:
                        retry_count += 1
                        continue

                    # Retornar resultado do fallback
                    return result

        return wrapper

    return decorator


# Fallbacks específicos para cada tipo de operação
def validation_fallback(ideia: str) -> dict[str, Any]:
    """Fallback para validação de ideias."""
    logger.warning(f"⚠️ Usando validação fallback para: {ideia}")
    return {
        "original_idea": ideia,
        "refined_idea": ideia,
        "best_angle": "demonstração prática",
        "score": 6.0,
        "score_breakdown": {
            "viral_potential": 6.0,
            "technical_value": 6.0,
            "audience_fit": 6.0,
            "production_feasibility": 6.0,
            "uniqueness": 6.0,
        },
        "viral_factors": ["Conteúdo técnico", "Claude SDK"],
        "improvements_needed": ["Validação manual necessária"],
        "estimated_metrics": {
            "views": "5k-15k",
            "ctr": "3-5%",
            "retention": "40-60%",
        },
        "recommended_format": "tutorial",
        "title_suggestions": [
            f"Claude SDK: {ideia.capitalize()}",
            f"Como usar Claude SDK para {ideia}",
            f"Tutorial: {ideia} com Claude SDK",
        ],
        "verdict": "NEEDS_WORK",
        "next_steps": ["Revisar ideia", "Validar manualmente", "Refinar ângulo"],
    }


def title_generation_fallback(ideia: str) -> dict[str, Any]:
    """Fallback para geração de títulos."""
    logger.warning(f"⚠️ Usando geração de títulos fallback para: {ideia}")
    return {
        "ideia_original": ideia,
        "titulos_virais": [
            {
                "titulo": f"🚀 Claude SDK: {ideia.capitalize()} - Tutorial Completo",
                "ctr_score": 7.0,
                "gatilho": "Curiosidade",
                "formula": "Básica",
                "emoji": "🚀",
            },
            {
                "titulo": f"Como usar Claude SDK para {ideia}",
                "ctr_score": 6.5,
                "gatilho": "Utilidade",
                "formula": "How-to",
                "emoji": "",
            },
            {
                "titulo": f"⚡ {ideia} com Claude SDK - Guia Prático",
                "ctr_score": 7.2,
                "gatilho": "Eficiência",
                "formula": "Guia",
                "emoji": "⚡",
            },
        ],
        "recomendado": f"🚀 Claude SDK: {ideia.capitalize()} - Tutorial Completo",
        "thumbnail_hint": "Fallback: código + logo Claude SDK",
    }


# Exportar utilitários
__all__ = [
    "ErrorSeverity",
    "ErrorCategory",
    "ErrorContext",
    "categorize_error",
    "handle_error_with_retry",
    "with_retry",
    "validation_fallback",
    "title_generation_fallback",
    "logger",
]
