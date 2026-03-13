from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# -------------------------------
# Mock Database
# -------------------------------

product_db = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": False},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

feedback_storage = []
order_records = []

# -------------------------------
# Root Endpoint
# -------------------------------

@app.get("/")
def index():
    return {"message": "FastAPI Project Running Successfully"}

# -------------------------------
# PRODUCT ENDPOINTS
# -------------------------------

@app.get("/products")
def list_products():
    return {
        "items": product_db,
        "count": len(product_db)
    }


@app.get("/products/category/{cat}")
def products_by_category(cat: str):

    filtered = [p for p in product_db if p["category"].lower() == cat.lower()]

    if not filtered:
        return {"error": "No items found for this category"}

    return {
        "category": cat,
        "items": filtered,
        "count": len(filtered)
    }


@app.get("/products/available")
def available_products():

    stock_items = [p for p in product_db if p["in_stock"]]

    return {
        "available_products": stock_items,
        "total": len(stock_items)
    }


@app.get("/store/info")
def store_info():

    in_stock = len([p for p in product_db if p["in_stock"]])
    out_stock = len(product_db) - in_stock
    unique_categories = list(set(p["category"] for p in product_db))

    return {
        "store": "My Online Store",
        "product_total": len(product_db),
        "available": in_stock,
        "out_of_stock": out_stock,
        "categories": unique_categories
    }


@app.get("/products/search/{term}")
def search_items(term: str):

    matches = [p for p in product_db if term.lower() in p["name"].lower()]

    if not matches:
        return {"message": "No matching products found"}

    return {
        "search_term": term,
        "results": matches,
        "matches": len(matches)
    }


@app.get("/products/highlights")
def product_highlights():

    lowest = min(product_db, key=lambda x: x["price"])
    highest = max(product_db, key=lambda x: x["price"])

    return {
        "cheapest_product": lowest,
        "most_expensive_product": highest
    }

# -------------------------------
# FILTER PRODUCTS (QUERY PARAMS)
# -------------------------------

@app.get("/products/filter")
def filter_items(
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None
):

    results = product_db

    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]

    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]

    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]

    return {
        "applied_filters": {
            "category": category,
            "min_price": min_price,
            "max_price": max_price
        },
        "results": results,
        "count": len(results)
    }


@app.get("/products/{product_id}/price")
def product_price(product_id: int):

    for item in product_db:
        if item["id"] == product_id:
            return {
                "product": item["name"],
                "price": item["price"]
            }

    return {"error": "Product not found"}

# -------------------------------
# FEEDBACK SYSTEM
# -------------------------------

class Feedback(BaseModel):

    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


@app.post("/feedback")
def add_feedback(data: Feedback):

    feedback_storage.append(data.dict())

    return {
        "message": "Feedback received",
        "feedback": data,
        "total_feedback": len(feedback_storage)
    }

# -------------------------------
# PRODUCT DASHBOARD SUMMARY
# -------------------------------

@app.get("/products/summary")
def dashboard_summary():

    total = len(product_db)

    in_stock = len([p for p in product_db if p["in_stock"]])
    out_stock = total - in_stock

    expensive = max(product_db, key=lambda x: x["price"])
    cheap = min(product_db, key=lambda x: x["price"])

    categories = list(set(p["category"] for p in product_db))

    return {
        "total_products": total,
        "in_stock": in_stock,
        "out_of_stock": out_stock,
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest": {"name": cheap["name"], "price": cheap["price"]},
        "categories": categories
    }

# -------------------------------
# BULK ORDER SYSTEM
# -------------------------------

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class CompanyOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]


@app.post("/orders/bulk")
def bulk_order(order: CompanyOrder):

    confirmed_items = []
    rejected_items = []
    total_price = 0

    for item in order.items:

        product = next((p for p in product_db if p["id"] == item.product_id), None)

        if not product:
            rejected_items.append({
                "product_id": item.product_id,
                "reason": "Product does not exist"
            })
            continue

        if not product["in_stock"]:
            rejected_items.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is currently unavailable"
            })
            continue

        subtotal = product["price"] * item.quantity
        total_price += subtotal

        confirmed_items.append({
            "product": product["name"],
            "quantity": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed_orders": confirmed_items,
        "failed_orders": rejected_items,
        "grand_total": total_price
    }

# -------------------------------
# SIMPLE ORDER TRACKER
# -------------------------------

class BasicOrder(BaseModel):
    product_id: int
    quantity: int


@app.post("/orders")
def create_new_order(order: BasicOrder):

    order_id = len(order_records) + 1

    new_entry = {
        "id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }

    order_records.append(new_entry)

    return new_entry


@app.get("/orders/{order_id}")
def get_order_details(order_id: int):

    for order in order_records:
        if order["id"] == order_id:
            return order

    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in order_records:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}