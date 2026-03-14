import asyncio

import typer
from rich.console import Console

from mini_research.config import Settings
from mini_research.llm import CostTracker, Message, complete
from mini_research.scrape import ScrapeError, scrape
from mini_research.search import SearchError, search

app = typer.Typer()
llm_app = typer.Typer()
app.add_typer(llm_app, name="llm")
search_app = typer.Typer()
scrape_app = typer.Typer()
app.add_typer(search_app, name="search")
app.add_typer(scrape_app, name="scrape")
console = Console()


@app.command()
def research(query: str) -> None:
    from rich.markdown import Markdown

    from mini_research.graph import build_graph
    from mini_research.state import ResearchState

    settings = Settings()
    tracker = CostTracker()
    graph = build_graph(settings=settings, tracker=tracker)
    initial_state = ResearchState(query=query)
    result = asyncio.run(graph.ainvoke(initial_state))
    if result.get("final_report"):
        console.print(Markdown(result["final_report"]))
    else:
        console.print("[yellow]No report generated.[/yellow]")
    console.print(tracker.summary())


@llm_app.command()
def chat(
    prompt: str,
    model: str | None = typer.Option(None, "--model", help="LiteLLM model string"),
    system: str | None = typer.Option(None, "--system", help="System prompt"),
) -> None:
    messages: list[Message] = []
    if system:
        messages.append(Message(role="system", content=system))
    messages.append(Message(role="user", content=prompt))
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


@search_app.command()
def search_cmd(
    query: str,
    provider: str | None = typer.Option(None, "--provider", help="Search provider"),
    limit: int | None = typer.Option(None, "--limit", help="Max results"),
) -> None:
    try:
        results = asyncio.run(search(query, max_results=limit, provider=provider))
    except SearchError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)
    for i, result in enumerate(results):
        if i > 0:
            console.print()
        console.print(result.title)
        console.print(result.url)
        console.print(f"[dim]{result.snippet}[/dim]")


@scrape_app.command()
def scrape_cmd(
    url: str,
    provider: str | None = typer.Option(None, "--provider", help="Scrape provider"),
) -> None:
    try:
        result = asyncio.run(scrape(url, provider=provider))
    except ScrapeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)
    console.print(result.text)
