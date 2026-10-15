from logging.config import dictConfig
from unittest.mock import Mock

import pytest

import logging_config


@pytest.mark.parametrize(
    ("configured_level", "expected_level"),
    [
        ("debug", "DEBUG"),
        ("invalid", "INFO"),
    ],
)
def test_configure_logging_uses_validated_log_level(
    monkeypatch: pytest.MonkeyPatch,
    configured_level: str,
    expected_level: str,
) -> None:
    dict_config = Mock()
    monkeypatch.setattr(logging_config, "dictConfig", dict_config)
    monkeypatch.setenv("LOG_LEVEL", configured_level)

    logging_config.configure_logging()

    assert dict_config.call_args.args[0]["root"]["level"] == expected_level
