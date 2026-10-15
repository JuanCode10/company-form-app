import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("app.js", () => {
    beforeEach(() => {
        vi.resetModules();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it("registers the submission handler on the form", async () => {
        const form = { addEventListener: vi.fn() };
        vi.spyOn(document, "querySelector").mockReturnValue(form);

        await import("../app.js");

        expect(document.querySelector).toHaveBeenCalledWith("form");
        expect(form.addEventListener).toHaveBeenCalledWith(
            "submit",
            expect.any(Function),
        );
    });

    it("throws when the form is missing", async () => {
        vi.spyOn(document, "querySelector").mockReturnValue(null);

        await expect(import("../app.js")).rejects.toThrow("Form not found!");
    });
});
