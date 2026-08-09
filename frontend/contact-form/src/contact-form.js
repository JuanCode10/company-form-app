export function processName(customerName) {
    return customerName.trim();
}

export function processEmail(customerEmail) {
    const email = customerEmail.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (emailRegex.test(email)) {
        return email;
    }

    throw new Error("Invalid email provided");
    return null;
}

export function processPhone(customerPhone) {
    const phone = customerPhone.replaceAll(" ", "");
    const phoneRegex = /^\d{8}$/;

    if (phoneRegex.test(phone)) {
        return `+506 ${phone.slice(0, 4)}-${phone.slice(4)}`;
    }

    throw new Error("Invalid phone detected.");
    return null;
}

export function getSelectedProducts(formElement) {
    return Array.from(
        formElement.querySelectorAll('input[name="products"]:checked'),
    ).map((input) => input.value);
}

export function processBudget(customerBudget) {
    const budget = Number(customerBudget);
    if (budget > 0) {
        return budget;
    }

    throw new Error("Invalid budget detected.");
    return null;
}

export function buildPayload(formElement) {
    const payload = {
        customer: {
            name: processName(formElement.customerName.value),
            email: processEmail(formElement.customerEmail.value),
            phone_number: processPhone(formElement.customerPhone.value),
        },
        store: formElement.store.value,
        products: getSelectedProducts(formElement),
        budget: processBudget(formElement.budget.value),
        purchase_time_horizon: formElement.purchaseTimeHorizon.value,
        customer_comments: formElement.customerComments.value,
    };

    console.log(payload);
    return payload;
}

export function sendPayload(payload) {
    // todo: implement when API is ready
}

export function submissionHandler(event) {
    event.preventDefault();
    const payload = buildPayload(event.currentTarget);
    sendPayload(payload);
    return payload;
}
