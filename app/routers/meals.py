from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from ..database import get_db
from ..models import Meal, MealCreate, MealUpdate, MealResponse, RandomMealResponse
import random

router = APIRouter(
    prefix="/meals",
    tags=["meals"]
)

@router.post("/", response_model=MealResponse)
def create_meal(meal: MealCreate, db: Session = Depends(get_db)):
    db_meal = Meal(**meal.model_dump())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

@router.get("/", response_model=List[MealResponse])
def get_meals(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_calories: Optional[int] = None,
    max_calories: Optional[int] = None,
    diet_type: Optional[str] = None,
    # For ingredients, we'll do basic substring matching for now as we don't have a robust many-to-many yet
    include_ingredients: Optional[str] = None, # comma separated
    exclude_ingredients: Optional[str] = None, # comma separated
    db: Session = Depends(get_db)
):
    query = db.query(Meal)
    
    if category:
        query = query.filter(Meal.category == category)
        
    if search:
        query = query.filter(Meal.name.contains(search))

    if min_calories is not None:
        query = query.filter(Meal.calories >= min_calories)
    
    if max_calories is not None:
        query = query.filter(Meal.calories <= max_calories)

    if diet_type and diet_type != "all":
        query = query.filter(Meal.diet_type == diet_type)
        
    if include_ingredients:
        ingredients = [i.strip() for i in include_ingredients.split(",")]
        for ingredient in ingredients:
            if ingredient:
                 query = query.filter(Meal.ingredients.contains(ingredient))

    # Exclusion is tricky with just text search, but let's try
    if exclude_ingredients:
        ingredients = [i.strip() for i in exclude_ingredients.split(",")]
        for ingredient in ingredients:
            if ingredient:
                 query = query.filter(~Meal.ingredients.contains(ingredient))
        
    meals = query.offset(skip).limit(limit).all()
    return meals

@router.get("/random", response_model=RandomMealResponse)
def get_random_meals(
    diet_type: Optional[str] = None,
    max_calories: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Base query for random selection
    base_query = db.query(Meal)
    
    if diet_type and diet_type != "all":
        base_query = base_query.filter(Meal.diet_type == diet_type)
    
    if max_calories:
        base_query = base_query.filter(Meal.calories <= max_calories)

    breakfast_meals = base_query.filter(Meal.category == "breakfast").all()
    lunch_meals = base_query.filter(Meal.category == "lunch").all()
    dinner_meals = base_query.filter(Meal.category == "dinner").all()
    
    breakfast = random.choice(breakfast_meals) if breakfast_meals else None
    lunch = random.choice(lunch_meals) if lunch_meals else None
    dinner = random.choice(dinner_meals) if dinner_meals else None
    
    return RandomMealResponse(
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner
    )

@router.get("/{meal_id}", response_model=MealResponse)
def get_meal(meal_id: int, db: Session = Depends(get_db)):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    return meal

@router.put("/{meal_id}", response_model=MealResponse)
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

@router.delete("/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    db.delete(db_meal)
    db.commit()
    return {"message": "Meal deleted successfully"}
