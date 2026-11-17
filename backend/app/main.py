
# ==========================================================
# CLOUDFOOD API - VERSION 1.3
# Restaurant + Menu + SQLite Order Management
# ==========================================================

import os
import sqlite3
import logging
import jwt

from pathlib import Path
from datetime import datetime, timezone, timedelta
from pwdlib import PasswordHash

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
# ==========================================================
# 1. CONFIGURATION
# ==========================================================

logging.basicConfig(level=logging.INFO)
# ==========================================================
# AUTHENTICATION CONFIGURATION
# ==========================================================

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is required")

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

password_hash = PasswordHash.recommended()
logger = logging.getLogger("cloudfood")

DB_PATH = os.getenv(
    "CLOUDFOOD_DB_PATH",
    str(Path(__file__).parent / "cloudfood.db")
)


# ==========================================================
# 2. FASTAPI APPLICATION
# ==========================================================

app = FastAPI(
    title="CloudFood API",
    description="Food Delivery and Order Management API",
    version="1.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================================
# 3. RESTAURANT DATA
# ==========================================================

RESTAURANTS = [
    {
        "id": 1,
        "name": "CloudFood Kitchen",
        "cuisine": "Indian"
    },
    {
        "id": 2,
        "name": "Spice Garden",
        "cuisine": "South Indian"
    }
]


# ==========================================================
# 4. FOOD MENU
# ==========================================================

MENUS = {

    1: [
        {
            "id": 101,
            "name": "Chicken Biryani",
            "description": "Traditional chicken dum biryani",
            "price": 220,
            "category": "Biryani",
            "image": "https://images.unsplash.com/photo-1563379091339-03246963d96c?w=800",
            "is_available": True
        },
        {
            "id": 102,
            "name": "Chicken 65",
            "description": "Crispy spicy chicken starter",
            "price": 180,
            "category": "Starters",
            "image": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=800",
            "is_available": True
        },
        {
            "id": 103,
            "name": "Paneer Butter Masala",
            "description": "Paneer in creamy tomato gravy",
            "price": 190,
            "category": "Main Course",
            "image": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=800",
            "is_available": True
        },
        {
            "id": 104,
            "name": "Veg Biryani",
            "description": "Vegetable biryani with Indian spices",
            "price": 170,
            "category": "Biryani",
            "image": "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=800",
            "is_available": True
        }
    ],

    2: [
        {
            "id": 201,
            "name": "Masala Dosa",
            "description": "Crispy dosa with potato masala",
            "price": 1000,
            "category": "Dosa",
            "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800",
            "is_available": True
        },
        {
            "id": 202,
            "name": "Idli Sambar",
            "description": "Soft steamed idli with sambar",
            "price": 60,
            "category": "Breakfast",
            "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800",
            "is_available": True
        },
        {
            "id": 203,
            "name": "Ghee Roast Dosa",
            "description": "Golden crispy ghee roast dosa",
            "price": 130,
            "category": "Dosa",
            "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800",
            "is_available": True
        },
        {
            "id": 204,
            "name": "South Indian Meals",
            "description": "Traditional South Indian meals",
            "price": 160,
            "category": "Meals",
            "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800",
            "is_available": True
        }
    ]
}


# ==========================================================
# 5. DATABASE INITIALIZATION
# ==========================================================
# ==========================================================
# AUTHENTICATION HELPERS
# ==========================================================

def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(user_data: dict) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_data["id"]),
        "email": user_data["email"],
        "role": user_data["role"],
        "restaurant_id": user_data["restaurant_id"],
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token"
        )

    with get_db() as connection:
        user = connection.execute(
            """
            SELECT id, restaurant_id, full_name, email, role, is_active
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

    if user is None or user["is_active"] != 1:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive"
        )

    return dict(user)
def get_db():

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with get_db() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id INTEGER NOT NULL,
                restaurant_name TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                delivery_address TEXT NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'PLACED',
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                food_id INTEGER NOT NULL,
                food_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id)
            )
        """)
        # Restaurants table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cuisine TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Users table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id INTEGER,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK (role IN ('SUPER_ADMIN', 'RESTAURANT_OWNER')),
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (restaurant_id)
                    REFERENCES restaurants(id)
            )
        """)

        # Insert existing restaurants without creating duplicates
        for restaurant in RESTAURANTS:
            connection.execute("""
                INSERT OR IGNORE INTO restaurants
                    (id, name, cuisine, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                restaurant["id"],
                restaurant["name"],
                restaurant["cuisine"],
                datetime.now(timezone.utc).isoformat()
            ))
        connection.commit()

    logger.info("CloudFood database initialized: %s", DB_PATH)


