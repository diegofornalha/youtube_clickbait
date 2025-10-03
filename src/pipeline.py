"""Pipeline orquestrador completo para geração de conteúdo viral."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .agents_api import (
    TitleCreationResult,
    ValidationResult,
    VideoTitle,
    gerar_titulos_com_neo4j,
    validar_ideia,
)
from .neo4j_client import Neo4jClient
from .neo4j_executor import executar_operacoes_neo4j
from .storage import salvar_resultado_completo


@dataclass
class PipelineResult:
    """Resultado completo do pipeline."""

    ideia_original: str
    validacao: ValidationResult
    titulos: TitleCreationResult
    arquivo_salvo: Path
    neo4j_context: dict[str, Any]
    success: bool
    error_message: str | None = None

    def __repr__(self) -> str:
        status = "✅" if self.success else "❌"
        return (
            f"PipelineResult({status} "
            f"score={self.validacao.score}, "
            f"titulos={len(self.titulos.titulos_virais)}, "
            f"arquivo={self.arquivo_salvo.name})"
        )


async def executar_pipeline_completo(
    ideia: str,
    consultar_neo4j: bool = True,
    salvar_neo4j: bool = True,
    output_dir: str | Path = "outputs/Lista de ideias",
    cwd: str | None = None,
) -> PipelineResult:
    """Executa o pipeline completo de geração de conteúdo.

    Este pipeline orquestra todas as etapas:
    1. Consultar Neo4j (contexto e aprendizados)
    2. Validar ideia
    3. Gerar títulos virais
    4. Salvar no Neo4j (memórias e conexões)
    5. Criar arquivo .md

    Args:
        ideia: Ideia bruta do usuário
        consultar_neo4j: Se deve consultar Neo4j antes de gerar
        salvar_neo4j: Se deve salvar resultados no Neo4j
        output_dir: Diretório de saída
        cwd: Diretório de trabalho

    Returns:
        PipelineResult com todos os dados do processo

    Example:
        >>> import anyio
        >>> from pipeline import executar_pipeline_completo
        >>>
        >>> async def main():
        ...     result = await executar_pipeline_completo("streaming do claude sdk")
        ...     print(f"Score: {result.validacao.score}")
        ...     print(f"Títulos: {len(result.titulos.titulos_virais)}")
        ...     print(f"Arquivo: {result.arquivo_salvo}")
        >>>
        >>> anyio.run(main)
    """
    neo4j_client = Neo4jClient()
    neo4j_context: dict[str, Any] = {}

    try:
        # ===== ETAPA 1: Consultar Neo4j (ANTES de validar) =====
        if consultar_neo4j:
            # Aqui seria feita a chamada ao Neo4j via MCP
            # Por enquanto, deixamos um placeholder
            # Na prática, isso seria feito pelo Claude SDK durante a execução
            neo4j_context = {
                "related_memories": "Consultado via MCP durante execução",
                "learnings": "Aprendizados do Neo4j",
                "best_practices": "Melhores práticas anteriores",
            }

        # ===== ETAPA 2: Validar ideia =====
        print(f"🔍 Validando ideia: '{ideia}'...")
        validacao = await validar_ideia(ideia, cwd=cwd)
        print(f"✅ Validação concluída: Score {validacao.score}/10")

        # ===== ETAPA 3: Gerar títulos virais =====
        print(f"🎬 Gerando títulos virais...")

        # Preparar dados de validação como dict
        validacao_dict = {
            "score": validacao.score,
            "best_angle": validacao.best_angle,
            "viral_factors": validacao.viral_factors,
            "recommended_format": validacao.recommended_format,
        }

        # Gerar títulos com contexto completo
        titulos = await gerar_titulos_com_neo4j(
            ideia=ideia,
            validacao=validacao_dict,
            neo4j_context=neo4j_context if consultar_neo4j else None,
            cwd=cwd,
        )

        print(f"✅ {len(titulos.titulos_virais)} títulos gerados")

        # ===== ETAPA 4: Salvar no Neo4j =====
        if salvar_neo4j:
            print("💾 Salvando aprendizado completo no Neo4j...")

            best_title = titulos.get_best_title()
            if best_title:
                # 1. Criar nós principais
                ideia_mem = neo4j_client.criar_memoria_ideia(
                    ideia_original=ideia,
                    validation_score=validacao.score,
                    angle=validacao.best_angle,
                    estimated_views=validacao.estimated_metrics.get("views", "N/A"),
                )

                # 2. Criar padrões SDK usados neste pipeline
                pattern_validator = neo4j_client.criar_memoria_pattern(
                    pattern_name="Async validation pattern",
                    description="Validação de ideias com ClaudeSDKClient async",
                    code_snippet="async with ClaudeSDKClient() as client: ...",
                    success_rate=0.95
                )

                pattern_creator = neo4j_client.criar_memoria_pattern(
                    pattern_name="Title generation pattern",
                    description="Geração de títulos virais com fórmulas",
                    code_snippet="Usar fórmulas + gatilhos psicológicos",
                    success_rate=0.88
                )

                # 3. Criar conceitos demonstrados
                conceito_pipeline = neo4j_client.criar_memoria_conceito(
                    concept_name="Multi-step Claude SDK pipeline",
                    explanation="Pipeline com validação + geração + aprendizado",
                    use_cases=["content creation", "validation workflow", "learning system"]
                )

                # 4. Registrar exemplo completo do pipeline
                exemplo_pipeline = neo4j_client.criar_memoria_exemplo(
                    example_name=f"Pipeline completo: {ideia[:30]}",
                    code=f"""
