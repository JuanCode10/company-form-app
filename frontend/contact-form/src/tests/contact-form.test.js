// Import vitest
import { it, expect, describe, vi } from "vitest";

// Import functions to test
import {
    processName,
    processEmail,
    processPhone,
    getSelectedProducts,
    processBudget,
    buildPayload,
    sendPayload,
    submissionHandler,
} from "../contact-form.js";

function createMockForm(overrides = {}) {
    return {
        customerName: { value: "  Example Customer  " },
        customerEmail: { value: " customer@example.com " },
        customerPhone: { value: "88887777" },
        store: { value: "san-jose" },
        budget: { value: "2500" },
        purchaseTimeHorizon: { value: "1-3 months" },
        customerComments: { value: "Need delivery details." },
        querySelectorAll: () => [{ value: "laptop" }, { value: "monitor" }],
        ...overrides,
    };
}

// --- contact-form.js testing suite ---
describe("contact-form.js full testing suite...", () => {
    describe("processName()", () => {
        it("should return trimmed string", () => {
            const input = " Example Customer ";
            const expectedResult = "Example Customer";
            const result = processName(input);
            expect(result).toBe(expectedResult);
        });

        it("should throw error when input is not a string", () => {
            const input = 1;
            const resultFn = () => {
                processName(input);
            };
            expect(resultFn).toThrow(/Invalid input/);
        });

        it("should throw error when input is an empty string after trim", () => {
            const input = "   ";
            const resultFn = () => {
                processName(input);
            };
            expect(resultFn).toThrow(/Invalid name/);
        });
    });
    describe("processEmail()", () => {
        it("should return trimmed valid email", () => {
            const input = " customer@example.com ";
            const expectedResult = "customer@example.com";
            const result = processEmail(input);
            expect(result).toBe(expectedResult);
        });

        it("should throw error when input is not a string", () => {
            const resultFn = () => {
                processEmail(null);
            };
            expect(resultFn).toThrow(/Invalid input/);
        });

        it("should throw error when email is invalid", () => {
            const input = "customer-example.com";
            const resultFn = () => {
                processEmail(input);
            };
            expect(resultFn).toThrow(/Invalid email/);
        });
    });
    describe("processPhone()", () => {
        it("should return formatted phone for valid Costa Rica number", () => {
            const input = "88887777";
            const expectedResult = "+506 8888-7777";
            const result = processPhone(input);
            expect(result).toBe(expectedResult);
        });

        it("should normalize separators and format valid number", () => {
            const input = "8888-7777";
            const expectedResult = "+506 8888-7777";
            const result = processPhone(input);
            expect(result).toBe(expectedResult);
        });

        it("should throw error when input is not a string", () => {
            const resultFn = () => {
                processPhone(88887777);
            };
            expect(resultFn).toThrow(/Invalid input/);
        });

        it("should throw error when number is invalid", () => {
            const resultFn = () => {
                processPhone("123");
            };
            expect(resultFn).toThrow(/Invalid phone/);
        });
    });
    describe("getSelectedProducts()", () => {
        it("should return selected product values", () => {
            const formElement = {
                querySelectorAll: () => [
                    { value: "laptop" },
                    { value: "keyboard" },
                ],
            };
            const expectedResult = ["laptop", "keyboard"];
            const result = getSelectedProducts(formElement);
            expect(result).toEqual(expectedResult);
        });

        it("should return empty array when no products are selected", () => {
            const formElement = {
                querySelectorAll: () => [],
            };
            const result = getSelectedProducts(formElement);
            expect(result).toEqual([]);
        });

        it("should throw error when form element is invalid", () => {
            const resultFn = () => {
                getSelectedProducts(null);
            };
            expect(resultFn).toThrow(/Invalid form element/);
        });
    });
    describe("processBudget()", () => {
        it("should convert valid budget string to number", () => {
            const input = "1200";
            const result = processBudget(input);
            expect(result).toBe(1200);
        });

        it("should throw error for zero or negative budget", () => {
            const resultFn = () => {
                processBudget("0");
            };
            expect(resultFn).toThrow(/Invalid budget/);
        });

        it("should throw error when budget is not numeric", () => {
            const resultFn = () => {
                processBudget("abc");
            };
            expect(resultFn).toThrow(/Invalid budget/);
        });
    });
    describe("buildPayload()", () => {
        it("should build expected payload from form data", () => {
            const formElement = createMockForm();
            const result = buildPayload(formElement);

            expect(result).toEqual({
                customer: {
                    name: "Example Customer",
                    email: "customer@example.com",
                    phone_number: "+506 8888-7777",
                },
                store: "san-jose",
                products: ["laptop", "monitor"],
                budget: 2500,
                purchase_time_horizon: "1-3 months",
                customer_comments: "Need delivery details.",
            });
        });

        it("should throw error when form element is missing", () => {
            const resultFn = () => {
                buildPayload(null);
            };
            expect(resultFn).toThrow(/Invalid form element/);
        });

        it("should throw error when nested data is invalid", () => {
            const formElement = createMockForm({
                customerEmail: { value: "invalid-email" },
            });
            const resultFn = () => {
                buildPayload(formElement);
            };
            expect(resultFn).toThrow(/Invalid email/);
        });
    });
    describe("sendPayload()", () => {
        it("should return the payload for valid input", () => {
            const payload = { ok: true };
            const result = sendPayload(payload);
            expect(result).toEqual(payload);
        });

        it("should throw error when payload is invalid", () => {
            const resultFn = () => {
                sendPayload(null);
            };
            expect(resultFn).toThrow(/Invalid payload/);
        });
    });
    describe("submissionHandler()", () => {
        it("should prevent default and return payload", () => {
            const formElement = createMockForm();
            const preventDefault = vi.fn();
            const event = {
                preventDefault,
                currentTarget: formElement,
            };

            const result = submissionHandler(event);

            expect(preventDefault).toHaveBeenCalledTimes(1);
            expect(result).toEqual({
                customer: {
                    name: "Example Customer",
                    email: "customer@example.com",
                    phone_number: "+506 8888-7777",
                },
                store: "san-jose",
                products: ["laptop", "monitor"],
                budget: 2500,
                purchase_time_horizon: "1-3 months",
                customer_comments: "Need delivery details.",
            });
        });

        it("should throw error for invalid submit event", () => {
            const resultFn = () => {
                submissionHandler(null);
            };
            expect(resultFn).toThrow(/Invalid submit event/);
        });

        it("should throw error when currentTarget is missing", () => {
            const event = {
                preventDefault: () => {},
            };
            const resultFn = () => {
                submissionHandler(event);
            };
            expect(resultFn).toThrow(/Missing event target/);
        });
    });
});
