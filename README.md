# Company Form App

## Project Overview

This repository contains the code and documentation for a company form application.

This is a personal project intended to help my family's business improve its lead-gathering process, with the goal of increasing lead conversion rates.

## Current System

Currently, the company's primary source of customer reach and exposure is social media. Links to direct WhatsApp conversations are provided through the company's social media pages, stories, and posts.

After the initial contact is made through a central phone number, client information is gathered manually. The client is then internally assigned to a sales representative.

Based on my current understanding, clients are assigned using workload-based criteria alongside any preferences or information provided by the client. The exact assignment process still needs to be confirmed with the business.

Once the client reaches this stage, a sales representative must manually gather additional information, including:

- Item or product of interest
- Available budget
- Additional comments, specific requests, or relevant information

## Current Implementation

The repository now contains an initial working form and backend intake slice:

- The Spanish-language contact form captures customer details, products, budget, purchase horizon, store, and comments.
- Client-side JavaScript trims and validates names and emails, normalizes Costa Rican phone numbers, collects selected products, and builds the documented JSON payload.
- The Flask application exposes `POST /leads`; its Marshmallow schema validates the payload structure and supported store and purchase-horizon values.
- Customer records use the submitted phone number as their unique key. The customer service normalizes the phone number and returns an existing customer for repeat submissions.
- SQLAlchemy is configured with SQLite by default (`sqlite:///data.db`), and the current `CustomerModel` is created when the application starts.

The form does not yet send a network request: `sendPayload` currently returns the validated payload. The backend currently creates or reuses the customer only; lead, store, and product persistence are not implemented.

## Future Objectives

The following objectives address the remaining intake and lead-management needs in later milestones:

- Complete the form submission round trip so customers receive an accurate success or error result from the API.
- Persist complete lead submissions in a local SQLite database, including the selected store and products.
- Introduce lead classification and prioritization after the stored lead workflow is established.
- Build authenticated store and sales-representative workflows for assignment, follow-up, and lead resolution.
- Retain completed customer and lead history to support future communication and service.

## Desired Process

### 1. Customer Form Submission

Customers complete a form containing relevant qualification questions, including:

1. General item of interest, such as:
    - Bed
    - Table
    - Chairs
    - Sofa
    - Other

2. Estimated purchase budget
3. Estimated time horizon for completing the purchase
4. Preferred store location, selected from a dropdown menu
5. Personal and contact information:
    - Name
    - Email address
    - Phone number

6. Additional comments, specific requests, or questions

### 2. Backend Processing

After the form is submitted, the information is sent to the backend for processing.

The backend should:

1. Validate the submitted information
2. Store the lead and customer information in the database
3. Use the email address or phone number to identify possible existing customers
4. Associate the lead with the store selected by the customer
5. Assign an initial status to the lead
6. Calculate an initial lead priority or classification based on the submitted information

### 3. Store Management Interface

Each store should have access to a web interface that allows authorized employees to manage its leads.

The interface should:

1. Require authentication using store or employee credentials
2. Retrieve leads associated with the authenticated user's store
3. Display active leads in priority order, from highest to lowest
4. Allow a store administrator to assign leads to individual sales representatives
5. Record which sales representative is responsible for each lead
6. Update the lead status after assignment so that it is clearly identified as assigned or in progress

### 4. Sales Representative Interface

Each sales representative should have access to an authenticated web interface.

The interface should:

1. Display the leads assigned to the authenticated sales representative
2. Provide access to the relevant customer and lead information
3. Include a contact action that opens WhatsApp Web with a prepared message containing relevant customer information
4. Allow the sales representative to update the lead's status
5. Allow the sales representative to close the lead by recording:
    - Final resolution
    - Outcome of the interaction
    - Additional comments

6. Attach the recorded outcome and comments to the customer's history to support future contact, more personalized service, and better customer interactions

## Completed Milestone: Form Intake Foundation

The initial implementation established the form, payload construction, backend schema, customer service, and an initial SQLite-backed customer model.

## Next Milestone: Form Submission Round Trip

- Implement `sendPayload` with `fetch` and submit the JSON payload to `POST /leads`.
- Return a meaningful API response for accepted submissions and validation failures.
- Add form submission states for submitting, successful, and failed requests.
- Align the frontend request URL with the backend route and configure local cross-origin behavior if the applications use different origins.

## Following Milestone: Local SQLite Lead Storage

- Implement SQLite models and persistence for leads, stores, products, and lead-product associations.
- Resolve the submitted store and product values against locally seeded records.
- Create the complete lead submission in a transaction, associated with its customer.
- Replace the fixed acknowledgement with a response containing the persisted lead's public identifier and initial status.

## Initial Milestone Reference

The original milestone scope was:

### Backend

- Define and document the initial database design
- Define and document the initial Python REST API design

### Frontend

- Design the HTML form
- Define and document the client-side JSON payload

## Backend Documentation

- [Database Design](backend/docs/database-design.md)
- [API Design](backend/docs/api-design.md)

## Frontend Documentation

- [HTML Form Design](frontend/docs/html-form-design.md)
- [JSON Payload Design](frontend/docs/json-payload.md)
