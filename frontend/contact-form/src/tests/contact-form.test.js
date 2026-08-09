// Import vitest
import { it, expect, describe } from "vitest";

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
    });
    // describe("processEmail()", () => {});
    // describe("processPhone()", () => {});
    // describe("getSelectedProducts()", () => {});
    // describe("processBudget()", () => {});
    // describe("buildPayload()", () => {});
    // describe("sendPayload()", () => {});
    // describe("submissionHandler()", () => {});
});
