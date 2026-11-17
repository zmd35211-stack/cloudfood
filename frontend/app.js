
/* =====================================================
   CLOUDFOOD - COMPLETE FRONTEND APPLICATION
   Restaurant Menu + Food Images + Shopping Cart
===================================================== */

// 1. BACKEND API CONFIGURATION
const API_URL = "http://localhost:8000";

// 2. APPLICATION STATE
let restaurants = [];
let selectedRestaurant = null;
let cart = [];

// =====================================================
// 3. LOAD RESTAURANTS
// =====================================================

async function displayRestaurants() {

    const container = document.getElementById("restaurant-list");

    if (!container) {
        console.error("Restaurant container not found");
        return;
    }

    container.textContent = "Loading restaurants...";

    console.log("Loading restaurants...");
    console.log("API Request:", `${API_URL}/restaurants`);

    try {

        const response = await fetch(`${API_URL}/restaurants`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        restaurants = data.restaurants || [];

        container.innerHTML = "";

        if (restaurants.length === 0) {
            container.textContent = "No restaurants available.";
            return;
        }

        restaurants.forEach(restaurant => {

            const card = document.createElement("div");
            card.className = "card restaurant-card";

            const content = document.createElement("div");
            content.className = "card-content";

            const heading = document.createElement("h3");
            heading.textContent = restaurant.name;

            const cuisine = document.createElement("p");
            cuisine.textContent = restaurant.cuisine;

            const id = document.createElement("p");
            id.textContent = `Restaurant ID: ${restaurant.id}`;

            const button = document.createElement("button");
            button.className = "add-button";
            button.textContent = "View Menu";

            button.addEventListener("click", () => {
                loadRestaurantMenu(restaurant.id);
            });

            content.append(heading, cuisine, id, button);
            card.appendChild(content);
            container.appendChild(card);

        });

        console.log("SUCCESS: Restaurants loaded!", restaurants);

    } catch (error) {

        console.error("Restaurant API error:", error);

        container.textContent =
            "Unable to load restaurants. Please check the backend.";

    }
}

// =====================================================
// 4. LOAD SELECTED RESTAURANT MENU
// =====================================================

async function loadRestaurantMenu(restaurantId) {

    const container = document.getElementById("food-list");

    if (!container) {
        console.error("Food container not found");
        return;
    }

    console.log("Loading menu for restaurant:", restaurantId);

    container.textContent = "Loading food menu...";

    try {

        const response = await fetch(
            `${API_URL}/restaurants/${restaurantId}/menu`
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        selectedRestaurant = data.restaurant;

        const menu = data.menu || [];

        const heading = document.querySelector("#menu h2");

        if (heading) {
            heading.textContent =
                `Menu - ${selectedRestaurant.name}`;
        }

        container.innerHTML = "";

        if (menu.length === 0) {
            container.textContent =
                "No food items available in this restaurant.";
            return;
        }

        menu.forEach(food => {

            if (!food.is_available) return;

            // Food card
            const card = document.createElement("div");
            card.className = "card food-card";

            // Food image
            const image = document.createElement("img");

            image.src = food.image || "";
            image.alt = food.name;
            image.loading = "lazy";

            image.onerror = () => {

                const fallback = document.createElement("div");

                fallback.className = "food-image-placeholder";
                fallback.textContent = "Image unavailable";

                image.replaceWith(fallback);

            };

            // Food details
            const content = document.createElement("div");
            content.className = "card-content";

            const category = document.createElement("p");
            category.className = "food-category";
            category.textContent = food.category;

            const name = document.createElement("h3");
            name.textContent = food.name;

            const description = document.createElement("p");
            description.textContent = food.description;

            const price = document.createElement("h3");
            price.className = "food-price";
            price.textContent = `₹${food.price}`;

            // Add to cart button
            const button = document.createElement("button");

            button.className = "add-button";
            button.textContent = "Add to Cart";

            button.addEventListener("click", () => {
                addToCart(food, selectedRestaurant);
            });

            content.append(
                category,
                name,
                description,
                price,
                button
            );

            card.append(image, content);

            container.appendChild(card);

        });

        console.log(
            "SUCCESS: Restaurant menu loaded!",
            selectedRestaurant,
            menu
        );

        container.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {

        console.error("Menu API error:", error);

        container.textContent =
            "Unable to load food menu. Please try again.";

    }
}

// =====================================================
// 5. ADD FOOD TO CART
// =====================================================

function addToCart(food, restaurant) {

    if (!food || !restaurant) {
        console.error("Food or restaurant information missing");
        return;
    }

    // Prevent mixing items from different restaurants
    if (
        cart.length > 0 &&
        cart[0].restaurantId !== restaurant.id
    ) {

        const confirmed = confirm(
            `Your cart contains items from ${cart[0].restaurantName}.\n\n` +
            `Clear the cart and order from ${restaurant.name}?`
        );

        if (!confirmed) return;

        cart = [];

    }

    const existing = cart.find(
        item =>
            item.id === food.id &&
            item.restaurantId === restaurant.id
    );

    if (existing) {

        existing.quantity++;

    } else {

        cart.push({
            ...food,
            restaurantId: restaurant.id,
            restaurantName: restaurant.name,
            quantity: 1
        });

    }

    updateCart();

    console.log("Cart updated:", cart);

}

// =====================================================
// 6. UPDATE CART
// =====================================================

function updateCart() {

    const container = document.getElementById("cart-items");

    const countElement = document.getElementById("cart-count");

    const totalElement = document.getElementById("cart-total");

    const count = cart.reduce(
        (sum, item) => sum + item.quantity,
        0
    );

    const total = cart.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
    );

    if (countElement) {
        countElement.textContent = count;
    }

    if (totalElement) {
        totalElement.textContent = total;
    }

    if (!container) return;

    container.innerHTML = "";

    if (cart.length === 0) {

        container.textContent = "Your cart is empty.";

        return;

    }

    const restaurantHeading = document.createElement("p");

    restaurantHeading.textContent =
        `Restaurant: ${cart[0].restaurantName}`;

    container.appendChild(restaurantHeading);

    cart.forEach(item => {

        const row = document.createElement("div");

        row.className = "cart-item";

        const name = document.createElement("span");

        name.textContent =
            `${item.name} × ${item.quantity}`;

        const price = document.createElement("span");

        price.textContent =
            `₹${item.price * item.quantity}`;

        row.append(name, price);

        container.appendChild(row);

    });

}

// =====================================================
// 7. OPEN / CLOSE CART
// =====================================================

function toggleCart() {

    const panel = document.getElementById("cart-panel");

    if (!panel) {
        console.error("Cart panel not found");
        return;
    }

    panel.classList.toggle("hidden");

}

// =====================================================
// 8. CHECKOUT
// =====================================================


// =====================================================
// REAL CUSTOMER CHECKOUT
// =====================================================

async function checkout() {

    if (cart.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    // Collect customer information

    const customerName = prompt("Enter your full name:");

    if (!customerName || customerName.trim().length < 2) {
        alert("Please enter a valid name.");
        return;
    }

    const phone = prompt("Enter your mobile number:");

    if (!phone || phone.trim().length < 7) {
        alert("Please enter a valid phone number.");
        return;
    }

    const address = prompt("Enter your delivery address:");

    if (!address || address.trim().length < 5) {
        alert("Please enter a valid delivery address.");
        return;
    }

    const orderButton = document.querySelector(".checkout-button");

    try {

        if (orderButton) {
            orderButton.disabled = true;
            orderButton.textContent = "Placing Order...";
        }

        // Prepare order payload

        const orderData = {
            restaurant_id: cart[0].restaurantId,
            customer_name: customerName.trim(),
            phone: phone.trim(),
            delivery_address: address.trim(),

            items: cart.map(item => ({
                food_id: item.id,
                quantity: item.quantity
            }))
        };

        console.log("Submitting order:", orderData);

        // Send order to FastAPI

        const response = await fetch(`${API_URL}/orders`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(orderData)

        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "Unable to place order"
            );
        }

        // Display confirmation

        alert(
            "ORDER PLACED SUCCESSFULLY!\n\n" +
            `Order ID: ${result.order_id}\n` +
            `Restaurant: ${result.restaurant}\n` +
            `Customer: ${result.customer_name}\n` +
            `Total: ₹${result.total_amount}\n` +
            `Status: ${result.status}`
        );

        console.log("Order saved successfully:", result);

        // Clear cart

        cart = [];

        updateCart();

        const panel = document.getElementById("cart-panel");

        if (panel) {
            panel.classList.add("hidden");
        }

    } catch (error) {

        console.error("Checkout error:", error);

        alert("Order failed: " + error.message);

    } finally {

        if (orderButton) {
            orderButton.disabled = false;
            orderButton.textContent = "Proceed to Checkout";
        }

    }
}


// =====================================================
// 9. APPLICATION INITIALIZATION
// =====================================================

document.addEventListener("DOMContentLoaded", () => {

    console.log("==================================");
    console.log("CLOUDFOOD APPLICATION STARTED");
    console.log("API:", API_URL);
    console.log("==================================");

    displayRestaurants();

    const foodContainer = document.getElementById("food-list");

    if (foodContainer) {

        foodContainer.textContent =
            "Select a restaurant above to explore its menu.";

    }

    updateCart();

});

/* =====================================================
   CLOUDFOOD - CUSTOMER ORDER TRACKING
===================================================== */

// Find order by ID

async function trackOrder() {
    const orderId = document.getElementById("track-order-id").value;
    const result = document.getElementById("order-tracking-result");

    if (!orderId) {
        result.textContent = "Please enter your order ID.";
        return;
    }
// Automatically refresh order status every 15 seconds
if (window.cloudFoodTrackingInterval) {
    clearInterval(window.cloudFoodTrackingInterval);
}

window.cloudFoodTrackingInterval = setInterval(() => {
    trackOrder();
}, 15000);
    result.textContent = "Loading order details...";

    try {
        const response = await fetch(`${API_URL}/orders/${orderId}`);

        if (!response.ok) {
            throw new Error("Order not found.");
        }

        const order = await response.json();

        const stages = [
            "PLACED",
            "CONFIRMED",
            "PREPARING",
            "OUT_FOR_DELIVERY",
            "DELIVERED"
        ];

        const currentStatus = String(order.status || "PLACED").toUpperCase();
        const currentIndex = stages.indexOf(currentStatus);

        if (currentStatus === "CANCELLED") {
            result.innerHTML = `
                <h3>Order #${order.id} — Cancelled</h3>
                <p>Your order has been cancelled.</p>
            `;
            return;
        }

        const timeline = stages.map((stage, index) => {
            const completed = currentIndex >= index;

            return `
                <div class="timeline-step ${completed ? "completed" : ""}">
                    <div class="timeline-dot">
                        ${completed ? "✓" : index + 1}
                    </div>
                    <div class="timeline-content">
                        <strong>${stage.replaceAll("_", " ")}</strong>
                        <p>${completed ? "Completed" : "Waiting"}</p>
                    </div>
                </div>
            `;
        }).join("");

        result.innerHTML = `
            <div class="tracking-header">
                <h3>Order #${order.id}</h3>
                <span class="tracking-status">
                    ${currentStatus.replaceAll("_", " ")}
                </span>
            </div>

            <p><strong>Restaurant:</strong> ${order.restaurant_name || "CloudFood Restaurant"}</p>
            <p><strong>Customer:</strong> ${order.customer_name || "Customer"}</p>
            <p><strong>Total:</strong> ₹${Number(order.total_amount || 0).toFixed(2)}</p>

            <h3 class="timeline-heading">Your Order Journey</h3>
            <div class="order-timeline">
                ${timeline}
            </div>

            <button class="hero-button" onclick="trackOrder()">
                Refresh Tracking
            </button>
        `;

    } catch (error) {
        console.error("Tracking error:", error);
        result.textContent = error.message || "Unable to track your order.";
    }
}

