"""Enable local custom integrations in Home Assistant tests."""

import pytest


@pytest.fixture(autouse=True)
def custom_integrations(enable_custom_integrations):
    yield
