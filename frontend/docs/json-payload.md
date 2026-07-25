# Initial Client-Side JSON Payload Design

## Purpose

This document defines the initial JSON payload created by the frontend and submitted to the REST API.

The payload represents one complete customer lead submission.

The frontend will gather information from the HTML form, convert it into a JavaScript object, serialize it as JSON, and send it to:

```text
POST /api/v1/leads
```

The payload should contain business-level information required by the backend without exposing database implementation details.

## Design Principles

The initial payload should follow these principles:

- Use JSON as the request format
- Use `snake_case` property names
- Group customer information inside a `customer` object
- Represent multiple selected products as an array
- Send store and product business values rather than internal database UUIDs
- Avoid sending fields generated or managed by the backend
- Avoid including undefined or unrelated information
- Keep the payload simple enough to construct from the HTML form

## Initial Payload

```json
{
  "customer": {
    "name": "Example Customer",
    "email": "customer@example.com",
    "phone_number": "88888888"
  },
  "store": "San José",
  "products": ["Bed", "Nightstand"],
  "budget": 500000,
  "purchase_time_horizon": "within_one_month",
  "customer_comments": "I am looking for a queen-size bed."
}
```

## Payload Structure

| Field                   | JSON Type        |    Required | Source                        |
| ----------------------- | ---------------- | ----------: | ----------------------------- |
| `customer`              | Object           |         Yes | Customer-information section  |
| `customer.name`         | String           |         Yes | Full-name input               |
| `customer.email`        | String           | Conditional | Email input                   |
| `customer.phone_number` | String           | Conditional | Phone-number input            |
| `store`                 | String           |         Yes | Preferred-store select        |
| `products`              | Array of strings |         Yes | Selected product controls     |
| `budget`                | Number           |         Yes | Budget input                  |
| `purchase_time_horizon` | String           |         Yes | Purchase-time-horizon select  |
| `customer_comments`     | String           |          No | Additional-comments text area |

At least one customer contact method should be present.

The exact requirement for email and phone number remains an open design decision.

## Customer Object

Customer identity and contact information will be grouped inside the `customer` object.

Example:

```json
{
  "customer": {
    "name": "Example Customer",
    "email": "customer@example.com",
    "phone_number": "88888888"
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
  "store": "San José"
}
```

The frontend should not submit the store's internal database UUID.

The exact client-facing representation remains flexible.

The initial version may submit a readable store name:

```json
{
  "store": "San José"
}
```

A future version may submit a stable code:

```json
{
  "store": "san-jose"
}
```

The frontend should use the `value` provided by the store-options response.

Example response:

```json
{
  "stores": [
    {
      "value": "San José",
      "label": "San José"
    }
  ]
}
```

The `label` is displayed to the customer.

The `value` is stored in the form control and included in the JSON payload.

This allows the API-facing value to change later without changing the text shown to the customer.

## Product Values

The `products` property contains all products selected by the customer.

Example:

```json
{
  "products": ["Bed", "Nightstand"]
}
```

The property must be an array even when the customer selects only one product.

Example with one product:

```json
{
  "products": ["Bed"]
}
```

The frontend should not submit internal product UUIDs.

The initial implementation may submit product names.

A future implementation may submit stable codes:

```json
{
  "products": ["bed", "nightstand"]
}
```

The values should come from the product-options response rather than being manually inferred from the visible text.

Example:

```json
{
  "products": [
    {
      "value": "Bed",
      "label": "Bed",
      "description": "Beds and related bedroom furniture"
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

The currency represented by the number remains an open design decision.

The frontend and backend must agree on one currency and unit.

## Purchase Time Horizon

The `purchase_time_horizon` field should contain one predefined value.

Example:

```json
{
  "purchase_time_horizon": "within_one_month"
}
```

Possible initial values include:

```text
immediately
within_one_month
within_three_months
within_six_months
more_than_six_months
undecided
```

The frontend may display a more natural label:

```text
Within one month
```

while submitting:

```text
within_one_month
```

The backend should reject values outside the supported list.

## Customer Comments

The `customer_comments` field contains optional free-form information.

Example:

```json
{
  "customer_comments": "I am looking for a queen-size bed."
}
```

Before constructing the payload, the frontend should trim leading and trailing whitespace.

When no comments are entered, the initial implementation may either:

- Send an empty string
- Send `null`
- Omit the property

The preferred behavior remains an implementation decision.

A consistent approach must be selected and supported by the backend schema.

## Fields Managed by the Backend

The frontend should not send fields that are created or controlled by the backend.

These include:

- Lead UUID
- Customer UUID
- Store UUID
- Product UUIDs
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
| `customer_name`         | `customer.name`         |
| `customer_email`        | `customer.email`        |
| `customer_phone`        | `customer.phone_number` |
| `store`                 | `store`                 |
| `products`              | `products`              |
| `budget`                | `budget`                |
| `purchase_time_horizon` | `purchase_time_horizon` |
| `customer_comments`     | `customer_comments`     |

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
  purchase_time_horizon: document.querySelector("#purchase-time-horizon").value,
  customer_comments: document.querySelector("#customer-comments").value.trim(),
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

## API Request

The initial request may be sent using the browser Fetch API.

Example:

```javascript
const response = await fetch("/api/v1/leads", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(payload),
});
```

During local development, the frontend and backend may run on different addresses or ports.

For example:

```text
Frontend: http://localhost:5500
Backend:  http://localhost:5000
```

In that case, the request URL and cross-origin configuration will need to be handled during implementation.

The final deployment arrangement has not yet been defined.

## Client-Side Validation Before Submission

Before creating or sending the payload, JavaScript should confirm:

- Customer name is not empty
- At least one contact method is present
- Email format is acceptable when provided
- Phone-number format is acceptable when provided
- Store value is present
- At least one product is selected
- Budget is a valid number
- Budget is within the allowed range
- Purchase time horizon is present
- Customer comments do not exceed the allowed length

The frontend should not send the request when known validation errors are present.

Client-side validation does not replace backend validation.

## Backend Validation Responsibility

The REST API remains responsible for validating the complete request.

The backend should verify:

- Required properties are present
- Property types are correct
- Unknown properties are rejected or handled consistently
- Email and phone formats are valid
- At least one contact method is present
- Store value corresponds to an active store
- Product values correspond to active products
- Budget is valid
- Purchase time horizon is supported
- Comment length is valid

The frontend cannot be considered trusted because requests may be modified or sent without using the official form.

## Successful Response Handling

A successful lead submission is expected to return:

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

The frontend does not need to display the generated lead UUID to the customer.

## Error Response Handling

A validation error may return:

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

## Example Minimal Payload

A minimal valid payload may look like:

```json
{
  "customer": {
    "name": "Example Customer",
    "email": "",
    "phone_number": "88888888"
  },
  "store": "Heredia",
  "products": ["Sofa"],
  "budget": 350000,
  "purchase_time_horizon": "within_three_months",
  "customer_comments": ""
}
```

This example assumes:

- A phone number is sufficient as the contact method
- Empty optional strings are accepted
- Store and product names are used as client-facing values

These assumptions must be confirmed during implementation.

## Open Design Decisions

The following decisions remain open:

- Whether both email and phone number are required
- Whether absent optional fields are empty strings, `null`, or omitted
- Budget currency and unit
- Minimum and maximum budget values
- Final purchase time-horizon values
- Whether store values use names or stable codes
- Whether product values use names or stable codes
- Maximum number of products per submission
- Maximum comment length
- Cross-origin request configuration during local development
- Whether the frontend and backend share the same deployment origin
- Exact handling of field-specific API errors

These decisions should be resolved when required by implementation.
