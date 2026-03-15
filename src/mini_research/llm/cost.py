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
        aggregated: dict[str, dict] = {}
        for r in self._responses:
            if r.model not in aggregated:
                aggregated[r.model] = {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
            aggregated[r.model]["input_tokens"] += r.input_tokens
            aggregated[r.model]["output_tokens"] += r.output_tokens
            aggregated[r.model]["cost_usd"] += r.cost_usd
        table = Table(title="LLM Cost Summary")
        table.add_column("Model")
        table.add_column("Input Tokens", justify="right")
        table.add_column("Output Tokens", justify="right")
        table.add_column("Cost (USD)", justify="right")
        for model, agg in aggregated.items():
            table.add_row(model, str(agg["input_tokens"]), str(agg["output_tokens"]), f"${agg['cost_usd']:.6f}") # noqa
        if len(aggregated) > 1:
            table.add_section()
            table.add_row(
                "Total",
                str(sum(a["input_tokens"] for a in aggregated.values())),
                str(sum(a["output_tokens"] for a in aggregated.values())),
                f"${self.total_usd():.6f}",
            )
        console = Console()
        with console.capture() as capture:
            console.print(table)
        return capture.get()
