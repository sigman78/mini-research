import truststore


def pytest_configure(config):
    truststore.inject_into_ssl()