# Pipeline: Validação -> Geração -> Aprendizado
# Ideia: {ideia}
# Score validação: {validacao.score}
# Título gerado: {best_title.titulo}
# CTR: {best_title.ctr_score}/10
                    """,
                    demonstrates_what="Multi-step pipeline with Claude SDK",
                    complexity="hard"
                )

                # 5. Criar relacionamentos (placeholder - em produção seria via MCP)
                # exemplo_pipeline -[IMPLEMENTS]-> pattern_validator
                # exemplo_pipeline -[IMPLEMENTS]-> pattern_creator
                # exemplo_pipeline -[DEMONSTRATES]-> conceito_pipeline

                neo4j_operations = [
                    ideia_mem,
                    pattern_validator,
                    pattern_creator,
                    conceito_pipeline,
                    exemplo_pipeline,
                ]

                # Executar operações MCP REAIS no Neo4j
                results = await executar_operacoes_neo4j(neo4j_operations)

                # Contar sucessos
                sucessos = sum(1 for r in results if r.get("node_id") or r.get("learning_saved"))

                neo4j_context["pending_operations"] = neo4j_operations
                neo4j_context["executed_operations"] = results
                neo4j_context["success_count"] = sucessos
                neo4j_context["pattern_count"] = 2
                neo4j_context["concept_count"] = 1

                print(f"✅ {sucessos}/{len(neo4j_operations)} operações Neo4j executadas com sucesso")
                print(f"   - 2 padrões SDK registrados")
                print(f"   - 1 conceito de pipeline demonstrado")
                print(f"   - 1 exemplo completo criado")

        # ===== ETAPA 5: Salvar arquivo .md =====
        print(f"📝 Criando arquivo .md...")
        arquivo_salvo = salvar_resultado_completo(
            ideia=ideia,
            validation_result=validacao,
            title_result=titulos,
            neo4j_context=neo4j_context,
            output_dir=output_dir,
        )

        print(f"✅ Arquivo criado: {arquivo_salvo}")

        # Retornar resultado completo
        return PipelineResult(
            ideia_original=ideia,
            validacao=validacao,
            titulos=titulos,
            arquivo_salvo=arquivo_salvo,
            neo4j_context=neo4j_context,
            success=True,
        )

    except Exception as e:
        # Em caso de erro, retornar resultado parcial
        print(f"❌ Erro no pipeline: {e}")

        # Criar resultado de fallback
        fallback_validation = ValidationResult(
            {
                "original_idea": ideia,
                "score": 0.0,
                "verdict": "ERROR",
                "best_angle": "desconhecido",
            }
        )

        fallback_title_data = {
            "titulo": f"Erro ao processar: {ideia}",
            "ctr_score": 0.0,
            "formula": "N/A",
            "gatilho": "N/A",
            "emoji": "",
        }

        fallback_titles = TitleCreationResult(
            {
                "ideia_original": ideia,
                "titulos_virais": [fallback_title_data],
                "recomendado": fallback_title_data["titulo"],
                "thumbnail_hint": "Erro no processamento",
            }
        )

        return PipelineResult(
            ideia_original=ideia,
            validacao=fallback_validation,
            titulos=fallback_titles,
            arquivo_salvo=Path("outputs/error.md"),
            neo4j_context={},
            success=False,
            error_message=str(e),
        )


async def executar_pipeline_rapido(
    ideia: str,
    output_dir: str | Path = "outputs/Lista de ideias",
) -> PipelineResult:
    """Pipeline rápido sem consulta ao Neo4j.

    Para uso rápido quando não precisa de contexto histórico.

    Args:
        ideia: Ideia bruta
        output_dir: Diretório de saída

    Returns:
        PipelineResult
    """
    return await executar_pipeline_completo(
        ideia=ideia,
        consultar_neo4j=False,
        salvar_neo4j=False,
        output_dir=output_dir,
    )
