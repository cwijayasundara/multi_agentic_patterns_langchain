"""
Pytest configuration for pattern selector agent tests.

Registers custom marks and provides shared fixtures.
"""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (require API calls, deselect with '-m \"not integration\"')"
    )
