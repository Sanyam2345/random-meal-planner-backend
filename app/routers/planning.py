from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import Meal, ShoppingListRequest, ShoppingListResponse, ShoppingListItem, WeeklyPlanResponse, DayMealPlan, MealResponse
import re
import random

router = APIRouter(
    tags=["planning"]
)

@router.post("/shopping-list", response_model=ShoppingListResponse)
def get_shopping_list(request: ShoppingListRequest, db: Session = Depends(get_db)):
    meal_ids = request.meal_ids
    meals = db.query(Meal).filter(Meal.id.in_(meal_ids)).all()
    
    # Improved parser could go here
    ingredient_dict = {}
    
    for meal in meals:
        ingredients_text = meal.ingredients
        # Split by newlines or commas
        ingredients = re.split(r'[,;\n]', ingredients_text)
        
        for ingredient in ingredients:
            raw = ingredient.strip().lower()
            if not raw:
                continue
                
            # Basic Regex to capture "2 eggs", "1/2 cup flour", "300g chicken"
            # Groups: (quantity) (unit)? (item)
            match = re.match(r'^([\d\./]+)\s*(?:([a-zA-Z]+)\s+)?(.*)$', raw)
            
            if match:
                qty_str = match.group(1)
                unit = match.group(2) or ""
                item = match.group(3)
                
                # Basic fraction to float conversion (simple cases)
                try:
                    if '/' in qty_str:
                        num, den = qty_str.split('/')
                        qty = float(num) / float(den)
                    else:
                        qty = float(qty_str)
                except ValueError:
                    qty = 1.0
                    item = raw # Fallback
                
                # Create a key that combines unit + item (e.g., "cup flour")
                key = f"{unit} {item}".strip()
                ingredient_dict[key] = ingredient_dict.get(key, 0) + qty
            else:
                # No number found, just add 1
                ingredient_dict[raw] = ingredient_dict.get(raw, 0) + 1
    
    shopping_items = [
        ShoppingListItem(ingredient=ingredient, count=count)
        for ingredient, count in sorted(ingredient_dict.items())
    ]
    
    return ShoppingListResponse(ingredients=shopping_items)

@router.get("/weekly-plan", response_model=WeeklyPlanResponse)
def generate_weekly_plan(
    diet_type: Optional[str] = None,
    max_calories: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Generate a REAL weekly meal plan from database with filters.
    """
    base_query = db.query(Meal)
    
    if diet_type and diet_type != "all":
        base_query = base_query.filter(Meal.diet_type == diet_type)
        
    if max_calories:
        base_query = base_query.filter(Meal.calories <= max_calories)

    # Fetch all meals grouped by category
    breakfasts = base_query.filter(Meal.category == 'breakfast').all()
    lunches = base_query.filter(Meal.category == 'lunch').all()
    dinners = base_query.filter(Meal.category == 'dinner').all()
    
    # Helper to clean/convert DB meal to Response
    def to_response(meal):
        if not meal: return None
        return MealResponse.model_validate(meal)

    days_plan = {}
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    for day in days:
        # Fallback to None if no meals exist in that category
        b = random.choice(breakfasts) if breakfasts else None
        l = random.choice(lunches) if lunches else None
        d = random.choice(dinners) if dinners else None
        
        days_plan[day] = DayMealPlan(
            breakfast=to_response(b),
            lunch=to_response(l),
            dinner=to_response(d)
        )
    
    return WeeklyPlanResponse(**days_plan)
