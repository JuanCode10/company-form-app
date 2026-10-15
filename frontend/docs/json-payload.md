# Client-Side JSON Payload Design

## Implementation Status

`buildPayload` currently constructs the payload, trims and validates the name and email, converts the budget to a number, and formats eight-digit Costa Rican phone numbers as `+506 1234-5678`.

`sendPayload` posts the payload as JSON to `http://127.0.0.1:5001/leads`. It returns the JSON response on success and throws an error for non-success HTTP responses. `submissionHandler` changes the submit button after success and displays a generic error message after failure.

## Purpose

This document defines the initial JSON payload created by the frontend and submitted to the REST API.

The payload represents one complete customer lead submission.

The frontend will gather information from the HTML form, convert it into a JavaScript object, serialize it as JSON, and send it to:

```text
POST /leads
```

The payload should contain business-level information required by the backend without exposing database implementation details.

## Design Principles

The initial payload should follow these principles:

- Use JSON as the request format
- Use `snake_case` property names
- Group customer information inside a `customer` object
- Represent multiple selected products as an array
- Send store and product-category values rather than internal database IDs
- Avoid sending fields generated or managed by the backend
- Avoid including undefined or unrelated information
- Keep the payload simple enough to construct from the HTML form

## Initial Payload

```json
{
    "customer": {
        "name": "Example Customer",
        "email": "customer@example.com",
        "phone_number": "+506 8888-7777"
    },
    "store": "san-sebastian",
    "products": ["bed"],
    "budget": 500000.50,
    "purchase_time_horizon": "one_month",
    "customer_comments": "I am looking for a queen-size bed."
}
```

## Payload Structure

| Field                   | JSON Type        |    Required | Source                        |
| ----------------------- | ---------------- | ----------: | ----------------------------- |
| `customer`              | Object           |         Yes | Customer-information section  |
| `customer.name`         | String           |         Yes | Full-name input               |
| `customer.email`         | String           | Yes         | Email input                   |
| `customer.phone_number` | String           | Yes         | Phone-number input            |
| `store`                 | String           |         Yes | Preferred-store select        |
| `products`              | Array of strings |         Yes | Selected product controls     |
| `budget`                | Number           |         Yes | Budget input                  |
| `purchase_time_horizon` | String           |         Yes | Purchase-time-horizon select  |
| `customer_comments`     | String (max 500) |         Yes | Additional-comments text area; empty string is allowed |

The current form and API require both email and phone number. The comments control is optional to fill in, but the payload includes `customer_comments`; an empty string is valid.

## Customer Object

Customer identity and contact information will be grouped inside the `customer` object.

Example:

```json
{
    "customer": {
        "name": "Example Customer",
        "email": "customer@example.com",
        "phone_number": "+506 8888-7777"
    }
}
```

Grouping this information makes the distinction between customer data and lead-specific data clear.

The same customer may submit multiple leads over time, but each form submission sends the customer information required to identify or create that customer.

The backend will determine whether a matching customer already exists.

The frontend should not attempt to identify or create customers separately.

## Store Value

The `store` field represents the customer's preferred store.

Initial example:

```json
{
    "store": "san-sebastian"
}
```

The frontend should not submit the store's internal database ID.

The current form submits a predefined store code:

```json
{
    "store": "san-sebastian"
}
```

The frontend should eventually use the `value` provided by a store-options response.

Example response:

```json
{
    "stores": [
        {
            "value": "san-sebastian",
            "label": "San Sebastián"
        }
    ]
}
```

This response shape is a future design; the current form does not load store options from the API. Its store choices are hard-coded as `la-mora` and `san-sebastian`.

When API option retrieval is implemented, the `label` will be displayed to the customer.

The `value` will be stored in the form control and included in the JSON payload.

This allows the API-facing value to change later without changing the text shown to the customer.

## Product Values

The `products` property contains all products selected by the customer.

Example:

```json
{
    "products": ["bed", "table"]
}
```

The property must be an array even when the customer selects only one product.

Example with one product:

```json
{
    "products": ["bed"]
}
```

The frontend should not submit internal product-category database IDs.

The current form submits product-category codes (`bed`, `table`, and `sofa`).

The current implementation submits stable codes:

```json
{
    "products": ["bed", "table"]
}
```

The values should eventually come from the product-options response rather than being manually inferred from the visible text; the current form has hard-coded options.

Example:

```json
{
    "products": [
        {
            "value": "bed",
            "label": "Cama",
            "description": "Categoría cama"
        }
    ]
}
```

The frontend displays the `label` and submits the `value`.

## Budget Value

The `budget` property should be sent as a JSON number rather than a formatted string.

Correct:

```json
{
    "budget": 500000
}
```

Avoid:

```json
{
    "budget": "₡500,000"
}
```

The frontend may display formatting to the customer, but it should remove symbols and separators before constructing the payload.

The form currently labels the amount in Costa Rican colones, but the JSON request and database store a unitless number.

The frontend and backend must agree on one currency and unit.

## Purchase Time Horizon

The `purchase_time_horizon` field should contain one predefined value.

Example:

```json
{
    "purchase_time_horizon": "one_month"
}
```

Possible initial values include:

```text
one_month
three_months
six_months
more_six_months
not_decided
```

The frontend may display a more natural label:

```text
Within one month
```

while submitting:

```text
one_month
```

The backend should reject values outside the supported list.

## Customer Comments

The `customer_comments` field contains optional free-form information, limited to 500 characters.

Example:

```json
{
    "customer_comments": "I am looking for a queen-size bed."
}
```

The current frontend sends comments as entered without trimming leading or trailing whitespace.

When no comments are entered, the frontend sends an empty string. The backend requires the field to be present and accepts an empty string.

