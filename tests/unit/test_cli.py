import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

from mini_research.cli import app
from mini_research.scrape import ScrapeError
from mini_research.scrape.models import ScrapeResult
from mini_research.search import SearchError
from mini_research.search.models import SearchResult

runner = CliRunner()


def test_search_command_displays_results():
    results = [
        SearchResult(
            title="Python Asyncio",
            url="https://example.com/asyncio",
            snippet="Async library",
        ),
    ]
    with patch("mini_research.cli._search", new_callable=AsyncMock, return_value=results):
        result = runner.invoke(app, ["search", "python asyncio"])
    assert result.exit_code == 0
    assert "Python Asyncio" in result.output
    assert "https://example.com/asyncio" in result.output
    assert "Async library" in result.output


def test_search_command_handles_error():
    exc = SearchError("provider failed")
    with patch("mini_research.cli._search", new_callable=AsyncMock, side_effect=exc):
        result = runner.invoke(app, ["search", "python asyncio"])
    assert result.exit_code == 1
    assert "provider failed" in result.output


def test_scrape_command_displays_content():
    scrape_result = ScrapeResult(url="https://example.com", text="Hello world content")
    with patch("mini_research.cli._scrape", new_callable=AsyncMock, return_value=scrape_result):
        result = runner.invoke(app, ["scrape", "https://example.com"])
    assert result.exit_code == 0
    assert "Hello world content" in result.output


def test_scrape_command_handles_error():
    exc = ScrapeError("fetch failed")
    with patch("mini_research.cli._scrape", new_callable=AsyncMock, side_effect=exc):
        result = runner.invoke(app, ["scrape", "https://example.com"])
    assert result.exit_code == 1
    assert "fetch failed" in result.output


async def _fake_astream(initial_state):
    yield {"plan": {"query": "enriched", "search_queries": []}}
    yield {"report": {"final_report": "## My Report\n\nContent here."}}


def test_research_command_displays_report():
    mock_graph = MagicMock()
    mock_graph.astream = _fake_astream
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        out_path = f.name
    with patch("mini_research.graph.build_graph", return_value=mock_graph):
        result = runner.invoke(app, ["research", "test query", "-o", out_path])
    assert result.exit_code == 0
    assert "My Report" in result.output
    assert Path(out_path).read_text() == "## My Report\n\nContent here."


async def _fake_astream_no_report(initial_state):
    yield {"plan": {"query": "enriched", "search_queries": []}}


def test_research_command_no_report():
    mock_graph = MagicMock()
    mock_graph.astream = _fake_astream_no_report
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        out_path = f.name
    with patch("mini_research.graph.build_graph", return_value=mock_graph):
        result = runner.invoke(app, ["research", "test query", "-o", out_path])
    assert result.exit_code == 0
    assert "No report generated" in result.output
