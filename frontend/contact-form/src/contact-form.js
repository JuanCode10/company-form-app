export function processName(customerName) {
    if (typeof customerName !== "string") {
        throw new Error("Invalid input - must be of type 'string'.");
    }

    const name = customerName.trim();
    if (!name) {
        throw new Error("Invalid name provided");
    }

    return name;
}

export function processEmail(customerEmail) {
    if (typeof customerEmail !== "string") {
        throw new Error("Invalid input - must be of type 'string'.");
    }

    const email = customerEmail.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (emailRegex.test(email)) {
        return email;
    }

    throw new Error("Invalid email provided");
}

export function processPhone(customerPhone) {
    if (typeof customerPhone !== "string") {
        throw new Error("Invalid input - must be of type 'string'.");
    }

    const phone = customerPhone.replace(/\D/g, "");
    const phoneRegex = /^\d{8}$/;

    if (phoneRegex.test(phone)) {
        return `+506 ${phone.slice(0, 4)}-${phone.slice(4)}`;
    }

    throw new Error("Invalid phone detected.");
}

export function getSelectedProducts(formElement) {
    if (!formElement || typeof formElement.querySelectorAll !== "function") {
        throw new Error("Invalid form element provided");
    }

    return Array.from(
        formElement.querySelectorAll('input[name="products"]:checked'),
    ).map((input) => input.value);
}

export function processBudget(customerBudget) {
    const budget = Number(customerBudget);

    if (Number.isFinite(budget) && budget > 0) {
        return budget;
    }

    throw new Error("Invalid budget detected.");
}

export function buildPayload(formElement) {
    if (!formElement) {
        throw new Error("Invalid form element provided");
    }

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

    return payload;
}

export async function sendPayload(payload) {
    if (!payload || typeof payload !== "object") {
        throw new Error("Invalid payload provided");
    }

    const response = await fetch("http://127.0.0.1:5001/leads", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message ?? `Request failed with status ${response.status}`,
        );
    }

    return data;
}

export async function submissionHandler(event) {
    if (!event || typeof event.preventDefault !== "function") {
        throw new Error("Invalid submit event provided");
    }

    event.preventDefault();

    if (!event.currentTarget) {
        throw new Error("Missing event target");
    }

    const payload = buildPayload(event.currentTarget);
    const result = await sendPayload(payload);

    console.log(result);

    return payload;
}
