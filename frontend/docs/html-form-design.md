# Contact Form Design

## Implementation Status

The HTML form is implemented at `frontend/contact-form/index.html` and is currently rendered in Spanish. It contains required inputs for name, email, phone, budget, purchase horizon, and store; optional comments; and checkbox product choices for bed, table, and sofa.

The form's module submit handler prevents the browser default, builds a payload, and submits it to `POST /leads` through `sendPayload`. It changes the submit button after a successful response and displays a generic error message after a failed request. Store and product options are currently static rather than loaded from the backend.

## Purpose

The customer form will collect the information required to create and qualify a new sales lead.

The form is the public entry point into the application. It should allow potential customers to describe what they are interested in, provide their contact information, select a preferred store, and submit additional relevant details.

The initial form will be implemented using HTML, CSS, and client-side JavaScript.

## Initial Scope

The first implementation will focus on:

1. Displaying the customer form
2. Collecting customer and lead information
3. Performing basic client-side validation
4. Converting the form values into a JavaScript object
5. Creating the JSON payload expected by the REST API
6. Sending the payload to the backend
7. Displaying a success or error message to the customer

The following features are outside the initial scope:

- Customer accounts
- Employee authentication
- Lead assignment
- Lead status management
- Automatic lead prioritization
- Customer history
- WhatsApp integration
- Advanced spam prevention
- Payment processing

## Form Sections

The form should be divided into clear sections so that customers can understand what information is being requested.

The initial sections are:

1. Customer information
2. Product interest
3. Purchase information
4. Preferred store
5. Additional comments
6. Submission confirmation

## Customer Information

This section collects the customer's identity and contact information.

| Field         | HTML Control           |    Required | Description              |
| ------------- | ---------------------- | ----------: | ------------------------ |
| Full name     | `<input type="text">`  |         Yes | Customer's full name     |
| Email address | `<input type="email">` | Yes         | Customer's email address |
| Phone number  | `<input type="tel">`   | Yes         | Customer's phone number  |

The current form and API require both email and phone number. The business may revisit this requirement.

The browser and client-side JavaScript validate the email, and the JavaScript normalizes Costa Rican phone numbers.

Example HTML structure:

```html
<section>
    <h2>Contact Information</h2>

    <label for="customer-name">Full name</label>
    <input
        type="text"
        id="customer-name"
        name="customerName"
        autocomplete="name"
        required
    />

    <label for="customer-email">Email address</label>
    <input
        type="email"
        id="customer-email"
        name="customerEmail"
        autocomplete="email"
        required
    />

    <label for="customer-phone">Phone number</label>
    <input
        type="tel"
        id="customer-phone"
        name="customerPhone"
        autocomplete="tel"
        required
    />
</section>
```

## Product Interest

The customer should be able to select one or more general products or product categories.

The current hard-coded form options are:

- Bed (`bed`)
- Table/dining set (`table`)
- Sofa (`sofa`)

Because one lead may contain multiple products, the input should support multiple selections.

Possible controls include:

- A group of checkboxes
- A multi-select control
- A custom selection component implemented later

Checkboxes may be the clearest option for the initial implementation because the available product list is expected to be relatively small.

Example:

```html
<fieldset>
    <legend>Which products are you interested in?</legend>

    <label>
        <input type="checkbox" name="products" value="bed" />
        Cama
    </label>

    <label>
        <input type="checkbox" name="products" value="table" />
        Comedor
    </label>

    <label>
        <input type="checkbox" name="products" value="sofa" />
        Sillón
    </label>
</fieldset>
```

The product options should eventually be retrieved from:

```text
GET /api/v1/products
```

The backend response will provide a display label and a client-facing value.

The current form submits stable codes with Spanish display labels:

```json
{
    "value": "bed",
    "label": "Cama"
}
```

The frontend should treat the value as an API-facing value and the label as customer-facing text.

Internal database IDs should not be exposed through the form.

The current form and API do not enforce that at least one product is selected; the frontend currently sends an empty array when none are checked.

