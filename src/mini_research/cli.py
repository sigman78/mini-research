import asyncio

import typer
from rich.console import Console

from mini_research.config import Settings
from mini_research.llm import CostTracker, Message, complete

app = typer.Typer()
llm_app = typer.Typer()
app.add_typer(llm_app, name="llm")
console = Console()


@app.command()
def research(query: str) -> None:
    typer.echo(f"Researching: {query}")


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
