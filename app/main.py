from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import meals, planning, auth

app = FastAPI(title="MealGenie API v2")

# CORS middleware - Load from env in real app, hardcoded for now to support existing frontend
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://elegant-eclair-c843ed.netlify.app",
    "https://daily-meal-generator.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Include Routers
# Include Routers
app.include_router(meals.router)
app.include_router(planning.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "MealGenie API v2 is running"}
