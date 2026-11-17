
const API_URL = "http://localhost:8000";

async function loadOrders() {
    const tableBody = document.getElementById("orders-table-body");
    const message = document.getElementById("admin-message");

    message.textContent = "Loading orders...";
    tableBody.replaceChildren();

    try {
        const response = await fetch(`${API_URL}/orders`);

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        // Backend returns { orders: [...], total: number }
        const orders = Array.isArray(data) ? data : (data.orders || []);

        document.getElementById("total-orders").textContent =
            data.total ?? orders.length;

        document.getElementById("pending-orders").textContent =
            orders.filter(o =>
                ["PENDING", "PLACED"].includes(
                    String(o.status).toUpperCase()
                )
            ).length;

        document.getElementById("preparing-orders").textContent =
            orders.filter(o =>
                String(o.status).toUpperCase() === "PREPARING"
            ).length;

        document.getElementById("delivered-orders").textContent =
            orders.filter(o =>
                String(o.status).toUpperCase() === "DELIVERED"
            ).length;

        if (orders.length === 0) {
            message.textContent = "No customer orders found yet.";
            return;
        }

        message.textContent = `Showing ${orders.length} order(s).`;

        orders.forEach(order => {
            const row = document.createElement("tr");

            const values = [
                `#${order.id}`,
                order.customer_name || "Customer",
                order.restaurant_name || `Restaurant ${order.restaurant_id}`,
                `₹${Number(order.total_amount).toFixed(2)}`,
                order.status || "PLACED"
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            const actionCell = document.createElement("td");
            const select = document.createElement("select");

            const statuses = [
                "PLACED",
                "CONFIRMED",
                "PREPARING",
                "OUT_FOR_DELIVERY",
                "DELIVERED",
                "CANCELLED"
            ];

            statuses.forEach(status => {
                const option = document.createElement("option");
                option.value = status;
                option.textContent = status.replaceAll("_", " ");

                if (
                    status === String(order.status || "PLACED").toUpperCase()
                ) {
                    option.selected = true;
                }

                select.appendChild(option);
            });

            select.addEventListener("change", () => {
                updateOrderStatus(order.id, select.value, select);
            });

            actionCell.appendChild(select);
            row.appendChild(actionCell);

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error("Admin dashboard error:", error);
        message.textContent =
            "Could not load orders. Check the browser console for details.";
    }
}

async function updateOrderStatus(orderId, status, selectElement) {
    selectElement.disabled = true;

    try {
        const response = await fetch(
            `${API_URL}/orders/${orderId}/status?status=${encodeURIComponent(status)}`,
            { method: "PATCH" }
        );

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || "Status update failed.");
        }

        document.getElementById("admin-message").textContent =
            `Order #${orderId} updated to ${status.replaceAll("_", " ")}.`;

        await loadOrders();

    } catch (error) {
        console.error("Status update error:", error);

        document.getElementById("admin-message").textContent =
            `Could not update order #${orderId}: ${error.message}`;

        await loadOrders();

    } finally {
        selectElement.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", loadOrders);
