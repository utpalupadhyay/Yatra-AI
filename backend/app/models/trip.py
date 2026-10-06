"""
Yatra AI - Pydantic models for request/response validation.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field, model_validator
from enum import Enum


class AccommodationType(str, Enum):
    budget = "budget"
    mid_range = "mid_range"
    luxury = "luxury"
    hostel = "hostel"
    homestay = "homestay"


class FoodPreference(str, Enum):
    vegetarian = "vegetarian"
    non_vegetarian = "non_vegetarian"
    vegan = "vegan"
    any = "any"


class Language(str, Enum):
    english = "english"
    hindi = "hindi"


class TripRequest(BaseModel):
    destination: str = Field(..., description="Travel destination")
    origin: Optional[str] = Field(None, description="Starting location")
    num_days: Optional[int] = Field(None, description="Number of travel days")
    budget: float = Field(..., ge=500, description="Total budget in INR")
    num_travelers: Optional[int] = Field(None, description="Number of travelers")
    interests: list[str] = Field(default_factory=list, description="Travel interests")
    accommodation: str = Field("mid_range", description="Accommodation preference")
    food_preference: Optional[str] = Field("any", description="Food preference")
    language: Optional[str] = Field("english", description="Response language")
    special_requests: Optional[str] = Field(None, description="Special requests")

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize 'from' -> 'origin'
            if "from" in data and not data.get("origin"):
                data["origin"] = data["from"]
            elif "from_loc" in data and not data.get("origin"):
                data["origin"] = data["from_loc"]
            # Normalize 'days' -> 'num_days'
            if "days" in data and not data.get("num_days"):
                data["num_days"] = data["days"]
            # Normalize 'travelers' -> 'num_travelers'
            if "travelers" in data and not data.get("num_travelers"):
                data["num_travelers"] = data["travelers"]
            # Normalize 'foodPreference' -> 'food_preference'
            if "foodPreference" in data and not data.get("food_preference"):
                data["food_preference"] = data["foodPreference"]
            # Normalize 'specialRequests' -> 'special_requests'
            if "specialRequests" in data and not data.get("special_requests"):
                data["special_requests"] = data["specialRequests"]
        return data

    @property
    def get_origin(self) -> str:
        return self.origin or "Your City"

    @property
    def get_num_days(self) -> int:
        return self.num_days or 3

    @property
    def get_num_travelers(self) -> int:
        return self.num_travelers or 1

    @property
    def get_food_preference(self) -> str:
        return self.food_preference or "any"

    @property
    def get_special_requests(self) -> Optional[str]:
        return self.special_requests or None


class ReplanRequest(BaseModel):
    original_plan: str = Field(..., description="Original trip plan text")
    change_request: str = Field(..., min_length=5, max_length=1000, description="What the user wants to change")
    destination: str
    num_days: int
    new_budget: Optional[float] = None
    language: Language = Language.english


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    trip_context: Optional[str] = Field(None, description="Current trip plan for context")
    conversation_id: Optional[str] = Field(None, description="Previous interaction ID for multi-turn chat")
    language: Language = Language.english


class PackingRequest(BaseModel):
    destination: str
    num_days: int
    interests: list[str] = Field(default_factory=list)
    season: Optional[str] = None
    language: Language = Language.english


class TripResponse(BaseModel):
    success: bool
    itinerary: Optional[str] = None
    budget_breakdown: Optional[str] = None
    recommendations: Optional[str] = None
    packing_list: Optional[str] = None
    emergency_plan: Optional[str] = None
    interaction_id: Optional[str] = None
    error: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    reply: Optional[str] = None
    interaction_id: Optional[str] = None
    error: Optional[str] = None
