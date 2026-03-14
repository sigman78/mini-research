import os
from unittest.mock import patch

from mini_research.config import Settings
from mini_research.graph import build_graph


def test_build_graph_sets_langsmith_env_when_enabled():
    settings = Settings(
        langsmith_tracing=True, langsmith_api_key="test-key", langsmith_project="my-proj"
    )
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("LANGSMITH_API_KEY", None)
        os.environ.pop("LANGSMITH_TRACING", None)
        os.environ.pop("LANGSMITH_PROJECT", None)
        build_graph(settings=settings)
        assert os.environ.get("LANGSMITH_API_KEY") == "test-key"
        assert os.environ.get("LANGSMITH_TRACING") == "true"
        assert os.environ.get("LANGSMITH_PROJECT") == "my-proj"


def test_build_graph_skips_langsmith_when_disabled():
    settings = Settings(langsmith_tracing=False, langsmith_api_key="test-key")
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("LANGSMITH_API_KEY", None)
        os.environ.pop("LANGSMITH_TRACING", None)
        build_graph(settings=settings)
        assert "LANGSMITH_API_KEY" not in os.environ
        assert "LANGSMITH_TRACING" not in os.environ


def test_build_graph_skips_langsmith_when_no_key():
    settings = Settings(langsmith_tracing=True, langsmith_api_key=None)
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("LANGSMITH_API_KEY", None)
        os.environ.pop("LANGSMITH_TRACING", None)
        build_graph(settings=settings)
        assert "LANGSMITH_API_KEY" not in os.environ
        assert "LANGSMITH_TRACING" not in os.environ
