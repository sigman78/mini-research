def test_package_importable():
    import mini_research  # noqa: F401


def test_version():
    import mini_research

    assert mini_research.__version__ == "0.1.0"


def test_settings_instantiable():
    from mini_research.config import Settings

    Settings()
