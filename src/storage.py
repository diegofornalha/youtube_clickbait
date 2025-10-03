"""Módulo para salvar outputs em arquivos .md."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any


def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos de nome de arquivo.

    Args:
        filename: Nome do arquivo original

    Returns:
        Nome sanitizado seguro para filesystem
    """
    # Remover emojis e caracteres especiais
    filename = re.sub(r"[^\w\s-]", "", filename)
    # Substituir espaços por hífens
    filename = re.sub(r"\s+", " ", filename).strip()
    # Limitar tamanho
    return filename[:200]


def salvar_ideia_com_titulos(
    ideia_original: str,
    titulo_recomendado: str,
    ctr_score: float,
    validacao: dict[str, Any] | None = None,
    titulos_alternativos: list[dict[str, Any]] | None = None,
    neo4j_insights: dict[str, Any] | None = None,
    output_dir: Path | str = "outputs/Lista de ideias",
) -> Path:
    """Salva ideia de vídeo com títulos gerados em arquivo .md.

    Args:
        ideia_original: Ideia bruta do usuário
        titulo_recomendado: Título recomendado (será o nome do arquivo)
        ctr_score: Score CTR do título recomendado
        validacao: Dados de validação da ideia
        titulos_alternativos: Lista de títulos alternativos gerados
        neo4j_insights: Insights do Neo4j
        output_dir: Diretório de saída

    Returns:
        Path do arquivo criado
    """
    # Criar diretório se não existir
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Sanitizar nome do arquivo
    safe_filename = sanitize_filename(titulo_recomendado)
    if not safe_filename:
        safe_filename = "titulo_sem_nome"

    # Criar nome de arquivo único se já existir
    file_path = output_path / f"{safe_filename}.md"
    counter = 1
    while file_path.exists():
        file_path = output_path / f"{safe_filename}_{counter}.md"
        counter += 1

    # Construir conteúdo do arquivo
    content_parts = [
        f"# {titulo_recomendado}\n",
        f"**Data**: {datetime.now().strftime('%Y-%m-%d')}\n",
        f"**CTR**: {ctr_score}/10\n",
        f"**Status**: 📌 Pendente\n",
        "\n## Ideia Original\n",
        f'"{ideia_original}"\n',
    ]

    # Adicionar validação se disponível
    if validacao:
        content_parts.extend(
            [
                "\n## 📊 Validação\n",
                f"- **Score**: {validacao.get('score', 'N/A')}/10\n",
                f"- **Ângulo**: {validacao.get('best_angle', 'N/A')}\n",
                f"- **Veredicto**: {validacao.get('verdict', 'N/A')}\n",
            ]
        )

        viral_factors = validacao.get("viral_factors", [])
        if viral_factors:
            content_parts.append(f"- **Fatores Virais**: {', '.join(viral_factors)}\n")

        estimated = validacao.get("estimated_metrics", {})
        if estimated:
            content_parts.extend(
                [
                    "\n### Métricas Estimadas\n",
                    f"- Views: {estimated.get('views', 'N/A')}\n",
                    f"- CTR: {estimated.get('ctr', 'N/A')}\n",
                    f"- Retenção: {estimated.get('retention', 'N/A')}\n",
                ]
            )

    # Adicionar insights do Neo4j
    if neo4j_insights:
        content_parts.extend(
            [
                "\n## 🧠 Insights do Neo4j\n",
                f"- **Memórias Relacionadas**: {neo4j_insights.get('related_memories', 'Nenhuma')}\n",  # noqa: E501
                f"- **Aprendizados**: {neo4j_insights.get('learnings', 'Nenhum')}\n",
            ]
        )

    # Adicionar títulos alternativos
    if titulos_alternativos:
        content_parts.extend(["\n## 🎯 Títulos Alternativos\n"])
        for i, titulo_data in enumerate(titulos_alternativos, 1):
            content_parts.extend(
                [
                    f"\n### {i}. {titulo_data.get('titulo', 'Sem título')}\n",
                    f"- **CTR**: {titulo_data.get('ctr_score', 0)}/10\n",
                    f"- **Fórmula**: {titulo_data.get('formula', 'N/A')}\n",
                    f"- **Gatilhos**: {titulo_data.get('gatilho', 'N/A')}\n",
                ]
            )

    # Escrever arquivo
    file_path.write_text("".join(content_parts), encoding="utf-8")

    return file_path


def salvar_resultado_completo(
    ideia: str,
    validation_result: Any,
    title_result: Any,
    neo4j_context: dict[str, Any] | None = None,
    output_dir: Path | str = "outputs/Lista de ideias",
) -> Path:
    """Salva resultado completo do pipeline (validação + títulos).

    Esta é uma função de conveniência que usa os objetos de resultado
    diretamente dos agents.

    Args:
        ideia: Ideia original
        validation_result: ValidationResult do validator agent
        title_result: TitleCreationResult do creator agent
        neo4j_context: Contexto do Neo4j
        output_dir: Diretório de saída

    Returns:
        Path do arquivo criado
    """
    # Extrair dados de validação
    validacao_dict = {
        "score": validation_result.score,
        "best_angle": validation_result.best_angle,
        "verdict": validation_result.verdict,
        "viral_factors": validation_result.viral_factors,
        "estimated_metrics": validation_result.estimated_metrics,
    }

    # Extrair títulos alternativos
    titulos_alternativos = [
        {
            "titulo": t.titulo,
            "ctr_score": t.ctr_score,
            "formula": t.formula,
            "gatilho": t.gatilho,
        }
        for t in title_result.titulos_virais
    ]

    # Obter título recomendado
    best_title = title_result.get_best_title()
    titulo_recomendado = best_title.titulo if best_title else title_result.recomendado
    ctr_score = best_title.ctr_score if best_title else 7.0

    return salvar_ideia_com_titulos(
        ideia_original=ideia,
        titulo_recomendado=titulo_recomendado,
        ctr_score=ctr_score,
        validacao=validacao_dict,
        titulos_alternativos=titulos_alternativos,
        neo4j_insights=neo4j_context,
        output_dir=output_dir,
    )
