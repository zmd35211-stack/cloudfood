
const API_URL = "http://localhost:8000";

const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(loginForm);

    const loginData = {
        email: formData.get("email").trim(),
        password: formData.get("password")
    };

    loginMessage.textContent = "Signing in...";

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(loginData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Login failed");
        }

        if (!result.access_token) {
            throw new Error("Authentication token was not returned");
        }

        // Store the login session for subsequent API requests.
        sessionStorage.setItem("cloudfood_token", result.access_token);
        sessionStorage.setItem("cloudfood_user", JSON.stringify(result.user));

        loginMessage.textContent = "Login successful! Opening dashboard...";
        loginMessage.style.color = "green";

        setTimeout(() => {
            window.location.href = "./admin.html";
        }, 800);

    } catch (error) {
        loginMessage.textContent = error.message;
        loginMessage.style.color = "red";
    }
});
