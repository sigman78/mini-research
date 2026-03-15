import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def stub_crawl4ai():
    stub = ModuleType("crawl4ai")
    stub.AsyncWebCrawler = MagicMock
    stub.BrowserConfig = MagicMock
    stub.CrawlerRunConfig = MagicMock
    prev = sys.modules.get("crawl4ai")
    sys.modules["crawl4ai"] = stub
    yield
    if prev is None:
        sys.modules.pop("crawl4ai", None)
    else:
        sys.modules["crawl4ai"] = prev
