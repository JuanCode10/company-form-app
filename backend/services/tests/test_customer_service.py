from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError

from services import customer_service as cs


def _integrity_error() -> IntegrityError:
    return IntegrityError("insert", {}, Exception("duplicate"))


def test_commit_or_rollback_commits_successfully(monkeypatch: pytest.MonkeyPatch) -> None:
    session = SimpleNamespace(commit=Mock(), rollback=Mock())
    monkeypatch.setattr(cs.db, "session", session)

    cs._commit_or_rollback()

    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()


def test_commit_or_rollback_rolls_back_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    session = SimpleNamespace(commit=Mock(side_effect=RuntimeError("boom")), rollback=Mock())
    monkeypatch.setattr(cs.db, "session", session)

    with pytest.raises(RuntimeError, match="boom"):
        cs._commit_or_rollback()

    session.rollback.assert_called_once_with()


def test_is_valid_email_returns_true_for_valid_email(monkeypatch: pytest.MonkeyPatch) -> None:
    validate_email = Mock()
    monkeypatch.setattr(cs, "validate_email", validate_email)

    assert cs.is_valid_email("valid@example.com", check_deliverability=True) is True
    validate_email.assert_called_once_with("valid@example.com", check_deliverability=True)


def test_is_valid_email_returns_false_for_invalid_email(monkeypatch: pytest.MonkeyPatch) -> None:
    validate_email = Mock(side_effect=cs.EmailNotValidError("invalid"))
    monkeypatch.setattr(cs, "validate_email", validate_email)

    assert cs.is_valid_email("not-an-email") is False


def test_is_valid_email_logs_and_returns_false_for_unexpected_error(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    validate_email = Mock(side_effect=RuntimeError("validator-down"))
    monkeypatch.setattr(cs, "validate_email", validate_email)

    with caplog.at_level("ERROR"):
        assert cs.is_valid_email("valid@example.com") is False

    assert "Unexpected error occurred when validating email" in caplog.text


@pytest.mark.parametrize(
    "phone_number",
    [None, "", 1234, "+0 1234-5678", "+5061234-5678", "+506 123-5678", "+506 12345-6789"],
)
def test_validate_phone_number_rejects_invalid_values(phone_number: object) -> None:
    assert cs.validate_phone_number(phone_number) is None


def test_validate_phone_number_accepts_and_normalizes_valid_format() -> None:
    assert cs.validate_phone_number("  +506 1234-5678  ") == "+506 1234-5678"


def test_validate_customer_data_accepts_valid_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cs, "is_valid_email", Mock(return_value=True))
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value="+506 1234-5678"))

    assert cs.validate_customer_data("valid@example.com", "+506 1234-5678") is None


def test_validate_customer_data_raises_for_invalid_email(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cs, "is_valid_email", Mock(return_value=False))

    with pytest.raises(ValueError, match="Invalid email address"):
        cs.validate_customer_data("invalid", "+506 1234-5678")


def test_validate_customer_data_raises_for_invalid_phone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cs, "is_valid_email", Mock(return_value=True))
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value=None))

    with pytest.raises(ValueError, match="Invalid phone number"):
        cs.validate_customer_data("valid@example.com", "bad-phone")


def test_get_customer_by_phone_number_uses_filter_and_first(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = object()
    query = Mock()
    query.filter_by.return_value = query
    query.first.return_value = expected
    monkeypatch.setattr(cs, "CustomerModel", SimpleNamespace(query=query))

    customer = cs.get_customer_by_phone_number("+506 1234-5678")

    query.filter_by.assert_called_once_with(phone_number="+506 1234-5678")
    query.first.assert_called_once_with()
    assert customer is expected


def test_customer_exists_returns_true_or_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cs, "get_customer_by_phone_number", Mock(side_effect=[object(), None]))

    assert cs.customer_exists("+506 1234-5678") is True
    assert cs.customer_exists("+506 9999-9999") is False


def test_create_customer_raises_for_missing_required_fields() -> None:
    with pytest.raises(ValueError, match="Missing required fields: name, phone_number"):
        cs.create_customer({"name": "", "phone_number": None})


def test_create_customer_raises_when_phone_cannot_be_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cs, "validate_customer_data", Mock())
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value=None))

    with pytest.raises(ValueError, match="Invalid phone number"):
        cs.create_customer({"name": "Alice", "phone_number": "bad", "email": "a@b.com"})


def test_create_customer_raises_when_customer_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cs, "validate_customer_data", Mock())
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value="+506 1234-5678"))
    monkeypatch.setattr(cs, "customer_exists", Mock(return_value=True))

    with pytest.raises(ValueError, match="Customer already exists"):
        cs.create_customer({"name": "Alice", "phone_number": "+506 1234-5678", "email": "a@b.com"})


