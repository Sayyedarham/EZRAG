import pytest

from settings import _int_env


def test_integer_setting_rejects_values_below_minimum(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAG_TEST_LIMIT", "0")
    with pytest.raises(ValueError, match="at least"):
        _int_env("RAG_TEST_LIMIT", 5)


def test_integer_setting_accepts_valid_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAG_TEST_LIMIT", "12")
    assert _int_env("RAG_TEST_LIMIT", 5) == 12
