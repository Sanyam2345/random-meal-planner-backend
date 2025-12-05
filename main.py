from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import re
import random

from database import get_db, init_db, Meal
from models import MealCreate, MealUpdate, MealResponse, RandomMealResponse, ShoppingListRequest, ShoppingListResponse, ShoppingListItem, WeeklyPlanResponse, DayMealPlan

app = FastAPI(title="Random Meal Planner API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

@app.get("/")
def read_root():
    return {"message": "Random Meal Planner API"}

@app.post("/meals", response_model=MealResponse)
def create_meal(meal: MealCreate, db: Session = Depends(get_db)):
    db_meal = Meal(**meal.model_dump())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

@app.get("/meals", response_model=list[MealResponse])
def get_meals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    meals = db.query(Meal).offset(skip).limit(limit).all()
    return meals

@app.get("/meals/{meal_id}", response_model=MealResponse)
def get_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    return meal

@app.put("/meals/{meal_id}", response_model=MealResponse)
def update_meal(meal_id: int, meal: MealUpdate, db: Session = Depends(get_db)):
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    update_data = meal.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_meal, key, value)
    
    db.commit()
    db.refresh(db_meal)
    return db_meal

@app.delete("/meals/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    db.delete(db_meal)
    db.commit()
    return {"message": "Meal deleted successfully"}

@app.get("/random", response_model=RandomMealResponse)
def get_random_meals(db: Session = Depends(get_db)):
    # Get all meals by category
    breakfast_meals = db.query(Meal).filter(Meal.category == "breakfast").all()
    lunch_meals = db.query(Meal).filter(Meal.category == "lunch").all()
    dinner_meals = db.query(Meal).filter(Meal.category == "dinner").all()
    
    # Randomly select one from each category (or None if empty)
    breakfast = random.choice(breakfast_meals) if breakfast_meals else None
    lunch = random.choice(lunch_meals) if lunch_meals else None
    dinner = random.choice(dinner_meals) if dinner_meals else None
    
    return RandomMealResponse(
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner
    )

@app.post("/shopping-list", response_model=ShoppingListResponse)
def get_shopping_list(request: ShoppingListRequest, db: Session = Depends(get_db)):
    meal_ids = request.meal_ids
    meals = db.query(Meal).filter(Meal.id.in_(meal_ids)).all()
    
    # Parse ingredients from all meals
    ingredient_dict = {}
    
    for meal in meals:
        # Split ingredients by comma or newline
        ingredients_text = meal.ingredients
        # Split by commas, newlines, or semicolons
        ingredients = re.split(r'[,;\n]', ingredients_text)
        
        for ingredient in ingredients:
            ingredient = ingredient.strip().lower()
            if ingredient:
                ingredient_dict[ingredient] = ingredient_dict.get(ingredient, 0) + 1
    
    shopping_items = [
        ShoppingListItem(ingredient=ingredient, count=count)
        for ingredient, count in sorted(ingredient_dict.items())
    ]
    
    return ShoppingListResponse(ingredients=shopping_items)

@app.post("/ai/weekly-plan", response_model=WeeklyPlanResponse)
def generate_weekly_plan():
    """
    Generate a weekly meal plan (mock data).
    Returns a 7-day meal plan with breakfast, lunch, and dinner for each day.
    """
    # Mock meal data for weekly plan
    mock_meals = {
        "breakfast": [
            {"id": 1, "name": "Scrambled Eggs with Toast", "ingredients": "eggs, bread, butter, salt, pepper", "category": "breakfast"},
            {"id": 2, "name": "Oatmeal with Berries", "ingredients": "oats, milk, blueberries, strawberries, honey", "category": "breakfast"},
            {"id": 3, "name": "Pancakes", "ingredients": "flour, eggs, milk, butter, syrup", "category": "breakfast"},
            {"id": 4, "name": "Greek Yogurt Parfait", "ingredients": "greek yogurt, granola, honey, fresh berries", "category": "breakfast"},
            {"id": 5, "name": "Avocado Toast", "ingredients": "bread, avocado, lemon, salt, pepper, olive oil", "category": "breakfast"},
        ],
        "lunch": [
            {"id": 6, "name": "Caesar Salad", "ingredients": "romaine lettuce, parmesan, croutons, caesar dressing, chicken", "category": "lunch"},
            {"id": 7, "name": "Chicken Wrap", "ingredients": "tortilla, chicken, lettuce, tomatoes, mayo, cheese", "category": "lunch"},
            {"id": 8, "name": "Vegetable Stir Fry", "ingredients": "mixed vegetables, soy sauce, garlic, ginger, rice", "category": "lunch"},
            {"id": 9, "name": "Grilled Salmon Bowl", "ingredients": "salmon, quinoa, vegetables, lemon, olive oil", "category": "lunch"},
            {"id": 10, "name": "Pasta Primavera", "ingredients": "pasta, mixed vegetables, olive oil, garlic, parmesan", "category": "lunch"},
        ],
        "dinner": [
            {"id": 11, "name": "Grilled Chicken Breast", "ingredients": "chicken breast, olive oil, herbs, vegetables, rice", "category": "dinner"},
            {"id": 12, "name": "Beef Stir Fry", "ingredients": "beef, bell peppers, onions, soy sauce, rice", "category": "dinner"},
            {"id": 13, "name": "Vegetarian Lasagna", "ingredients": "lasagna noodles, ricotta, spinach, marinara sauce, cheese", "category": "dinner"},
            {"id": 14, "name": "Baked Salmon", "ingredients": "salmon fillet, lemon, herbs, vegetables, potatoes", "category": "dinner"},
            {"id": 15, "name": "Chicken Curry", "ingredients": "chicken, curry powder, coconut milk, vegetables, rice", "category": "dinner"},
        ]
    }
    
    # Randomly select meals for each day
    days_plan = {}
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    for day in days:
        breakfast_meal = random.choice(mock_meals["breakfast"])
        lunch_meal = random.choice(mock_meals["lunch"])
        dinner_meal = random.choice(mock_meals["dinner"])
        
        days_plan[day] = DayMealPlan(
            breakfast=MealResponse(**breakfast_meal),
            lunch=MealResponse(**lunch_meal),
            dinner=MealResponse(**dinner_meal)
        )
    
    return WeeklyPlanResponse(**days_plan)

