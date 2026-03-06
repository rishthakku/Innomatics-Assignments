from fastapi import FastAPI

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": False},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": True},

    {"id": 5, "name": "Laptop Stand", "price": 899, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1299, "category": "Electronics", "in_stock": False}
]


# Q1
@app.get("/products")
def get_products():
    total_products = len(products)
    return {"products": products, "total": total_products}


# Q2
@app.get("/products/category/{category_name}")
def products_by_category(category_name: str):

    result = []

    for p in products:
        if p["category"].lower() == category_name.lower():
            result.append(p)

    if len(result) == 0:
        return {"error": "No products found in this category"}

    return {"products": result}


# Q3
@app.get("/products/instock")
def instock_products():

    instock_list = []
    count = 0

    for p in products:
        if p["in_stock"] == True:
            instock_list.append(p)
            count = count + 1

    return {"in_stock_products": instock_list, "count": count}


# Q4
@app.get("/store/summary")
def store_summary():

    total = len(products)

    instock = 0
    outstock = 0
    categories = []

    for p in products:

        if p["in_stock"] == True:
            instock = instock + 1
        else:
            outstock = outstock + 1

        if p["category"] not in categories:
            categories.append(p["category"])

    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }


# Q5
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matches = []

    for p in products:
        name = p["name"].lower()
        key = keyword.lower()

        if key in name:
            matches.append(p)

    if len(matches) == 0:
        return {"message": "No products matched your search"}

    return {"matched_products": matches, "count": len(matches)}


# BONUS
@app.get("/products/deals")
def product_deals():

    cheapest = products[0]
    expensive = products[0]

    for p in products:

        if p["price"] < cheapest["price"]:
            cheapest = p

        if p["price"] > expensive["price"]:
            expensive = p

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }
