import { defineConfig } from "vitest/config";

export default defineConfig({
    test: {
        coverage: {
            include: ["contact-form/src/**/*.js"],
            exclude: ["contact-form/src/tests/**"],
        },
    },
});
