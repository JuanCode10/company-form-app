# Contact Form Design

## Implementation Status

The HTML form is implemented at `frontend/contact-form/index.html` and is currently rendered in Spanish. It contains required inputs for name, email, phone, budget, purchase horizon, and store; optional comments; and checkbox product choices for bed, table, and sofa.

The form's module submit handler prevents the browser default, builds a validated payload, and calls `sendPayload`. It does not yet make an HTTP request or display submission status. Store and product options are currently static rather than loaded from the backend.

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
| Email address | `<input type="email">` | Conditional | Customer's email address |
| Phone number  | `<input type="tel">`   | Conditional | Customer's phone number  |

At least one contact method should be required.

The exact rule for requiring email, phone number, or both remains an implementation decision.

Possible initial behavior:

- Full name is always required
- The customer must provide an email address, a phone number, or both
- Email format is validated by the browser and JavaScript
- Phone-number validation should allow the expected Costa Rican format without preventing future international support

Example HTML structure:

```html
<section>
    <h2>Contact Information</h2>

    <label for="customer-name">Full name</label>
    <input
        type="text"
        id="customer-name"
        name="customer_name"
        autocomplete="name"
        required
    />

    <label for="customer-email">Email address</label>
    <input
        type="email"
        id="customer-email"
        name="customer_email"
        autocomplete="email"
    />

    <label for="customer-phone">Phone number</label>
    <input
        type="tel"
        id="customer-phone"
        name="customer_phone"
        autocomplete="tel"
    />
</section>
```

## Product Interest

The customer should be able to select one or more general products or product categories.

Possible initial options include:

- Bed
- Table
- Chair
- Sofa
- Nightstand
- Other

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
        <input type="checkbox" name="products" value="Bed" />
        Bed
    </label>

    <label>
        <input type="checkbox" name="products" value="Table" />
        Table
    </label>

    <label>
        <input type="checkbox" name="products" value="Sofa" />
        Sofa
    </label>
</fieldset>
```

The product options should eventually be retrieved from:

```text
GET /api/v1/products
```

The backend response will provide a display label and a client-facing value.

For the initial implementation, these values may be identical:

```json
{
    "value": "Bed",
    "label": "Bed"
}
```

A future version may use a stable code:

```json
{
    "value": "bed",
    "label": "Bed"
}
```

The frontend should treat the value as an API-facing value and the label as customer-facing text.

Internal database UUIDs should not be exposed through the form.

At least one product should be selected before the form can be submitted.

## Purchase Information

This section collects information that may help qualify and prioritize the lead.

### Budget

| Property       | Initial Design          |
| -------------- | ----------------------- |
| HTML control   | `<input type="number">` |
| Required       | Yes                     |
| Expected value | Positive numeric amount |
| Currency       | To be defined           |
| API field      | `budget`                |

Example:

```html
<label for="budget">Estimated budget</label>
<input type="number" id="budget" name="budget" min="0" step="1" required />
```

The final currency and allowed budget range remain open design decisions.

### Purchase Time Horizon

The purchase time horizon should use predefined options instead of unrestricted text.

Possible initial values include:

| Displayed Label      | Submitted Value        |
| -------------------- | ---------------------- |
| As soon as possible  | `immediately`          |
| Within one month     | `within_one_month`     |
| Within three months  | `within_three_months`  |
| Within six months    | `within_six_months`    |
| More than six months | `more_than_six_months` |
| I am not sure yet    | `undecided`            |

Example:

```html
<label for="purchase-time-horizon">
    When are you planning to make the purchase?
</label>

<select id="purchase-time-horizon" name="purchase_time_horizon" required>
    <option value="">Select an option</option>
    <option value="immediately">As soon as possible</option>
    <option value="within_one_month">Within one month</option>
    <option value="within_three_months">Within three months</option>
    <option value="within_six_months">Within six months</option>
    <option value="more_than_six_months">More than six months</option>
    <option value="undecided">I am not sure yet</option>
</select>
```

The final list of options may change after discussing the qualification process with the business.

## Preferred Store

The customer should select the store location that serves them best.

| Property     | Initial Design       |
| ------------ | -------------------- |
| HTML control | `<select>`           |
| Required     | Yes                  |
| API field    | `store`              |
| Data source  | `GET /api/v1/stores` |

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

The customer sees the `label`, while the form submits the corresponding `value`.

The submitted value may initially be the store name. A stable client-facing code may be introduced later.

Internal database UUIDs should not be required by the frontend.

## Additional Comments

Customers should be able to provide additional information that does not fit into the predefined fields.

| Property       | Initial Design      |
| -------------- | ------------------- |
| HTML control   | `<textarea>`        |
| Required       | No                  |
| API field      | `customer_comments` |
| Maximum length | To be defined       |

Example:

```html
<label for="customer-comments"> Additional comments or requests </label>

<textarea
    id="customer-comments"
    name="customer_comments"
    rows="5"
    placeholder="Tell us anything else that may help us understand what you need."
></textarea>
```

JavaScript should trim leading and trailing whitespace before creating the request payload.

The backend must enforce the final maximum length even if client-side validation is also present.

## Field Summary

| Form Field            | HTML Control               |    Required | Payload Field           |
| --------------------- | -------------------------- | ----------: | ----------------------- |
| Full name             | Text input                 |         Yes | `customer.name`         |
| Email address         | Email input                | Conditional | `customer.email`        |
| Phone number          | Telephone input            | Conditional | `customer.phone_number` |
| Products              | Checkboxes or multi-select |         Yes | `products`              |
| Budget                | Number input               |         Yes | `budget`                |
| Purchase time horizon | Select menu                |         Yes | `purchase_time_horizon` |
| Preferred store       | Select menu                |         Yes | `store`                 |
| Additional comments   | Text area                  |          No | `customer_comments`     |

## Client-Side Validation

Client-side validation improves the customer experience by identifying obvious problems before a request is sent.

The frontend should initially validate:

- Full name is present
- At least one contact method is present
- Email has a valid format when provided
- Phone number has an acceptable format when provided
- At least one product is selected
- A store is selected
- Budget is present and greater than or equal to the allowed minimum
- Purchase time horizon is selected
- Customer comments do not exceed the allowed length

Client-side validation does not replace backend validation.

All submitted information must still be validated by the REST API because client-side checks can be modified or bypassed.

## Form Submission Behavior

When the customer submits the form, JavaScript should:

1. Prevent the browser's default form submission
2. Read the current form values
3. Trim and normalize appropriate text fields
4. Confirm that the required fields are valid
5. Collect all selected product values
6. Create the JavaScript payload object
7. Convert the object to JSON
8. Send it to `POST /api/v1/leads`
9. Disable the submit button while the request is being processed
10. Display a success or error message
11. Re-enable the submit button when appropriate

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
POST /api/v1/leads
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
- Internal database UUID mappings
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
- Whether both email and phone number are required
- Exact phone-number validation rules
- Budget currency
- Minimum and maximum budget values
- Final purchase time-horizon options
- Maximum comment length
- Whether store and product values use names or stable codes
- Whether the form is cleared immediately after success
- Exact success and error messages

These decisions should be resolved when required by implementation or business feedback.
