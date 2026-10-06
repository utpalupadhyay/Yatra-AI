"""
Yatra AI - FastAPI Route Handlers
All trip planning and chat endpoints.
"""
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.trip import (
    TripRequest, ReplanRequest, ChatRequest,
    PackingRequest, TripResponse, ChatResponse
)
from app.services import gemma_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Yatra AI"])


@router.get("/health")
async def health_check():
    """API health check endpoint."""
    return {"status": "ok", "service": "Yatra AI", "model": "gemma-4-31b-it"}


@router.post("/trip/generate", response_model=TripResponse)
@router.post("/generate-trip", response_model=TripResponse)
async def generate_trip(request: TripRequest):
    """
    🗺️ Generate a complete personalized travel itinerary using Gemma 4.
    
    Core AI Feature: Gemma 4 analyzes all preferences and generates a
    structured day-by-day itinerary with budget breakdown.
    """
    try:
        origin_val = request.get_origin
        days_val = request.get_num_days
        travelers_val = request.get_num_travelers
        food_val = request.get_food_preference
        special_val = request.get_special_requests
        lang_val = str(request.language.value if hasattr(request.language, "value") else (request.language or "english"))
        accom_val = str(request.accommodation.value if hasattr(request.accommodation, "value") else (request.accommodation or "mid_range"))

        logger.info(f"Generating trip: {origin_val} → {request.destination}, {days_val} days")
        
        result = gemma_service.generate_itinerary(
            destination=request.destination,
            origin=origin_val,
            num_days=days_val,
            budget=request.budget,
            num_travelers=travelers_val,
            interests=request.interests,
            accommodation=accom_val,
            food_preference=food_val,
            special_requests=special_val,
            language=lang_val,
        )
        
        return TripResponse(
            success=True,
            itinerary=result["itinerary"],
            interaction_id=result.get("interaction_id"),
        )

    except ValueError as e:
        err_msg = str(e)
        logger.warning(f"Trip validation / AI error: {err_msg}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": err_msg, "detail": err_msg},
        )
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Trip generation error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": err_msg, "detail": err_msg},
        )


@router.post("/trip/replan", response_model=TripResponse)
async def replan_trip(request: ReplanRequest):
    """
    🔄 Smart Re-planner — Modify an existing trip using Gemma 4.
    
    User can say 'I only have ₹15,000 now' and Gemma 4 adapts the whole plan.
    """
    try:
        logger.info(f"Replanning trip to {request.destination}")
        
        result = gemma_service.replan_trip(
            original_plan=request.original_plan,
            change_request=request.change_request,
            destination=request.destination,
            num_days=request.num_days,
            new_budget=request.new_budget,
            language=request.language.value,
        )
        
        return TripResponse(
            success=True,
            itinerary=result["itinerary"],
            interaction_id=result["interaction_id"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Replan error: {e}")
        raise HTTPException(status_code=500, detail=f"Re-planning failed: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    💬 Multi-turn Travel Chat Assistant powered by Gemma 4.
    
    Maintains conversation context. Ask anything about your trip.
    """
    try:
        logger.info("Processing chat message")
        
        result = gemma_service.chat_with_assistant(
            message=request.message,
            trip_context=request.trip_context,
            conversation_id=request.conversation_id,
            language=request.language.value,
        )
        
        return ChatResponse(
            success=True,
            reply=result["reply"],
            interaction_id=result["interaction_id"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/trip/packing")
async def get_packing_list(request: PackingRequest):
    """
    🎒 Generate a personalized packing checklist using Gemma 4.
    """
    try:
        result = gemma_service.generate_packing_list(
            destination=request.destination,
            num_days=request.num_days,
            interests=request.interests,
            season=request.season,
            language=request.language.value,
        )
        
        return {
            "success": True,
            "packing_list": result["packing_list"],
            "interaction_id": result["interaction_id"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Packing list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trip/optimize-budget")
async def optimize_budget(
    destination: str,
    num_days: int,
    budget: float,
    num_travelers: int,
    current_plan: str,
    language: str = "english",
):
    """
    💰 Budget Optimizer — Gemma 4 analyzes and optimizes the trip budget.
    """
    try:
        result = gemma_service.optimize_budget(
            destination=destination,
            num_days=num_days,
            budget=budget,
            num_travelers=num_travelers,
            current_plan=current_plan,
            language=language,
        )
        
        return {
            "success": True,
            "optimization": result["optimization"],
            "interaction_id": result["interaction_id"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Budget optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