# ==========================================================
# 6. REQUEST MODELS
# ==========================================================

class OrderItem(BaseModel):

    food_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=50)


class CreateOrder(BaseModel):

    restaurant_id: int = Field(gt=0)

    customer_name: str = Field(
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        min_length=7,
        max_length=20
    )

    delivery_address: str = Field(
        min_length=5,
        max_length=500
    )

    items: list[OrderItem] = Field(
        min_length=1,
        max_length=50
    )
class RegisterRestaurantOwner(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    restaurant_name: str = Field(min_length=2, max_length=150)
    cuisine: str = Field(min_length=2, max_length=100)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=128)

# ==========================================================
# 7. ROOT API
# ==========================================================

@app.get("/")
async def root():

    return {
        "application": "CloudFood",
        "version": "1.3.0",
        "status": "running",
        "docs": "/docs"
    }


# ==========================================================
# 8. HEALTH CHECK
# ==========================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "application": "CloudFood",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ==========================================================
# AUTHENTICATION - REGISTER RESTAURANT OWNER
# ==========================================================

@app.post("/auth/register", status_code=201)
async def register_restaurant_owner(
    data: RegisterRestaurantOwner
):
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        with get_db() as connection:

            # Create restaurant
            cursor = connection.execute(
                """
                INSERT INTO restaurants (
                    name,
                    cuisine,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    data.restaurant_name.strip(),
                    data.cuisine.strip(),
                    created_at
                )
            )

            restaurant_id = cursor.lastrowid

            # Create restaurant owner
            cursor = connection.execute(
                """
                INSERT INTO users (
                    restaurant_id,
                    full_name,
                    email,
                    password_hash,
                    role,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    restaurant_id,
                    data.full_name.strip(),
                    data.email.strip().lower(),
                    hash_password(data.password),
                    "RESTAURANT_OWNER",
                    created_at
                )
            )

            user_id = cursor.lastrowid

            connection.commit()

        return {
            "success": True,
            "message": "Restaurant owner registered successfully",
            "user_id": user_id,
            "restaurant_id": restaurant_id
        }

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Email address is already registered"
        )
    # ==========================================================
# AUTHENTICATION - LOGIN
# ==========================================================

@app.post("/auth/login")
async def login(data: LoginRequest):

    with get_db() as connection:
        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (data.email.strip().lower(),)
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if user["is_active"] != 1:
        raise HTTPException(
            status_code=403,
            detail="Your account is inactive"
        )

    if not verify_password(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    user_data = dict(user)

    access_token = create_access_token(user_data)

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"],
            "restaurant_id": user["restaurant_id"]
        }
    }
# ==========================================================
# AUTHENTICATION - CURRENT USER PROFILE
# ==========================================================

@app.get("/auth/me")
async def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    return {
        "success": True,
        "user": {
            "id": current_user["id"],
            "full_name": current_user["full_name"],
            "email": current_user["email"],
            "role": current_user["role"],
            "restaurant_id": current_user["restaurant_id"],
            "is_active": current_user["is_active"]
        }
    }
# ==========================================================
# 9. GET ALL RESTAURANTS
# ==========================================================

@app.get("/restaurants")
async def get_restaurants():

    return {
        "restaurants": RESTAURANTS,
        "total": len(RESTAURANTS)
    }


# ==========================================================
# 10. GET RESTAURANT BY ID
# ==========================================================

@app.get("/restaurants/{restaurant_id}")
async def get_restaurant(restaurant_id: int):

    restaurant = next(
        (r for r in RESTAURANTS if r["id"] == restaurant_id),
        None
    )

    if restaurant is None:
        raise HTTPException(404, "Restaurant not found")

    return {"restaurant": restaurant}


# ==========================================================
# 11. GET RESTAURANT MENU
# ==========================================================

@app.get("/restaurants/{restaurant_id}/menu")
async def get_menu(restaurant_id: int):

    restaurant = next(
        (r for r in RESTAURANTS if r["id"] == restaurant_id),
        None
    )

    if restaurant is None:
        raise HTTPException(404, "Restaurant not found")

    menu = MENUS.get(restaurant_id, [])

    return {
        "restaurant": restaurant,
        "menu": menu,
        "total_items": len(menu)
    }


# ==========================================================
# 12. CREATE ORDER
# ==========================================================

