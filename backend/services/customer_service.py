"""Customer-related service helpers."""

import logging
import re
from typing import Any

from email_validator import EmailNotValidError, validate_email
from sqlalchemy.exc import IntegrityError

from db import db
from models import CustomerModel

logger = logging.getLogger(__name__)


def _commit_or_rollback() -> None:
    """Commit the active transaction and roll back on failure."""
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def is_valid_email(email: str, check_deliverability: bool = False) -> bool:
    """
    Validate an email address.

    Args:
        email: Email address to validate.
        check_deliverability: Whether to check MX records.

    Returns:
        True when the email is valid, otherwise False.
    """
    try:
        validate_email(email, check_deliverability=check_deliverability)
        return True
    except EmailNotValidError:
        return False
    except Exception as e:
        logger.error("Unexpected error occurred when validating email: %s", e)
        return False


def validate_phone_number(phone_number: str | None) -> str | None:
    """
    Validate a phone number in the backend display format.

    Expected format: +<country_code> <4_digits>-<4_digits>
    Example: +506 1234-5678.

    Args:
        phone_number: Phone number to validate.

    Returns:
        The normalized phone number when valid, otherwise None.
    """
    if not phone_number or not isinstance(phone_number, str):
        return None

    candidate = phone_number.strip()

    # Frontend already sends display format; backend only verifies it.
    if not re.fullmatch(r"\+[1-9]\d{0,2}\s\d{4}-\d{4}", candidate):
        return None

    return candidate


def validate_customer_data(email: str | None, phone_number: str | None) -> None:
    """Validate customer payload fields used by this service.

    Email is optional, but when present it must be valid. Phone number is
    required and must match the backend display format.
    """
    if email and not is_valid_email(email):
        raise ValueError("Invalid email address")

    normalized_phone = validate_phone_number(phone_number)
    if not normalized_phone:
        raise ValueError("Invalid phone number")

    return None


def get_customer_by_phone_number(phone_number: str) -> CustomerModel | None:
    """Return the customer matching the given phone number, if any."""
    return CustomerModel.query.filter_by(phone_number=phone_number).first()


def customer_exists(phone_number: str) -> bool:
    """Check whether a customer exists for the given phone number."""
    return get_customer_by_phone_number(phone_number) is not None


def create_customer(customer_data: dict[str, Any]) -> CustomerModel:
    """Create a new customer record.

    Args:
        customer_data: Customer payload containing name, phone_number, and
            email.

    Returns:
        The newly created customer.
    """

    email = customer_data.get("email")
    name = customer_data.get("name")
    phone_number = customer_data.get("phone_number")

    if not name or not phone_number:
        raise ValueError("Missing required fields: name, phone_number")

    validate_customer_data(email, phone_number)

    normalized_phone = validate_phone_number(phone_number)
    if not normalized_phone:
        raise ValueError("Invalid phone number")

    if customer_exists(normalized_phone):
        raise ValueError("Customer already exists")

    customer_data["phone_number"] = normalized_phone

    customer = CustomerModel(**customer_data)
    db.session.add(customer)
    _commit_or_rollback()

    logger.info("Create new customer: %s", customer.id)
    return customer


def create_customer_from_form(form_customer_data: dict[str, Any]) -> CustomerModel:
    """Create a customer from form-submitted data.

    If the customer already exists, return the existing record instead of
    raising an error. This is used for idempotent form submissions.
    """

    email = form_customer_data.get("email")
    name = form_customer_data.get("name")
    phone_number = form_customer_data.get("phone_number")

    if not name or not phone_number:
        raise ValueError("Missing required fields: name, phone_number")

    validate_customer_data(email, phone_number)

    normalized_phone = validate_phone_number(phone_number)
    if not normalized_phone:
        raise ValueError("Invalid phone number")

    customer = get_customer_by_phone_number(normalized_phone)
    if customer is not None:
        logger.info("Customer already exists. Customer id: %s", customer.id)
        return customer

    form_customer_data["phone_number"] = normalized_phone

    customer = CustomerModel(**form_customer_data)
    db.session.add(customer)
    try:
        _commit_or_rollback()
    except IntegrityError:
        customer = get_customer_by_phone_number(normalized_phone)
        if customer is not None:
            logger.info(
                "Customer already exists after race. Customer id: %s",
                customer.id,
            )
            return customer
        raise

    return customer

