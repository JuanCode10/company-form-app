## Implementation Status

The current Flask application registers one public endpoint:

| Method | Endpoint | Current behavior                                                                                                                                                 |
| ------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST` | `/leads` | Validates the form payload, creates or reuses a customer by normalized phone number, and returns `200 OK` with `{"message": "Payload received"}`. |

The route is currently `/leads`, not `/api/v1/leads`. The service does not yet create a lead or resolve and persist store and product values. `GET /stores`, `GET /products`, and `/health` are not implemented. Marshmallow request-schema failures return `422`; customer-service validation errors are not yet mapped to structured responses. The frontend displays a generic error message for failed requests.

## Target API Conventions

The initial API should follow these conventions:

- Request and response bodies use JSON
- JSON property names use `snake_case`
- Resource names use plural nouns
- Internal database records use database-managed numeric IDs
- Database IDs are not required in public customer form submissions
- Public requests use business-level values for stores and products
- Datetimes use ISO 8601 format
- Public API endpoints use the `/api/v1` prefix
- HTTP methods describe the requested operation
- API responses use appropriate HTTP status codes
- Validation and server errors use a consistent response structure
- Internal database details should not be exposed to clients

## Application Structure

The implementation should follow a services-based architecture in which the main business workflow logic is contained in service modules, while the endpoint blueprints are organized under the `backend/resources` directory.

This separation keeps the API layer focused on request handling and delegation, while the services layer contains the core logic for each workflow.

## Client-Facing Store and Product Values

The public frontend should not need to know the internal database IDs assigned to stores and product categories.

The customer form will present readable store and product names through dropdown menus or other predefined input controls.

The frontend may internally associate each displayed label with a stable client-facing value.

For example:

```javascript
const stores = {
    "La Mora": "la-mora",
    "San Sebastián": "san-sebastian",
};
```

The current form submits stable client-facing codes:

```json
{
    "store": "san-sebastian",
    "products": ["bed"]
}
```

The client does not submit internal database IDs.

The backend should resolve these values to the corresponding `Store` and `ProductCategory` database records; that resolution is not implemented yet.

The database relationships use numeric foreign keys internally:

```text
Lead.store_id -> Store.id
LeadProductCategory.product_category_id -> ProductCategory.id
```

This keeps the public API separated from the database implementation.

Changing these public codes later would require a coordinated API and frontend update, but it would not require redesigning the underlying database relationships.

## Initial Resources

The initial API will operate primarily on the following resources:

| Resource  | Description                                                       |
| --------- | ----------------------------------------------------------------- |
| Leads     | Potential sales opportunities submitted through the customer form |
| Customers | People who submit one or more leads                               |
| Stores    | Store locations available for customer selection                  |
| Products  | General products or product categories that customers can select  |

A public customer submission represents one complete lead-generation action.

The frontend should not need to create customers, leads, or database relationships through separate requests.

## Planned Endpoints

| Method | Endpoint           | Purpose                                 | Authentication |
| ------ | ------------------ | --------------------------------------- | -------------- |
| `POST` | `/api/v1/leads`    | Submit and create a new customer lead   | Public         |
| `GET`  | `/api/v1/stores`   | Retrieve the available store options    | Public         |
| `GET`  | `/api/v1/products` | Retrieve the available product options  | Public         |
| `GET`  | `/health`          | Confirm that the API service is running | Public         |

The endpoint list may expand in future milestones.

## Lead Submission

### Endpoint

```text
POST /api/v1/leads
```

This is the target route for a future version. The currently registered route is `POST /leads`.

This endpoint represents the complete customer form submission.

The frontend sends customer information and lead information together in one request. The backend is responsible for resolving the submitted store and product values and storing the information in the appropriate database tables.

### Request Body

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

### Initial Request Fields

| Field                   | Type             | Required    | Description                                                     |
| ----------------------- | ---------------- | ----------- | --------------------------------------------------------------- |
| `customer`              | Object           | Yes         | Customer identity and contact information                       |
| `customer.name`         | String           | Yes         | Customer's full name                                            |
| `customer.email`         | String           | Yes         | Customer's email address                                        |
| `customer.phone_number` | String           | Yes         | Customer's phone number                                         |
| `store`                 | String           | Yes         | Client-facing name or code representing the selected store      |
| `products`              | Array of strings | Yes         | Client-facing names or codes representing the selected products |
| `budget`                | Number           | Yes         | Customer's estimated purchase budget                            |
| `purchase_time_horizon` | String           | Yes         | One of `one_month`, `three_months`, `six_months`, `more_six_months`, or `not_decided` |
| `customer_comments`     | String (max 500) | Yes         | Additional questions, requests, or information; empty string is allowed |

The current form and API require both email and phone number. The business may revisit this policy.

The current form submits stable codes for stores (`la-mora`, `san-sebastian`) and product categories (`bed`, `table`, `sofa`).

### Backend Processing

After receiving a valid request, the backend should:

1. Normalize the submitted email address and phone number
2. Attempt to identify an existing customer
3. Create a customer if no matching customer exists
4. Normalize the submitted store value
5. Query the `Store` model to find the corresponding active store
6. Normalize every submitted product value
7. Query the `ProductCategory` model to find the corresponding active categories
8. Reject the request if the submitted store is unknown or inactive
9. Reject the request if any submitted product is unknown or inactive
10. Create the lead
11. Set the initial lead status to `new`
12. Associate the lead with the resolved store
13. Associate the lead with the resolved products
14. Commit the complete operation to the database
15. Return the created lead identifier

Customer creation, lead creation, and product association should be completed as one database transaction.

If any required database operation fails, the transaction should be rolled back so that incomplete customer or lead records are not retained.

### Target Successful Response

Status:

```text
201 Created
```

Response body:

```json
{
    "message": "Lead created successfully.",
    "lead": {
        "id": 1234,
        "status": "new",
        "created_at": "2026-07-24T19:30:00-06:00"
    }
}
```

The generated numeric lead ID may be returned as a reference for the newly created resource.

The public response should not expose internal store IDs, product IDs, database relationships, internal notes, or unrelated customer history.

## Store Retrieval

### Endpoint

```text
GET /api/v1/stores
```

This endpoint returns the store locations that may be selected in the customer form.

The response should provide the information required to build the dropdown menu without exposing database IDs.

### Successful Response

Status:

```text
200 OK
```

Response body:

```json
{
    "stores": [
        {
            "value": "la-mora",
            "label": "La Mora"
        },
        {
            "value": "san-sebastian",
            "label": "San Sebastián"
        }
    ]
}
```

The `label` represents the text displayed to the customer.

The `value` is the stable code submitted by the current frontend:

```json
{
    "value": "san-sebastian",
    "label": "San Sebastián"
}
```

Only stores currently available for customer selection should be returned.

## Product Retrieval

### Endpoint

```text
GET /api/v1/products
```

This endpoint returns the products or product categories available in the customer form.

The response should provide the information required to build the product selection controls without exposing database IDs.

### Successful Response

Status:

```text
200 OK
```

Response body:

```json
{
    "products": [
        {
            "value": "bed",
            "label": "Cama",
            "description": "Categoría cama"
        },
        {
            "value": "table",
            "label": "Comedor",
            "description": "Categoría comedor"
        },
        {
            "value": "sofa",
            "label": "Sillón",
            "description": "Categoría sillón"
        }
    ]
}
```

The current form submits stable codes:

```json
{
    "value": "bed",
    "label": "Cama",
    "description": "Categoría cama"
}
```

Only active products should be returned.

## Current Validation

`FormPayloadSchema` currently requires all of the following fields:

- `customer.name`, `customer.email`, and `customer.phone_number`
- `store`, restricted to `la-mora` or `san-sebastian`
- `products` as a list of strings
- `budget` as a floating-point number
- `purchase_time_horizon`, restricted to the configured choices
- `customer_comments` as a string of at most 500 characters

Phone numbers are normalized by the customer service to the `+506 1234-5678` format. Customer identity is currently determined by the normalized phone number; email is stored but is not unique.

## Remaining Validation Work

The current Marshmallow schema validates required fields, the supported store and purchase-horizon values, budget as a number, and comments as a string of at most 500 characters. The lead model additionally stores budget as a non-null float, allows comments to be null, and restricts purchase horizons to the configured enum values.

The request schema does not constrain email or phone formats, although the customer service checks them while processing the customer. These service errors are not yet translated into structured validation responses. The API also does not require at least one selected product, enforce a positive budget range, or resolve store and product values against active database records. These gaps should be addressed before full lead persistence.

## Store and Product Resolution

The API must convert the client-facing `store` and `products` values into database entities.

Conceptually:

```text
Submitted store value
        |
        v
Normalize value
        |
        v
Query Store model
        |
        v
Store database entity
```

For products:

```text
Submitted product values
        |
        v
Normalize each value
        |
        v
Query ProductCategory model
        |
        v
Product database entities
```

Possible normalization includes:

- Removing leading and trailing whitespace
- Applying consistent capitalization
- Comparing values without case sensitivity
- Converting display names into predefined codes

The backend must not accept arbitrary store or product values simply because they are valid strings.

Each value must correspond to a known and active database record.

## Open Design Decisions

The following decisions remain open:

- Database engine to use in deployment
- Whether to store currency metadata; the form currently labels its budget in Costa Rican colones, while the API accepts a unitless number
- Exact customer uniqueness and matching rules
- Whether both email and phone number should remain required
- Maximum number of products per lead
- Whether store and product codes should be configurable rather than hard-coded in the initial form
- Automatic lead-priority calculation
- Store and product active-status behavior
- Authentication and employee role structure
- API rate limiting and spam prevention
- Restricting the current wildcard cross-origin resource sharing configuration for deployment

These decisions should be resolved only when required by an implementation step.
