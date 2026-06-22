"""Tests for meteora.constants."""

from meteora import constants


def test_default_base_url_is_the_datapi_host() -> None:
    assert constants.DEFAULT_BASE_URL == "https://dlmm.datapi.meteora.ag"


def test_default_base_url_has_no_trailing_slash() -> None:
    assert not constants.DEFAULT_BASE_URL.endswith("/")
