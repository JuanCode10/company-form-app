// Import vitest
import { it, expect, describe, vi, beforeEach, afterEach } from "vitest";

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
    beforeEach(() => {
        vi.stubGlobal("fetch", vi.fn());
    });

    afterEach(() => {
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
    });

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
        it("should send the payload and return the API response", async () => {
            const payload = { ok: true };
            const responseBody = { message: "Payload received" };
            fetch.mockResolvedValue({
                ok: true,
                json: vi.fn().mockResolvedValue(responseBody),
            });

            const result = await sendPayload(payload);

            expect(fetch).toHaveBeenCalledWith("http://127.0.0.1:5001/leads", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            expect(result).toEqual(responseBody);
        });

        it("should reject when payload is invalid", async () => {
            await expect(sendPayload(null)).rejects.toThrow(/Invalid payload/);
            expect(fetch).not.toHaveBeenCalled();
        });

        it("should reject with the API error message for failed responses", async () => {
            fetch.mockResolvedValue({
                ok: false,
                status: 422,
                json: vi
                    .fn()
                    .mockResolvedValue({ message: "Invalid form data" }),
            });

            await expect(sendPayload({ ok: true })).rejects.toThrow(
                "Invalid form data",
            );
        });
    });
    describe("submissionHandler()", () => {
        it("should prevent default, submit, and return payload", async () => {
            const formElement = createMockForm();
            const preventDefault = vi.fn();
            fetch.mockResolvedValue({
                ok: true,
                json: vi
                    .fn()
                    .mockResolvedValue({ message: "Payload received" }),
            });
            const event = {
                preventDefault,
                currentTarget: formElement,
            };

            const result = await submissionHandler(event);

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

        it("should reject for invalid submit event", async () => {
            await expect(submissionHandler(null)).rejects.toThrow(
                /Invalid submit event/,
            );
        });

        it("should reject when currentTarget is missing", async () => {
            const event = {
                preventDefault: () => {},
            };
            await expect(submissionHandler(event)).rejects.toThrow(
                /Missing event target/,
            );
        });
    });
});