## Purchase Information

This section collects information that may help qualify and prioritize the lead.

### Budget

| Property       | Initial Design          |
| -------------- | ----------------------- |
| HTML control   | `<input type="number">` |
| Required       | Yes                     |
| Expected value | Positive numeric amount |
| Currency       | Costa Rican colones (CRC), as displayed by the form |
| API field      | `budget`                |

Example:

```html
<label for="budget">Estimated budget</label>
<input type="number" id="budget" name="budget" min="1" step="any" required />
```

The form requires a positive numeric amount and permits decimals. The API currently accepts a number but does not enforce a positive range or retain currency metadata.

### Purchase Time Horizon

The purchase time horizon uses the following fixed values, validated by both the API schema and the database model:

| Displayed Label      | Submitted Value |
| -------------------- | --------------- |
| Within one month     | `one_month` |
| Within three months  | `three_months` |
| Within six months    | `six_months` |
| More than six months | `more_six_months` |
| I am not sure yet    | `not_decided` |

Example:

```html
<label for="purchase-time-horizon">
    When are you planning to make the purchase?
</label>

<select id="purchase-time-horizon" name="purchaseTimeHorizon" required>
    <option value="">Select an option</option>
    <option value="one_month">Within one month</option>
    <option value="three_months">Within three months</option>
    <option value="six_months">Within six months</option>
    <option value="more_six_months">More than six months</option>
    <option value="not_decided">I am not sure yet</option>
</select>
```

Changing these values requires updating the shared backend choices, form, and tests together.

## Preferred Store

The customer should select the store location that serves them best.

| Property     | Initial Design       |
| ------------ | -------------------- |
| HTML control | `<select>`           |
| Required     | Yes                  |
| API field    | `store`              |
| Data source  | Static form options (`la-mora`, `san-sebastian`); API lookup is planned |

Example initial structure:

```html
<label for="store">Preferred store</label>

<select id="store" name="store" required>
    <option value="">Select a store</option>
</select>
```

JavaScript should retrieve the available store options from the backend and add them to the dropdown.

Example backend response:

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

When API option retrieval is implemented, the customer will see the `label` while the form submits the corresponding `value`.

The current form uses the stable codes `la-mora` and `san-sebastian`.

Internal database IDs should not be required by the frontend.

## Additional Comments

Customers should be able to provide additional information that does not fit into the predefined fields.

| Property       | Initial Design      |
| -------------- | ------------------- |
| HTML control   | `<textarea>`        |
| Required       | No                  |
| API field      | `customer_comments` |
| Maximum length | 500 characters      |

Example:

```html
<label for="customer-comments"> Additional comments or requests </label>

<textarea
    id="customer-comments"
    name="customerComments"
    rows="5"
    maxlength="500"
    placeholder="Tell us anything else that may help us understand what you need."
></textarea>
```

The current JavaScript sends comments as entered; it does not trim leading or trailing whitespace. The HTML limits entry to 500 characters, and the API also rejects comments longer than 500 characters.

The backend must enforce the 500-character maximum even if client-side validation is also present.

## Field Summary

| Form Field            | HTML Control               |    Required | Payload Field           |
| --------------------- | -------------------------- | ----------: | ----------------------- |
| Full name             | Text input                 |         Yes | `customer.name`         |
| Email address         | Email input                |         Yes | `customer.email`        |
| Phone number          | Telephone input            |         Yes | `customer.phone_number` |
| Products              | Checkboxes or multi-select |          No | `products` (array may be empty) |
| Budget                | Number input               |         Yes | `budget`                |
| Purchase time horizon | Select menu                |         Yes | `purchase_time_horizon` |
| Preferred store       | Select menu                |         Yes | `store`                 |
| Additional comments   | Text area                  |          No | `customer_comments`     |

## Current Client-Side Validation

Client-side validation improves the customer experience by identifying obvious problems before a request is sent.

The current frontend:

