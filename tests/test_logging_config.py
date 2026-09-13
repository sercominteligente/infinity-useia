import logging

import pytest

from hakham.logging_config import configure_logging


def test_configure_logging_sets_requested_level():
    configure_logging("DEBUG")
    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_rejects_invalid_level():
    with pytest.raises(ValueError):
        configure_logging("LOUD")
