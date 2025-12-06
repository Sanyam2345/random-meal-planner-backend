<<<<<<< HEAD
from pydantic import BaseModel
from typing import Optional

class MealBase(BaseModel):
    name: str
    ingredients: str
    category: str

class MealCreate(MealBase):
    pass

class MealUpdate(BaseModel):
    name: Optional[str] = None
    ingredients: Optional[str] = None
    category: Optional[str] = None

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

class ShoppingListRequest(BaseModel):
    meal_ids: list[int]

class ShoppingListResponse(BaseModel):
    ingredients: list[ShoppingListItem]

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
    message: str = "Weekly meal plan generated successfully (mock data)"

=======
from pydantic import BaseModel
from typing import Optional

class MealBase(BaseModel):
    name: str
    ingredients: str
    category: str

class MealCreate(MealBase):
    pass

class MealUpdate(BaseModel):
    name: Optional[str] = None
    ingredients: Optional[str] = None
    category: Optional[str] = None

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

class ShoppingListRequest(BaseModel):
    meal_ids: list[int]

class ShoppingListResponse(BaseModel):
    ingredients: list[ShoppingListItem]

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
    message: str = "Weekly meal plan generated successfully (mock data)"

>>>>>>> 2d74c10219954dc9ac16d606db0f25e6bc708a82
