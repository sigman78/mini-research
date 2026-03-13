from rich.console import Console
from rich.table import Table

from .models import LLMResponse


class CostTracker:
    def __init__(self) -> None:
        self._responses: list[LLMResponse] = []

    def add(self, response: LLMResponse) -> None:
        self._responses.append(response)

    def total_usd(self) -> float:
        return sum(r.cost_usd for r in self._responses)

    def summary(self) -> str:
        table = Table(title="LLM Cost Summary")
        table.add_column("Model")
        table.add_column("Input Tokens", justify="right")
        table.add_column("Output Tokens", justify="right")
        table.add_column("Cost (USD)", justify="right")
        for r in self._responses:
            table.add_row(r.model, str(r.input_tokens), str(r.output_tokens), f"${r.cost_usd:.6f}")
        console = Console()
        with console.capture() as capture:
            console.print(table)
        return capture.get()
