from types import SimpleNamespace
from unittest.mock import Mock

from services import form_service


def test_submit_contact_form_creates_customer_and_returns_processing_result(monkeypatch):
    customer = SimpleNamespace(id=17)
    create_customer = Mock(return_value=customer)
    monkeypatch.setattr(form_service, "create_customer_from_form", create_customer)

    payload = {
        "customer": {"name": "Alice", "email": "a@example.com", "phone_number": "+506 1234-5678"},
        "store": "san-sebastian",
        "products": ["bed"],
        "budget": 1200,
        "purchase_time_horizon": "within_one_month",
        "customer_comments": "Call after 5 PM.",
    }

    result = form_service.submit_contact_form(payload)

    create_customer.assert_called_once_with(payload["customer"])
    assert result == {"customer_id": 17, "processing_complete": False}