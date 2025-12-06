from sqlalchemy import Column, Integer, String, Text
from .database import Base
from pydantic import BaseModel
from typing import Optional, List

# --- SQLAlchemy Models ---
class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ingredients = Column(Text)
    category = Column(String, index=True)  # breakfast, lunch, dinner, snack
    
    # New Fields
    image_url = Column(String, nullable=True)
    prep_time = Column(Integer, default=15) # in minutes
    servings = Column(Integer, default=2)
    calories = Column(Integer, nullable=True)
    diet_type = Column(String, nullable=True) # veg, non-veg, vegan, keto

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# --- Pydantic Schemas ---

class MealBase(BaseModel):
    name: str
    ingredients: str
    category: str
    image_url: Optional[str] = None
    prep_time: Optional[int] = 15
    servings: Optional[int] = 2
    calories: Optional[int] = None
    diet_type: Optional[str] = "veg"

class MealCreate(MealBase):
    pass

class MealUpdate(BaseModel):
    name: Optional[str] = None
    ingredients: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    prep_time: Optional[int] = None
    servings: Optional[int] = None
    calories: Optional[int] = None
    diet_type: Optional[str] = None

class MealResponse(MealBase):
    id: int

    class Config:
        from_attributes = True

class RandomMealResponse(BaseModel):
    breakfast: Optional[MealResponse] = None
    lunch: Optional[MealResponse] = None
    dinner: Optional[MealResponse] = None

class ShoppingListItem(BaseModel):
    ingredient: str
    count: int

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ShoppingListRequest(BaseModel):
    meal_ids: List[int]

class ShoppingListResponse(BaseModel):
    ingredients: List[ShoppingListItem]

class DayMealPlan(BaseModel):
    breakfast: Optional[MealResponse] = None
    lunch: Optional[MealResponse] = None
    dinner: Optional[MealResponse] = None

class WeeklyPlanResponse(BaseModel):
    monday: DayMealPlan
    tuesday: DayMealPlan
    wednesday: DayMealPlan
    thursday: DayMealPlan
    friday: DayMealPlan
    saturday: DayMealPlan
    sunday: DayMealPlan
    message: str = "Weekly meal plan generated successfully"
