
const API_URL = "http://localhost:8000";

const registerForm = document.getElementById("register-form");
const registerMessage = document.getElementById("register-message");

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(registerForm);

    const registrationData = {
        full_name: formData.get("full_name").trim(),
        email: formData.get("email").trim(),
        password: formData.get("password"),
        restaurant_name: formData.get("restaurant_name").trim(),
        cuisine: formData.get("cuisine").trim()
    };

    registerMessage.textContent = "Registering your restaurant...";

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(registrationData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Registration failed");
        }

        registerMessage.textContent =
            "Registration successful! Redirecting to login...";

        registerMessage.style.color = "green";

        registerForm.reset();

        setTimeout(() => {
            window.location.href = "./login.html";
        }, 1500);

    } catch (error) {
        registerMessage.textContent = error.message;
        registerMessage.style.color = "red";
    }
});
