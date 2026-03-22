from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="CineStar Booking")

movies = [
    {"id": 1, "title": "Inception", "genre": "Action", "language": "English", "duration_mins": 148, "ticket_price": 150, "seats_available": 100},
    {"id": 2, "title": "The Conjuring", "genre": "Horror", "language": "English", "duration_mins": 112, "ticket_price": 120, "seats_available": 50},
    {"id": 3, "title": "Superbad", "genre": "Comedy", "language": "English", "duration_mins": 113, "ticket_price": 100, "seats_available": 80},
    {"id": 4, "title": "The Dark Knight", "genre": "Action", "language": "English", "duration_mins": 152, "ticket_price": 200, "seats_available": 120},
    {"id": 5, "title": "Parasite", "genre": "Drama", "language": "Korean", "duration_mins": 132, "ticket_price": 140, "seats_available": 60},
    {"id": 6, "title": "Get Out", "genre": "Horror", "language": "English", "duration_mins": 104, "ticket_price": 130, "seats_available": 90}
]

bookings, holds = [], []
booking_counter = hold_counter = 1

class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""

class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)

class HoldRequest(BaseModel):
    customer_name: str
    movie_id: int
    seats: int

def find_movie(movie_id: int):
    return next((m for m in movies if m["id"] == movie_id), None)

def calculate_ticket_cost(base_price: int, seats: int, seat_type: str, promo_code: str = ""):
    cost = int(base_price * 1.5) * seats if seat_type == 'premium' else (base_price * 2) * seats if seat_type == 'recliner' else base_price * seats
    discounted = int(cost * 0.9) if promo_code == 'SAVE10' else int(cost * 0.8) if promo_code == 'SAVE20' else cost
    return cost, discounted

def filter_movies_logic(m, g, l, mp, ms):
    if g and m["genre"].lower() != g.lower(): return False
    if l and m["language"].lower() != l.lower(): return False
    if mp and m["ticket_price"] > mp: return False
    if ms and m["seats_available"] < ms: return False
    return True

@app.get("/")
def home(): return {"message": "Welcome to CineStar Booking"}

@app.get("/movies")
def get_movies():
    return {"movies": movies, "total": len(movies), "total_seats_available": sum(m["seats_available"] for m in movies)}

@app.get("/bookings")
def get_bookings():
    return {"bookings": bookings, "total": len(bookings), "total_revenue": sum(b["discounted_cost"] for b in bookings)}

@app.get("/movies/summary")
def get_movie_summary():
    return {
        "total_movies": len(movies),
        "most_expensive_ticket": max(m["ticket_price"] for m in movies) if movies else 0,
        "cheapest_ticket": min(m["ticket_price"] for m in movies) if movies else 0,
        "total_seats": sum(m["seats_available"] for m in movies),
        "genre_counts": {g: sum(1 for m in movies if m["genre"]==g) for g in {m["genre"] for m in movies}}
    }

@app.get("/movies/filter")
def filter_movies(genre: Optional[str] = None, language: Optional[str] = None, max_price: Optional[int] = None, min_seats: Optional[int] = None):
    return {"filtered_movies": [m for m in movies if filter_movies_logic(m, genre, language, max_price, min_seats)]}

@app.get("/movies/search")
def search_movies(keyword: str):
    kw = keyword.lower()
    matches = [m for m in movies if kw in m["title"].lower() or kw in m["genre"].lower() or kw in m["language"].lower()]
    return {"matches": matches, "total_found": len(matches)} if matches else {"message": "No movies found matching your keyword."}

@app.get("/movies/sort")
def sort_movies(sort_by: str = "ticket_price"):
    if sort_by not in {"ticket_price", "title", "duration_mins", "seats_available"}: raise HTTPException(status_code=400, detail="Invalid param")
    return {"sorted_movies": sorted(movies, key=lambda x: x[sort_by])}

