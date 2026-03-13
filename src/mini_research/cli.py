import typer

app = typer.Typer()


@app.command()
def research(query: str) -> None:
    typer.echo(f"Researching: {query}")
