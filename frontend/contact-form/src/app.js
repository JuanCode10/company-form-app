import { submissionHandler } from "./contact-form.js";

// --- Event listener ---

const form = document.querySelector("form");
if (!form) {
    throw new Error("Form not found!");
}
form.addEventListener("submit", submissionHandler);