@app.post("/orders", status_code=201)
async def create_order(order: CreateOrder):

    logger.info("Creating order for %s", order.customer_name)

    # Validate restaurant

    restaurant = next(
        (
            r for r in RESTAURANTS
            if r["id"] == order.restaurant_id
        ),
        None
    )

    if restaurant is None:
        raise HTTPException(404, "Restaurant not found")

    # Validate food and calculate price on backend.
    # Never trust prices submitted by the browser.

    menu = MENUS.get(order.restaurant_id, [])

    menu_lookup = {
        food["id"]: food for food in menu
    }

    validated_items = []
    total_amount = 0

    for requested_item in order.items:

        food = menu_lookup.get(requested_item.food_id)

        if food is None:
            raise HTTPException(
                400,
                f"Food ID {requested_item.food_id} does not belong to this restaurant"
            )

        if not food["is_available"]:
            raise HTTPException(
                400,
                f"{food['name']} is currently unavailable"
            )

        subtotal = food["price"] * requested_item.quantity

        total_amount += subtotal

        validated_items.append({
            "food_id": food["id"],
            "food_name": food["name"],
            "price": food["price"],
            "quantity": requested_item.quantity,
            "subtotal": subtotal
        })

    created_at = datetime.now(timezone.utc).isoformat()

    # Save order and order items in one transaction.

    try:

        with get_db() as connection:

            cursor = connection.execute(
                """
                INSERT INTO orders (
                    restaurant_id,
                    restaurant_name,
                    customer_name,
                    phone,
                    delivery_address,
                    total_amount,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    restaurant["id"],
                    restaurant["name"],
                    order.customer_name.strip(),
                    order.phone.strip(),
                    order.delivery_address.strip(),
                    total_amount,
                    "PLACED",
                    created_at
                )
            )

            order_id = cursor.lastrowid

            for item in validated_items:

                connection.execute(
                    """
                    INSERT INTO order_items (
                        order_id,
                        food_id,
                        food_name,
                        price,
                        quantity,
                        subtotal
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        item["food_id"],
                        item["food_name"],
                        item["price"],
                        item["quantity"],
                        item["subtotal"]
                    )
                )

       

        connection.commit()

        logger.info("Order created successfully: %s", order_id)

        return {
            "success": True,
            "message": "Order placed successfully",
            "order_id": order_id,
            "restaurant": restaurant["name"],
            "customer_name": order.customer_name,
            "items": validated_items,
            "total_amount": total_amount,
            "status": "PLACED",
            "created_at": created_at
        }

    except sqlite3.Error:

        logger.exception("Database error while creating order")

        raise HTTPException(
            500,
            "Unable to save order. Please try again."
        )


# ==========================================================
# 13. GET ORDER DETAILS
# ==========================================================

@app.get("/orders/{order_id}")
async def get_order(order_id: int):

    with get_db() as connection:

        order = connection.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,)
        ).fetchone()

        if order is None:
            raise HTTPException(404, "Order not found")

        items = connection.execute(
            """
            SELECT food_id, food_name, price, quantity, subtotal
            FROM order_items
            WHERE order_id = ?
            """,
            (order_id,)
        ).fetchall()

    return {
        "order": dict(order),
        "items": [dict(item) for item in items]
    }


# ==========================================================
# 14. GET ALL ORDERS
# ==========================================================

@app.get("/orders")
async def get_all_orders(
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "RESTAURANT_OWNER":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    with get_db() as connection:

        orders = connection.execute(
            """
            SELECT *
            FROM orders
            WHERE restaurant_id = ?
            ORDER BY id DESC
            LIMIT 100
            """,
            (current_user["restaurant_id"],)
        ).fetchall()

    return {
        "orders": [dict(order) for order in orders],
        "total": len(orders)
    }



# ==========================================================
# 15. UPDATE ORDER STATUS
# ==========================================================


@app.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "RESTAURANT_OWNER":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    allowed_statuses = [
        "PLACED",
        "CONFIRMED",
        "PREPARING",
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "CANCELLED"
    ]

    status = status.upper()

    if status not in allowed_statuses:
        raise HTTPException(400, "Invalid order status")

    with get_db() as connection:

        cursor = connection.execute(
            """
            UPDATE orders
            SET status = ?
            WHERE id = ?
              AND restaurant_id = ?
            """,
            (
                status,
                order_id,
                current_user["restaurant_id"]
            )
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Order not found for this restaurant"
            )

        connection.commit()

    return {
        "success": True,
        "order_id": order_id,
        "status": status
    }


# ==========================================================
# 16. STARTUP
# ==========================================================

@app.on_event("startup")
async def startup_event():

    initialize_database()

    logger.info("====================================")
    logger.info("CLOUDFOOD API STARTED")
    logger.info("Version: 1.3.0")
    logger.info("Database: SQLite")
    logger.info("====================================")


@app.on_event("shutdown")
async def shutdown_event():

    logger.info("CloudFood API shutting down")

import jwt

from datetime import timedelta
from pwdlib import PasswordHash