"""Tests for the Meteora error model and exception hierarchy."""

from meteora import MeteoraAPIError, MeteoraError


def test_api_error_is_a_meteora_error() -> None:
    err = MeteoraAPIError(message="Pool not found.", status_code=404)
    assert isinstance(err, MeteoraError)


def test_api_error_str_includes_status_and_message() -> None:
    err = MeteoraAPIError(message="pool not found", status_code=404)
    text = str(err)
    assert "404" in text
    assert "pool not found" in text


def test_api_error_exposes_fields() -> None:
    err = MeteoraAPIError(message="bad request", status_code=400)
    assert err.message == "bad request"
    assert err.status_code == 400
