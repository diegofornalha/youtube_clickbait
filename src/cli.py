#!/usr/bin/env python3
"""CLI interativo para geração de conteúdo viral sobre Claude SDK."""

import anyio
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typing_extensions import Annotated

from .pipeline import executar_pipeline_completo, executar_pipeline_rapido

app = typer.Typer(
    name="youtube-cli",
    help="🎬 Sistema automatizado para gerar títulos virais sobre Claude Agent SDK",
    add_completion=False,
)
console = Console()


@app.command()
def gerar(
    ideia: Annotated[str, typer.Argument(help="Ideia de vídeo para gerar títulos")],
    rapido: Annotated[
        bool,
        typer.Option("--rapido", "-r", help="Modo rápido (sem consultar Neo4j)"),
    ] = False,
    output: Annotated[
        str,
        typer.Option("--output", "-o", help="Diretório de saída"),
    ] = "outputs/Lista de ideias",
):
    """Gera títulos virais para uma ideia de vídeo.

    Example:
        youtube-cli gerar "streaming do claude sdk"
        youtube-cli gerar "multi agents" --rapido
    """
    console.print(
        Panel.fit(
            f"🎬 [bold cyan]Gerando títulos virais[/]\nIdeia: [yellow]{ideia}[/]",
            border_style="cyan",
        )
    )

    async def run():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processando...", total=None)

            if rapido:
                result = await executar_pipeline_rapido(ideia, output_dir=output)
            else:
                result = await executar_pipeline_completo(ideia, output_dir=output)

            progress.update(task, completed=True)

        # Exibir resultados
        if result.success:
            console.print("\n[bold green]✅ Pipeline concluído com sucesso![/]\n")

            # Tabela de validação
            val_table = Table(title="📊 Validação", border_style="blue")
            val_table.add_column("Métrica", style="cyan")
            val_table.add_column("Valor", style="yellow")

            val_table.add_row("Score", f"{result.validacao.score}/10")
            val_table.add_row("Ângulo", result.validacao.best_angle)
            val_table.add_row("Veredicto", result.validacao.verdict)
            if result.validacao.viral_factors:
                val_table.add_row(
                    "Fatores Virais", ", ".join(result.validacao.viral_factors)
                )

            console.print(val_table)

            # Tabela de títulos
            title_table = Table(title="🎯 Títulos Gerados", border_style="green")
            title_table.add_column("#", style="cyan", width=4)
            title_table.add_column("Título", style="white")
            title_table.add_column("CTR", style="yellow", width=8)
            title_table.add_column("Fórmula", style="magenta")

            for i, titulo_obj in enumerate(result.titulos.titulos_virais, 1):
                title_table.add_row(
                    str(i),
                    titulo_obj.titulo,
                    f"{titulo_obj.ctr_score}/10",
                    titulo_obj.formula,
                )

            console.print(title_table)

            # Melhor título
            best = result.titulos.get_best_title()
            if best:
                console.print(
                    Panel.fit(
                        f"[bold green]{best.titulo}[/]\n"
                        f"CTR: [yellow]{best.ctr_score}/10[/] | "
                        f"Gatilhos: [magenta]{best.gatilho}[/]",
                        title="🏆 Título Recomendado",
                        border_style="green",
                    )
                )

            # Arquivo salvo
            console.print(f"\n📁 [cyan]Arquivo salvo:[/] {result.arquivo_salvo}\n")

        else:
            console.print(
                f"\n[bold red]❌ Erro no pipeline:[/] {result.error_message}\n"
            )

    anyio.run(run)


@app.command()
def validar(
    ideia: Annotated[str, typer.Argument(help="Ideia para validar")],
):
    """Apenas valida uma ideia sem gerar títulos.

    Example:
        youtube-cli validar "streaming do claude"
    """
    console.print(
        Panel.fit(
            f"🔍 [bold cyan]Validando ideia[/]\n{ideia}",
            border_style="cyan",
        )
    )

    async def run():
        from .agents.validator import validar_ideia

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validando...", total=None)
            result = await validar_ideia(ideia)
            progress.update(task, completed=True)

        # Exibir resultado
        table = Table(title="📊 Resultado da Validação", border_style="blue")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="yellow")

        table.add_row("Score", f"{result.score}/10")
        table.add_row("Ângulo", result.best_angle)
        table.add_row("Veredicto", result.verdict)
        table.add_row("Formato", result.recommended_format)

        if result.viral_factors:
            table.add_row("Fatores Virais", ", ".join(result.viral_factors))

        if result.improvements_needed:
            table.add_row("Melhorias", ", ".join(result.improvements_needed))

        console.print(table)

        if result.title_suggestions:
            console.print("\n[bold cyan]💡 Sugestões de Título:[/]")
            for i, sugestao in enumerate(result.title_suggestions, 1):
                console.print(f"  {i}. {sugestao}")

    anyio.run(run)


@app.command()
def batch(
    arquivo: Annotated[
        Path,
        typer.Argument(help="Arquivo com lista de ideias (uma por linha)"),
    ],
    output: Annotated[
        str,
        typer.Option("--output", "-o", help="Diretório de saída"),
    ] = "outputs/Lista de ideias",
):
    """Processa múltiplas ideias em batch.

    Example:
        youtube-cli batch ideias.txt
    """
    if not arquivo.exists():
        console.print(f"[bold red]❌ Arquivo não encontrado:[/] {arquivo}")
        raise typer.Exit(1)

    ideias = arquivo.read_text(encoding="utf-8").strip().split("\n")
    ideias = [i.strip() for i in ideias if i.strip()]

    console.print(
        Panel.fit(
            f"📦 [bold cyan]Processamento em Batch[/]\n"
            f"Arquivo: [yellow]{arquivo}[/]\n"
            f"Total de ideias: [green]{len(ideias)}[/]",
            border_style="cyan",
        )
    )

    async def run():
        resultados_sucesso = 0
        resultados_falha = 0

        for i, ideia in enumerate(ideias, 1):
            console.print(f"\n[cyan]═══ [{i}/{len(ideias)}] {ideia} ═══[/]")

            try:
                result = await executar_pipeline_completo(ideia, output_dir=output)
                if result.success:
                    resultados_sucesso += 1
                    console.print(f"[green]✅ Concluído[/]")
                else:
                    resultados_falha += 1
                    console.print(f"[red]❌ Falhou: {result.error_message}[/]")
            except Exception as e:
                resultados_falha += 1
                console.print(f"[red]❌ Erro: {e}[/]")

        # Resumo final
        console.print(
            Panel.fit(
                f"[bold green]✅ Sucesso:[/] {resultados_sucesso}\n"
                f"[bold red]❌ Falhas:[/] {resultados_falha}\n"
                f"[bold cyan]Total:[/] {len(ideias)}",
                title="📊 Resumo do Batch",
                border_style="cyan",
            )
        )

    anyio.run(run)


@app.command()
def versao():
    """Exibe versão do sistema."""
    console.print(
        Panel.fit(
            "[bold cyan]YouTube Clickbait Generator[/]\n"
            "Versão: [yellow]0.1.0[/]\n"
            "Powered by [magenta]Claude Agent SDK[/]",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    app()
