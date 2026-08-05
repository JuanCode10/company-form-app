## API Conventions

The initial API should follow these conventions:

- Request and response bodies use JSON
- JSON property names use `snake_case`
- Resource names use plural nouns
- Internal database records use UUIDsa
- Database UUIDs are not required in public customer form submissions
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

The public frontend should not need to know the internal database UUIDs assigned to stores and products.

The customer form will present readable store and product names through dropdown menus or other predefined input controls.

The frontend may internally associate each displayed label with a stable client-facing value.

For example:

```javascript
const stores = {
    "San José": "san-jose",
    Heredia: "heredia",
};
```

However, the exact client-facing identifier strategy does not need to be finalized during the initial design.

The first implementation may submit the displayed names directly:

```json
{
    "store": "San José",
    "products": ["Bed", "Nightstand"]
}
```

A future implementation may instead submit stable codes:

```json
{
    "store": "san-jose",
    "products": ["bed", "nightstand"]
}
```

In either case, the client will not submit internal database UUIDs.

The backend will be responsible for resolving the submitted values to the corresponding `Store` and `Product` database records.

The database relationships will continue to use UUID foreign keys internally:

```text
Lead.store_id -> Store.id
LeadProduct.product_id -> Product.id
```

This keeps the public API separated from the database implementation.

Changing from names to stable codes or database identifiers later would require a coordinated API and frontend update, but it would not require redesigning the underlying database relationships.

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

## Initial Endpoints

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

This endpoint represents the complete customer form submission.

The frontend sends customer information and lead information together in one request. The backend is responsible for resolving the submitted store and product values and storing the information in the appropriate database tables.

### Request Body

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

### Initial Request Fields

| Field                   | Type             | Required    | Description                                                     |
| ----------------------- | ---------------- | ----------- | --------------------------------------------------------------- |
| `customer`              | Object           | Yes         | Customer identity and contact information                       |
| `customer.name`         | String           | Yes         | Customer's full name                                            |
| `customer.email`        | String           | Conditional | Customer's email address                                        |
| `customer.phone_number` | String           | Conditional | Customer's phone number                                         |
| `store`                 | String           | Yes         | Client-facing name or code representing the selected store      |
| `products`              | Array of strings | Yes         | Client-facing names or codes representing the selected products |
| `budget`                | Number           | Yes         | Customer's estimated purchase budget                            |
| `purchase_time_horizon` | String           | Yes         | Estimated timeframe for the purchase                            |
| `customer_comments`     | String           | No          | Additional questions, requests, or information                  |

At least one contact method should be required. The exact rule for requiring email, phone number, or both remains an implementation decision.

The exact format used by `store` and `products` also remains an implementation decision. The initial version may use names, while a future version may use stable client-facing codes.

### Backend Processing

After receiving a valid request, the backend should:

1. Normalize the submitted email address and phone number
2. Attempt to identify an existing customer
3. Create a customer if no matching customer exists
4. Normalize the submitted store value
5. Query the `Store` model to find the corresponding active store
6. Normalize every submitted product value
7. Query the `Product` model to find the corresponding active products
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

### Successful Response

Status:

```text
201 Created
```

Response body:

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

The generated lead UUID may be returned as a reference for the newly created resource.

The public response should not expose internal store IDs, product IDs, database relationships, internal notes, or unrelated customer history.

## Store Retrieval

### Endpoint

```text
GET /api/v1/stores
```

This endpoint returns the store locations that may be selected in the customer form.

The response should provide the information required to build the dropdown menu without exposing database UUIDs.

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
            "value": "San José",
            "label": "San José"
        },
        {
            "value": "Heredia",
            "label": "Heredia"
        }
    ]
}
```

The `label` represents the text displayed to the customer.

The `value` represents the value submitted by the frontend. During the initial implementation, the value and label may be identical.

A future version may use a stable code as the value:

```json
{
    "value": "san-jose",
    "label": "San José"
}
```

Only stores currently available for customer selection should be returned.

## Product Retrieval

### Endpoint

```text
GET /api/v1/products
```

This endpoint returns the products or product categories available in the customer form.

The response should provide the information required to build the product selection controls without exposing database UUIDs.

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
            "value": "Bed",
            "label": "Bed",
            "description": "Beds and related bedroom furniture"
        },
        {
            "value": "Nightstand",
            "label": "Nightstand",
            "description": "Nightstands and related bedroom furniture"
        }
    ]
}
```

During the initial implementation, the submitted value and displayed label may be identical.

A future version may use stable codes:

```json
{
    "value": "bed",
    "label": "Bed",
    "description": "Beds and related bedroom furniture"
}
```

Only active products should be returned.

## Data Validation

Input validation will be implemented using Marshmallow schemas.

The API should validate:

- Required fields
- Customer name length
- Email format
- Phone-number format
- Presence of at least one contact method
- Budget type and allowed range
- Allowed purchase time-horizon values
- Presence of a store value
- Presence of at least one product value
- Maximum number of selected products
- Maximum customer-comment length
- Store existence
- Product existence
- Product active status
- Store active status

Validation should occur before database changes are committed.

Marshmallow will validate the structure and format of the request.

Database queries and business logic will validate that submitted store and product values correspond to existing active records.

Database constraints should also be used where appropriate. API validation improves the client experience, while database constraints protect the stored data.

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
Query Product model
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
- Budget currency and storage format
- Exact customer uniqueness and matching rules
- Whether both email and phone number are required
- Final purchase time-horizon options
- Maximum allowed comment length
- Maximum number of products per lead
- Whether the initial store value uses a name or stable code
- Whether the initial product values use names or stable codes
- Whether store and product codes should later be stored in the database
- Automatic lead-priority calculation
- Store and product active-status behavior
- Authentication and employee role structure
- API rate limiting and spam prevention
- Cross-origin resource sharing configuration

These decisions should be resolved only when required by an implementation step.
