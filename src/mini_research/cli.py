import asyncio
from pathlib import Path

import typer
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from rich.console import Console

from mini_research.config import Settings
from mini_research.llm import CostTracker, complete
from mini_research.scrape import ScrapeError
from mini_research.scrape import scrape as _scrape
from mini_research.search import SearchError
from mini_research.search import search as _search

app = typer.Typer(pretty_exceptions_enable=False, rich_markup_mode=None)
llm_app = typer.Typer(pretty_exceptions_enable=False, rich_markup_mode=None)
app.add_typer(llm_app, name="llm")
console = Console()

_NODE_LABELS = {
    "plan": "Planning research...",
    "gather": "Gathering sources...",
    "evaluate": "Evaluating coverage...",
    "report": "Writing final report...",
}


def _resolve(val: str) -> str:
    if val.startswith("@"):
        return Path(val[1:]).read_text()
    return val


@app.command()
def research(
    query: str,
    out: Path = typer.Option(..., "-o", "--out", help="Output file for the report"),
    iter: int | None = typer.Option(None, "-i", "--iter", help="Max research iterations"),
    limit: int | None = typer.Option(None, "-l", "--limit", help="Max searches per iteration"),
    scraper: str | None = typer.Option(None, "-c", "--scraper", help="Scrape provider"),
    stats: bool = typer.Option(False, "-t", "--stats", help="Print token/cost stats after run"),
) -> None:
    from rich.status import Status

    from mini_research.graph import build_graph
    from mini_research.state import ResearchState

    query = _resolve(query)
    settings = Settings()
    if iter is not None:
        settings = settings.model_copy(update={"max_research_iterations": iter})
    if limit is not None:
        settings = settings.model_copy(update={"search_max_results": limit})
    if scraper is not None:
        settings = settings.model_copy(update={"scrape_provider": scraper})
    tracker = CostTracker()

    with Status("Starting...", console=console) as status:

        def _on_scrape_progress(done: int, total: int) -> None:
            status.update(f"Gathering sources... |{done}/{total}|")

        graph = build_graph(
            settings=settings, tracker=tracker, on_scrape_progress=_on_scrape_progress
        )
        initial_state = ResearchState(query=query)

        async def _run() -> dict:
            merged: dict = {}
            async for chunk in graph.astream(initial_state):
                for node_name, updates in chunk.items():
                    if not node_name.startswith("__"):
                        if node_name == "evaluate":
                            iteration = updates.get("iteration_count", 0)
                            max_iter = settings.max_research_iterations
                            label = f"Evaluating coverage (iteration {iteration}/{max_iter})..."
                        else:
                            label = _NODE_LABELS.get(node_name, node_name)
                        status.update(label)
                        merged.update(updates)
            return merged

        result = asyncio.run(_run())

    if result.get("final_report"):
        out.write_text(result["final_report"], encoding="utf-8")
        console.print(f"Report written to {out}")
    else:
        console.print("[yellow]No report generated.[/yellow]")
    if stats:
        console.print(tracker.summary())


@app.command()
def search(
    query: str,
    searcher: str | None = typer.Option(None, "-s", "--searcher", help="Search provider"),
    limit: int | None = typer.Option(None, "-l", "--limit", help="Max results"),
) -> None:
    query = _resolve(query)
    try:
        results = asyncio.run(_search(query, max_results=limit, provider=searcher))
    except SearchError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)
    for i, result in enumerate(results):
        if i > 0:
            console.print()
        console.print(result.title)
        console.print(result.url)
        console.print(f"[dim]{result.snippet}[/dim]")


@app.command()
def scrape(
    url: str,
    scraper: str | None = typer.Option(None, "-c", "--scraper", help="Scrape provider"),
) -> None:
    try:
        result = asyncio.run(_scrape(url, provider=scraper))
    except ScrapeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)
    console.print(result.text)


@llm_app.command()
def chat(
    prompt: str,
    model: str | None = typer.Option(None, "-m", "--model", help="LiteLLM model string"),
    system: str | None = typer.Option(None, "-s", "--system", help="System prompt"),
) -> None:
    prompt = _resolve(prompt)
    system = _resolve(system) if system else None
    messages: list[BaseMessage] = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))
    tracker = CostTracker()
    response = asyncio.run(complete(messages, model=model, tracker=tracker))
    console.print(response.text)
    cost_line = (
        f"[dim]model={response.model} tokens={response.input_tokens}"
        f"+{response.output_tokens} cost=${response.cost_usd:.6f}[/dim]"
    )
    console.print(cost_line)


@llm_app.command()
def models() -> None:
    settings = Settings()
    console.print(f"Configured model: [bold]{settings.litellm_model}[/bold]")