@app.get("/movies/page")
def page_movies(page: int = 1, limit: int = 3):
    return {"total": len(movies), "total_pages": (len(movies) + limit - 1) // limit, "sliced_list": movies[(page - 1) * limit:(page - 1) * limit + limit]}

@app.get("/movies/browse")
def browse_movies(keyword: Optional[str] = None, sort_by: str = "ticket_price", order: str = "asc", page: int = 1, limit: int = 3, genre: Optional[str] = None, language: Optional[str] = None):
    res = movies
    if keyword: res = [m for m in res if keyword.lower() in m["title"].lower() or keyword.lower() in m["genre"].lower() or keyword.lower() in m["language"].lower()]
    res = [m for m in res if filter_movies_logic(m, genre, language, None, None)]
    res = sorted(res, key=lambda x: x.get(sort_by if sort_by in {"ticket_price", "title", "duration_mins", "seats_available"} else "ticket_price", x["ticket_price"]), reverse=(order == "desc"))
    return {"total": len(res), "total_pages": (len(res) + limit - 1) // limit, "sliced_list": res[(page - 1) * limit:(page - 1) * limit + limit]}

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    m = find_movie(movie_id)
    if not m: raise HTTPException(status_code=404, detail="Not found")
    return m

@app.post("/bookings")
def book(req: BookingRequest):
    global booking_counter
    m = find_movie(req.movie_id)
    if not m or m["seats_available"] < req.seats: raise HTTPException(status_code=400, detail="Error")
    og, disc = calculate_ticket_cost(m["ticket_price"], req.seats, req.seat_type, req.promo_code)
    m["seats_available"] -= req.seats
    b = {"booking_id": booking_counter, "movie_title": m["title"], "seats": req.seats, "seat_type": req.seat_type, "original_cost": og, "discounted_cost": disc, "total_cost": disc, "customer_name": req.customer_name}
    bookings.append(b)
    booking_counter += 1
    return b

@app.post("/movies", status_code=status.HTTP_201_CREATED)
def add_movie(m: NewMovie):
    if any(x["title"].lower() == m.title.lower() for x in movies): raise HTTPException(status_code=400, detail="Duplicate title")
    new_m = {**m.model_dump(), "id": max((x["id"] for x in movies), default=0) + 1}
    movies.append(new_m)
    return new_m

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, ticket_price: Optional[int] = None, seats_available: Optional[int] = None):
    m = find_movie(movie_id)
    if not m: raise HTTPException(status_code=404, detail="Not found")
    if ticket_price is not None: m["ticket_price"] = ticket_price
    if seats_available is not None: m["seats_available"] = seats_available
    return m

@app.delete("/movies/{movie_id}")
def drop_movie(movie_id: int):
    m = find_movie(movie_id)
    if not m: raise HTTPException(status_code=404, detail="Not found")
    if any(b["movie_title"] == m["title"] for b in bookings): raise HTTPException(status_code=400, detail="Has bookings")
    movies.remove(m)
    return {"message": "Deleted"}

@app.post("/seat-hold")
def hold_seat(req: HoldRequest):
    global hold_counter
    m = find_movie(req.movie_id)
    if not m or m["seats_available"] < req.seats: raise HTTPException(status_code=400, detail="Error")
    m["seats_available"] -= req.seats
    h = {"hold_id": hold_counter, **req.model_dump()}
    holds.append(h)
    hold_counter += 1
    return h

@app.get("/seat-hold")
def get_holds(): return {"holds": holds}

@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id: int):
    global booking_counter
    h = next((x for x in holds if x["hold_id"] == hold_id), None)
    if not h: raise HTTPException(status_code=404, detail="Not found")
    m = find_movie(h["movie_id"])
    c, d = calculate_ticket_cost(m["ticket_price"], h["seats"], "standard")
    b = {"booking_id": booking_counter, "movie_title": m["title"], "seats": h["seats"], "seat_type": "standard", "original_cost": c, "discounted_cost": c, "total_cost": c, "customer_name": h["customer_name"]}
    bookings.append(b)
    booking_counter += 1
    holds.remove(h)
    return b

@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id: int):
    h = next((x for x in holds if x["hold_id"] == hold_id), None)
    if not h: raise HTTPException(status_code=404, detail="Not found")
    find_movie(h["movie_id"])["seats_available"] += h["seats"]
    holds.remove(h)
    return {"message": "Released"}

@app.get("/bookings/search")
def search_backs(customer_name: str):
    return [b for b in bookings if customer_name.lower() in b["customer_name"].lower()]

@app.get("/bookings/sort")
def sort_books(sort_by: str = "total_cost"):
    if sort_by not in {"total_cost", "seats"}: raise HTTPException(status_code=400, detail="Invalid param")
    return sorted(bookings, key=lambda b: b[sort_by])

@app.get("/bookings/page")
def page_books(page: int = 1, limit: int = 3):
    return {"total": len(bookings), "sliced_list": bookings[(page - 1) * limit:(page - 1) * limit + limit]}