- Requires and trims the customer's name and email, and checks the email format.
- Normalizes the phone number to the Costa Rican `+506 1234-5678` format.
- Converts the budget to a number and requires it to be finite and greater than zero.
- Uses required HTML controls for both contact methods, store, budget, and purchase time horizon.
- Limits comments to 500 characters in the HTML control.
- Does not require a product selection or trim customer comments before submission.

The API independently validates required fields, store and purchase-time-horizon choices, numeric budget, and the comments type and length. It currently requires both email and phone number. The request schema does not constrain their formats, though the customer service checks them when processing the submission; the API does not require at least one product.

Client-side validation does not replace backend validation because browser-side checks can be modified or bypassed.

## Form Submission Behavior

When the customer submits the form, JavaScript currently:

1. Prevents the browser's default form submission.
2. Reads the current form values and builds the JSON payload.
3. Sends it to `POST /leads` at the configured-in-code local URL.
4. Changes the submit button value after success or displays a generic error message after failure.

The current handler does not show a loading state, disable the button while submitting, or reset the form after success.

Conceptual flow:

```text
Customer completes form
        |
        v
Client-side validation
        |
        v
Create JavaScript object
        |
        v
Convert object to JSON
        |
        v
POST /leads
        |
        v
Display result
```

## Submission States

The form should clearly represent its current state.

Possible states include:

| State      | Expected Behavior                                             |
| ---------- | ------------------------------------------------------------- |
| Ready      | Customer can enter information and submit                     |
| Invalid    | Relevant validation messages are displayed                    |
| Submitting | Submit button is disabled and progress is indicated           |
| Successful | Confirmation message is displayed                             |
| Failed     | A clear error message is displayed and the customer may retry |

The initial implementation does not require advanced animations or complex state management.

A simple status message near the submit button is sufficient.

## Success Behavior

After a successful submission, the form should display a clear confirmation.

Example:

```text
Thank you. Your information was submitted successfully.
A sales representative will contact you soon.
```

The form may be cleared after a successful response.

Whether to clear the form immediately or only after the customer acknowledges the confirmation remains an implementation decision.

## Error Behavior

The frontend should distinguish between field-validation errors and general submission failures.

Examples include:

- Highlighting invalid fields
- Displaying validation messages near the corresponding field
- Displaying a general message when the server cannot be reached
- Allowing the customer to retry without losing their entered information

Example general error:

```text
We could not submit your information.
Please review the form and try again.
```

Internal exception messages, stack traces, and database errors must never be shown to the customer.

## Accessibility Considerations

The initial form should include basic accessibility practices:

- Every input should have an associated `<label>`
- Related product choices should use `<fieldset>` and `<legend>`
- Form controls should be usable with a keyboard
- Validation errors should be written as text and not communicated only through color
- Required fields should be clearly identified
- Placeholder text should not replace visible labels
- The page should use a logical heading structure
- Status messages should be understandable by assistive technologies

## Responsive Design

The form should be usable on both desktop and mobile devices.

This is especially important because customers may reach the form through social media applications on their phones.

The initial layout should:

- Use a single-column form on small screens
- Avoid fixed widths that exceed the viewport
- Provide sufficiently large touch targets
- Keep labels close to their corresponding fields
- Avoid requiring horizontal scrolling

## Security Considerations

The frontend should not be treated as a trusted source.

The form should not contain:

- Database credentials
- Internal database ID mappings
- API secrets
- Authentication secrets
- Private employee information
- Internal lead-priority rules

Environment secrets must never be placed in client-side JavaScript.

The backend remains responsible for validation, authorization, database access, and business rules.

## Open Design Decisions

The following decisions remain open:

- Final form visual style
- Final product categories
- Whether product selection uses checkboxes or a multi-select component
- Whether both email and phone number should remain required
- Exact phone-number validation rules
- Minimum and maximum budget values
- Whether current store and product codes should be replaced or mapped to database records
- Whether the form is cleared immediately after success
- Exact success and error messages

These decisions should be resolved when required by implementation or business feedback.
