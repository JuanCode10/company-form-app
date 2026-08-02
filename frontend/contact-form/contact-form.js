"use strict";
// Things to do:
// 1. listen for submit event
// 2. Extract values from form
// 3. Build json payload
// any need for objects? not for now, add later if needed

// --- Functions ---

function submissionHandler(event) {
    event.preventDefault();
    console.log("FORM SUBMISSION DETECTED");
    return {};
}

// --- Event Listener ---

const form = document.querySelector("form");
if (!form) {
    throw new Error("Form not found!");
}

document.querySelector("form").addEventListener("submit", submissionHandler);
