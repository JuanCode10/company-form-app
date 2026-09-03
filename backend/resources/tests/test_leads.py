from unittest.mock import Mock

from app import create_app
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
        "purchase_time_horizon": "within_one_month",
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