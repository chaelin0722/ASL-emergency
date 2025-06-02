// Import Firebase authentication module
import { auth } from "./firebase-config.js";
import { createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ Register.js Loaded");

    const registerForm = document.getElementById("register-form");

    if (!registerForm) {
        console.error("Register form not found. Check if 'register-form' ID exists in register.html.");
        return;
    }

    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm-password").value;

        if (!email || !password || !confirmPassword) {
            alert("Please fill in all fields.");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        try {
            console.log("🔄 Registering user...");
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            
            console.log("✅ Registration successful!", userCredential);
            alert("Registration successful! Redirecting to home page.");
            window.location.href = "home.html"; // Redirect to home page

        } catch (error) {
            console.error("❌ Registration error:", error);
            alert("Error: " + error.message);
        }
    });
});
