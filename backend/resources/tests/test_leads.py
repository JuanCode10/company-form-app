from unittest.mock import Mock

import pytest
from sqlalchemy.exc import StatementError

from app import create_app
from db import db
from models import LeadModel
from resources import leads


def _valid_payload():
    return {
        "customer": {
            "name": "Alice",
            "email": "alice@example.com",
            "phone_number": "+506 1234-5678",
        },
        "store": "san-sebastian",
        "products": ["bed"],
        "budget": 1200,
        "purchase_time_horizon": "one_month",
        "customer_comments": "Call after 5 PM.",
    }


def test_post_leads_delegates_validated_payload_and_returns_acknowledgement(monkeypatch):
    submit_contact_form = Mock()
    monkeypatch.setattr(leads, "submit_contact_form", submit_contact_form)
    app = create_app("sqlite:///:memory:")

    response = app.test_client().post("/leads", json=_valid_payload())

    assert response.status_code == 200
    assert response.get_json() == {"message": "Payload received"}
    submit_contact_form.assert_called_once_with(_valid_payload())


def test_post_leads_rejects_invalid_store_before_service_call(monkeypatch):
    submit_contact_form = Mock()
    monkeypatch.setattr(leads, "submit_contact_form", submit_contact_form)
    app = create_app("sqlite:///:memory:")
    payload = _valid_payload()
    payload["store"] = "unknown-store"

    response = app.test_client().post("/leads", json=payload)

    assert response.status_code == 422
    submit_contact_form.assert_not_called()


def test_post_leads_accepts_decimal_budget(monkeypatch):
    submit_contact_form = Mock()
    monkeypatch.setattr(leads, "submit_contact_form", submit_contact_form)
    app = create_app("sqlite:///:memory:")
    payload = _valid_payload()
    payload["budget"] = 1200.75

    response = app.test_client().post("/leads", json=payload)

    assert response.status_code == 200
    assert submit_contact_form.call_args.args[0]["budget"] == 1200.75


@pytest.mark.parametrize(
    "time_horizon",
    [
        "one_month",
        "three_months",
        "six_months",
        "more_six_months",
        "not_decided",
    ],
)
def test_post_leads_accepts_allowed_purchase_time_horizons(
    monkeypatch, time_horizon
):
    submit_contact_form = Mock()
    monkeypatch.setattr(leads, "submit_contact_form", submit_contact_form)
    app = create_app("sqlite:///:memory:")
    payload = _valid_payload()
    payload["purchase_time_horizon"] = time_horizon

    response = app.test_client().post("/leads", json=payload)

    assert response.status_code == 200


def test_post_leads_rejects_unlisted_purchase_time_horizon(monkeypatch):
    submit_contact_form = Mock()
    monkeypatch.setattr(leads, "submit_contact_form", submit_contact_form)
    app = create_app("sqlite:///:memory:")
    payload = _valid_payload()
    payload["purchase_time_horizon"] = "within_one_month"

    response = app.test_client().post("/leads", json=payload)

    assert response.status_code == 422
    submit_contact_form.assert_not_called()


def test_post_leads_accepts_customer_comments_at_500_characters(monkeypatch):
    submit_contact_form = Mock()
    monkeypatch.setattr(leads, "submit_contact_form", submit_contact_form)
    app = create_app("sqlite:///:memory:")
    payload = _valid_payload()
    payload["customer_comments"] = "x" * 500

    response = app.test_client().post("/leads", json=payload)

    assert response.status_code == 200


def test_post_leads_rejects_customer_comments_over_500_characters(monkeypatch):
    submit_contact_form = Mock()
    monkeypatch.setattr(leads, "submit_contact_form", submit_contact_form)
    app = create_app("sqlite:///:memory:")
    payload = _valid_payload()
    payload["customer_comments"] = "x" * 501

    response = app.test_client().post("/leads", json=payload)

    assert response.status_code == 422
    submit_contact_form.assert_not_called()


def test_post_leads_rejects_non_string_customer_comments(monkeypatch):
    submit_contact_form = Mock()
    monkeypatch.setattr(leads, "submit_contact_form", submit_contact_form)
    app = create_app("sqlite:///:memory:")
    payload = _valid_payload()
    payload["customer_comments"] = 123

    response = app.test_client().post("/leads", json=payload)

    assert response.status_code == 422
    submit_contact_form.assert_not_called()


def test_lead_model_rejects_unlisted_purchase_time_horizon():
    app = create_app("sqlite:///:memory:")

    with app.app_context():
        db.session.add(LeadModel(purchase_time_horizon="within_one_month"))

        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()