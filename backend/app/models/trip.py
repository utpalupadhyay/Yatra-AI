"""
Yatra AI - Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
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
    destination: str = Field(..., min_length=2, max_length=200, description="Travel destination")
    origin: str = Field(..., min_length=2, max_length=200, description="Starting city")
    num_days: int = Field(..., ge=1, le=30, description="Number of travel days")
    budget: float = Field(..., ge=500, description="Total budget in INR")
    num_travelers: int = Field(..., ge=1, le=20, description="Number of travelers")
    interests: list[str] = Field(default_factory=list, description="Travel interests")
    accommodation: AccommodationType = AccommodationType.mid_range
    food_preference: FoodPreference = FoodPreference.any
    language: Language = Language.english
    special_requests: Optional[str] = Field(None, max_length=500)


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