def test_create_customer_persists_new_customer(monkeypatch: pytest.MonkeyPatch) -> None:
    created = SimpleNamespace(id=99)
    customer_model = Mock(return_value=created)
    session = SimpleNamespace(add=Mock())

    monkeypatch.setattr(cs, "validate_customer_data", Mock())
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value="+506 1234-5678"))
    monkeypatch.setattr(cs, "customer_exists", Mock(return_value=False))
    monkeypatch.setattr(cs, "CustomerModel", customer_model)
    monkeypatch.setattr(cs.db, "session", session)
    monkeypatch.setattr(cs, "_commit_or_rollback", Mock())

    payload = {"name": "Alice", "phone_number": " +506 1234-5678 ", "email": "a@b.com"}
    customer = cs.create_customer(payload)

    assert payload["phone_number"] == "+506 1234-5678"
    customer_model.assert_called_once_with(**payload)
    session.add.assert_called_once_with(created)
    cs._commit_or_rollback.assert_called_once_with()
    assert customer is created


def test_create_customer_from_form_raises_for_missing_required_fields() -> None:
    with pytest.raises(ValueError, match="Missing required fields: name, phone_number"):
        cs.create_customer_from_form({"name": None, "phone_number": ""})


def test_create_customer_from_form_raises_when_phone_cannot_be_normalized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cs, "validate_customer_data", Mock())
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value=None))

    with pytest.raises(ValueError, match="Invalid phone number"):
        cs.create_customer_from_form({"name": "Alice", "phone_number": "bad", "email": "a@b.com"})


def test_create_customer_from_form_returns_existing_customer(monkeypatch: pytest.MonkeyPatch) -> None:
    existing = SimpleNamespace(id=7)

    monkeypatch.setattr(cs, "validate_customer_data", Mock())
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value="+506 1234-5678"))
    monkeypatch.setattr(cs, "get_customer_by_phone_number", Mock(return_value=existing))

    customer = cs.create_customer_from_form(
        {"name": "Alice", "phone_number": "+506 1234-5678", "email": "a@b.com"}
    )

    assert customer is existing


def test_create_customer_from_form_creates_new_customer(monkeypatch: pytest.MonkeyPatch) -> None:
    created = SimpleNamespace(id=11)
    customer_model = Mock(return_value=created)
    session = SimpleNamespace(add=Mock())

    monkeypatch.setattr(cs, "validate_customer_data", Mock())
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value="+506 1234-5678"))
    monkeypatch.setattr(cs, "get_customer_by_phone_number", Mock(return_value=None))
    monkeypatch.setattr(cs, "CustomerModel", customer_model)
    monkeypatch.setattr(cs.db, "session", session)
    monkeypatch.setattr(cs, "_commit_or_rollback", Mock())

    payload = {"name": "Alice", "phone_number": " +506 1234-5678 ", "email": "a@b.com"}
    customer = cs.create_customer_from_form(payload)

    assert payload["phone_number"] == "+506 1234-5678"
    customer_model.assert_called_once_with(**payload)
    session.add.assert_called_once_with(created)
    cs._commit_or_rollback.assert_called_once_with()
    assert customer is created


def test_create_customer_from_form_handles_integrity_race_and_returns_existing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created = SimpleNamespace(id=13)
    existing = SimpleNamespace(id=42)
    customer_model = Mock(return_value=created)
    session = SimpleNamespace(add=Mock())

    monkeypatch.setattr(cs, "validate_customer_data", Mock())
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value="+506 1234-5678"))
    monkeypatch.setattr(
        cs,
        "get_customer_by_phone_number",
        Mock(side_effect=[None, existing]),
    )
    monkeypatch.setattr(cs, "CustomerModel", customer_model)
    monkeypatch.setattr(cs.db, "session", session)
    monkeypatch.setattr(cs, "_commit_or_rollback", Mock(side_effect=_integrity_error()))

    payload = {"name": "Alice", "phone_number": "+506 1234-5678", "email": "a@b.com"}
    customer = cs.create_customer_from_form(payload)

    assert customer is existing


def test_create_customer_from_form_reraises_integrity_error_when_existing_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created = SimpleNamespace(id=13)
    customer_model = Mock(return_value=created)
    session = SimpleNamespace(add=Mock())

    monkeypatch.setattr(cs, "validate_customer_data", Mock())
    monkeypatch.setattr(cs, "validate_phone_number", Mock(return_value="+506 1234-5678"))
    monkeypatch.setattr(cs, "get_customer_by_phone_number", Mock(side_effect=[None, None]))
    monkeypatch.setattr(cs, "CustomerModel", customer_model)
    monkeypatch.setattr(cs.db, "session", session)
    monkeypatch.setattr(cs, "_commit_or_rollback", Mock(side_effect=_integrity_error()))

    with pytest.raises(IntegrityError):
        cs.create_customer_from_form(
            {"name": "Alice", "phone_number": "+506 1234-5678", "email": "a@b.com"}
        )