## Fields Managed by the Backend

The frontend should not send fields that are created or controlled by the backend.

These include:

- Lead database ID
- Customer database ID
- Store database ID
- Product-category database IDs
- Lead status
- Lead priority
- Assigned sales representative
- Resolution
- Sales representative notes
- Created timestamp
- Updated timestamp

For example, the frontend should not send:

```json
{
    "status": "new",
    "priority": "high",
    "sales_representative_id": "example-id"
}
```

The backend is responsible for creating and managing these values.

## Form-to-Payload Mapping

| HTML Field Name         | Payload Property        |
| ----------------------- | ----------------------- |
| `customerName`          | `customer.name`         |
| `customerEmail`         | `customer.email`        |
| `customerPhone`         | `customer.phone_number` |
| `store`                 | `store`                 |
| `products`              | `products`              |
| `budget`                | `budget`                |
| `purchaseTimeHorizon`   | `purchase_time_horizon` |
| `customerComments`      | `customer_comments`     |

The HTML field names do not need to match the JSON structure exactly.

JavaScript will create the nested `customer` object.

## JavaScript Object Construction

A possible initial implementation is:

```javascript
const selectedProducts = Array.from(
    document.querySelectorAll('input[name="products"]:checked'),
).map((input) => input.value);

const payload = {
    customer: {
        name: document.querySelector("#customer-name").value.trim(),
        email: document.querySelector("#customer-email").value.trim(),
        phone_number: document.querySelector("#customer-phone").value.trim(),
    },
    store: document.querySelector("#store").value,
    products: selectedProducts,
    budget: Number(document.querySelector("#budget").value),
    purchase_time_horizon: document.querySelector("#purchase-time-horizon")
        .value,
    customer_comments: document.querySelector("#customer-comments").value,
};

console.log(payload);
```

This example is illustrative and may change as the final HTML structure is implemented.

Before sending the request, the frontend should confirm that `budget` was converted into a valid number.

## JSON Serialization

The JavaScript payload object should be serialized using:

```javascript
JSON.stringify(payload);
```

Example:

```javascript
const requestBody = JSON.stringify(payload);
```

The frontend should not manually build JSON using string concatenation.

## Planned API Request

The initial request may be sent using the browser Fetch API.

Example:

```javascript
const response = await fetch("/leads", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
});
```

The current frontend sends to `http://127.0.0.1:5001/leads`, while the backend enables CORS for `/leads` from any origin. The request URL is currently hard-coded and should be configured appropriately for other environments.

For example:

```text
Frontend: http://localhost:5500
Backend:  http://localhost:5000
```

In that case, the request URL and cross-origin configuration will need to be handled during implementation.

The current Flask route is `/leads`. Moving it to the target `/api/v1/leads` prefix requires a coordinated backend and frontend change.

## Current Client-Side Validation

Before sending the payload, JavaScript currently:

- Trims and validates the customer name and email.
- Normalizes the phone number to the Costa Rican display format.
- Requires a finite, positive numeric budget.
- Reads required store and purchase-time-horizon form controls.
- Sends all selected products, including an empty array if none are selected.
- Sends customer comments as entered; the HTML and API limit them to 500 characters.

The API requires customer name, email, phone number, store, products array, budget, purchase horizon, and comments. It restricts store and purchase-horizon values, requires a numeric budget, and limits comments to a string of at most 500 characters. The customer service checks email and phone formats while processing the customer, but these failures are not yet returned as structured validation responses. The API does not require a non-empty products array or enforce a positive budget.

Client-side validation does not replace backend validation because requests may be modified or sent without using the official form.

## Planned Successful Response

The current endpoint returns `200 OK` with `{"message": "Payload received"}` after creating or reusing the customer. It does not yet create a lead. A future response for a persisted lead could include:

```json
{
    "message": "Lead created successfully.",
    "lead": {
        "id": "a1886b1d-80ad-4700-909a-da4ffdbe4050",
        "status": "new",
        "created_at": "2026-07-24T19:30:00-06:00"
    }
}
```

The frontend may use the response to:

- Confirm that the request succeeded
- Display the success message
- Clear the form
- Prevent accidental duplicate submissions

The frontend does not need to display the generated lead ID to the customer.

## Planned Field-Specific Error Handling

The current frontend displays a generic error message. A future API contract could provide field-specific details, for example:

```json
{
    "code": "validation_error",
    "message": "The submitted information is invalid.",
    "errors": {
        "customer.email": ["Not a valid email address."]
    }
}
```

The frontend should:

1. Check whether the response was successful
2. Parse the JSON response when available
3. Display field-specific errors when possible
4. Display a general error for unexpected failures
5. Preserve the customer's entered information
6. Allow the customer to correct the form and retry

Example:

```javascript
const responseData = await response.json();

if (!response.ok) {
    throw new Error(responseData.message || "The form could not be submitted.");
}
```

The final error-handling implementation may become more detailed as the API contract is implemented.

## Example Minimal Valid Payload

A minimal valid payload may look like:

```json
{
    "customer": {
        "name": "Example Customer",
        "email": "customer@example.com",
        "phone_number": "+506 8888-7777"
    },
    "store": "san-sebastian",
    "products": ["sofa"],
    "budget": 350000,
    "purchase_time_horizon": "three_months",
    "customer_comments": ""
}
```

Both customer contact fields are required by the current API. The comments field is present as an empty string because the customer did not enter a comment.

## Open Design Decisions

The following decisions remain open:

- Whether both email and phone number should remain required
- Whether the unitless budget API/database value should include explicit currency metadata (the form currently labels it as Costa Rican colones)
- Minimum and maximum budget values
- Maximum number of products per submission
- Exact handling of field-specific API errors

These decisions should be resolved when required by implementation.
