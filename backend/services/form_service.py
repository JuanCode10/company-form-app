# Import libraries

# Import other services
from services.customer_service import create_customer_from_form

# Import logger
import logging
logger = logging.getLogger(__name__)


# todo: code form service logic

def submit_contact_form(form_payload):
    # This functions receive the full payload from the /leads endpoint to submit a form
    logger.info("Processing form_payload...")
    
    # 1. Create/update customer, call the customer_service functions
    logger.info("Creating customer...")
    customer = create_customer_from_form(form_payload["customer"])
    logger.info("Cutomer id: %s", customer.id)

    # todo:
    # 2. Create/update store, call the store_service functions
    # 3. Create/update product, call product_service functions
    # 4. Create the lead, call lead_service functions
    pass