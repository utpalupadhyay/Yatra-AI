"""
Yatra AI - Gemma 4 Service
Core AI engine using Gemma 4 via the Gemini API SDK.
Model: gemma-4-31b-it (Dense) or gemma-4-26b-a4b-it (MoE)
"""
import os
import logging
from typing import Optional
from google import genai

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    """Retrieve GEMMA_API_KEY from environment or settings."""
    key = os.environ.get("GEMMA_API_KEY", "").strip()
    if not key:
        settings = get_settings()
        key = (settings.GEMMA_API_KEY or "").strip()
    return key


def _get_client() -> genai.Client:
    """Return an authenticated Gemini API client."""
    key = _get_api_key()
    if not key or key in ["your_actual_key", "your_new_key_here", "your_gemma_api_key_here"]:
        raise ValueError(
            "AI service is not configured. Please add GEMMA_API_KEY to the server environment."
        )
    return genai.Client(api_key=key)


def _build_system_prompt(language: str = "english") -> str:
    """Return the Yatra AI system prompt in the requested language."""
    if language == "hindi":
        return (
            "आप Yatra AI हैं — एक बुद्धिमान भारतीय यात्रा योजनाकार। "
            "आप Gemma 4 द्वारा संचालित हैं। "
            "आप विस्तृत, व्यावहारिक, बजट-जागरूक यात्रा योजनाएँ बनाते हैं। "
            "हमेशा INR (₹) में कीमतें दें। "
            "उत्तर को स्पष्ट और सुव्यवस्थित मार्कडाउन में दें।"
        )
    return (
        "You are Yatra AI, an intelligent Indian travel planner powered by Gemma 4. "
        "You create detailed, practical, budget-aware travel itineraries for Indian destinations. "
        "Always provide prices in INR (₹). Be specific about places, food, and activities. "
        "Format output clearly using Markdown with emojis for visual appeal. "
        "You are empathetic, knowledgeable about Indian culture, festivals, food, and travel logistics."
    )


# ──────────────────────────────────────────────
# CORE FEATURE 1: Trip Itinerary Generator
# ──────────────────────────────────────────────
def generate_itinerary(
    destination: str,
    origin: str,
    num_days: int,
    budget: float,
    num_travelers: int,
    interests: list[str],
    accommodation: str,
    food_preference: str,
    special_requests: Optional[str],
    language: str = "english",
) -> dict:
    """
    Generate a full day-by-day travel itinerary using Gemma 4.
    Returns a dict with itinerary and interaction_id.
    """
    client = _get_client()
    settings = get_settings()

    interests_str = (
        ", ".join(interests) if interests and len(interests) > 0
        else "No specific interests selected"
    )
    lang_instruction = "Respond in Hindi." if language == "hindi" else "Respond in English."

    prompt = f"""
{lang_instruction}
Create a personalized travel itinerary.

Starting location: {origin}
Destination: {destination}
Number of days: {num_days}
Number of travelers: {num_travelers}
Total budget: ₹{budget:,.0f}

Travel interests:
{interests_str}

Accommodation:
{accommodation.replace('_', ' ').title()}

Food preference:
{food_preference.replace('_', ' ').title()}

Special requests:
{special_requests or "None"}

Generate a practical day-by-day itinerary.

Include:
- Day-by-day schedule (Morning, Afternoon, Evening)
- Places to visit
- Suggested activities
- Food recommendations
- Accommodation suggestions
- Approximate daily cost
- Local transportation suggestions
- Estimated total cost
- Useful travel tips

Keep the itinerary within the user's total budget as much as realistically possible.
"""

    try:
        interaction = client.interactions.create(
            model=settings.GEMMA_MODEL,
            input=prompt,
            system_instruction=_build_system_prompt(language),
        )
    except Exception as e:
        err_str = str(e).lower()
        if any(w in err_str for w in ["api_key_invalid", "api key not valid", "invalid api key", "unauthenticated", "401", "403", "permission_denied"]):
            raise ValueError("The AI API key is invalid or expired.")
        elif any(w in err_str for w in ["resource_exhausted", "quota", "rate limit", "busy", "429"]):
            raise ValueError("The AI service is temporarily busy. Please try again.")
        elif any(w in err_str for w in ["connect", "connecterror", "timeout", "timed out", "dns", "network", "offline"]):
            raise ValueError("Unable to connect to the AI service. Please try again.")
        else:
            logger.error(f"Gemma 4 generation error: {e}")
            raise ValueError(f"AI generation failed: {str(e)}")

    output_text = getattr(interaction, "output_text", None)
    if not output_text or not output_text.strip():
        raise ValueError("The AI returned an unexpected response.")

    return {
        "itinerary": output_text,
        "interaction_id": getattr(interaction, "id", None),
    }

# ──────────────────────────────────────────────
# CORE FEATURE 2: Smart Re-planner
# ──────────────────────────────────────────────
def replan_trip(
    original_plan: str,
    change_request: str,
    destination: str,
    num_days: int,
    new_budget: Optional[float],
    language: str = "english",
) -> dict:
    """
    Intelligently re-plan a trip based on user's change request using Gemma 4.
    Maintains conversation context via previous_interaction_id if provided.
    """
    client = _get_client()
    lang_instruction = "Respond in Hindi." if language == "hindi" else "Respond in English."
    budget_note = f"New budget constraint: ₹{new_budget:,.0f}" if new_budget else "Budget remains the same."

    prompt = f"""
{lang_instruction}
The user wants to modify their existing {num_days}-day trip to {destination}.

**Original Trip Plan:**
{original_plan[:3000]}

**User's Change Request:**
{change_request}

**{budget_note}**

Please provide:
1. **What Changed** — briefly explain the modifications made
2. **Updated Itinerary** — the revised day-by-day plan (only show changed days in full, summarize unchanged days)
3. **Updated Budget Breakdown** — revised cost estimates
4. **Why This Works** — explain how the new plan is better given the constraints

Keep the tone positive and helpful. Make sure the revised plan is realistic.
"""

    interaction = client.interactions.create(
        model=settings.GEMMA_MODEL,
        input=prompt,
        system_instruction=_build_system_prompt(language),
    )

    return {
        "itinerary": interaction.output_text,
        "interaction_id": interaction.id,
    }


# ──────────────────────────────────────────────
# CORE FEATURE 3: Travel Chat Assistant
# ──────────────────────────────────────────────
def chat_with_assistant(
    message: str,
    trip_context: Optional[str],
    conversation_id: Optional[str],
    language: str = "english",
) -> dict:
    """
    Multi-turn travel chat assistant powered by Gemma 4.
    Maintains conversation history via previous_interaction_id.
    """
    client = _get_client()
    lang_instruction = "Respond in Hindi." if language == "hindi" else "Respond in English."

    context_block = ""
    if trip_context:
        context_block = f"""
**Current Trip Plan Context:**
{trip_context[:2000]}

"""

    full_input = f"{lang_instruction}\n\n{context_block}**User Question:** {message}"

    kwargs = {
        "model": settings.GEMMA_MODEL,
        "input": full_input,
        "system_instruction": _build_system_prompt(language),
    }

    # Enable multi-turn conversation if a previous interaction ID exists
    if conversation_id:
        kwargs["previous_interaction_id"] = conversation_id

    interaction = client.interactions.create(**kwargs)

    return {
        "reply": interaction.output_text,
        "interaction_id": interaction.id,
    }


# ──────────────────────────────────────────────
# CORE FEATURE 4: Packing Assistant
# ──────────────────────────────────────────────
def generate_packing_list(
    destination: str,
    num_days: int,
    interests: list[str],
    season: Optional[str],
    language: str = "english",
) -> dict:
    """Generate a personalized packing checklist using Gemma 4."""
    client = _get_client()
    lang_instruction = "Respond in Hindi." if language == "hindi" else "Respond in English."
    interests_str = ", ".join(interests) if interests else "General sightseeing"
    season_note = f"Current season: {season}" if season else ""

    prompt = f"""
{lang_instruction}
Create a smart, personalized packing checklist for:
- 📍 Destination: {destination}
- 📅 Duration: {num_days} days
- 🎯 Activities: {interests_str}
- {season_note}

## 🎒 Packing Checklist

Organize into categories:
### 👔 Clothing
### 🔌 Electronics & Tech
### 💊 Health & Medicine
### 📄 Documents & Money
### 🧴 Toiletries
### 🎒 Backpack Essentials
### 🌦️ Weather-Specific Items
### 🎯 Activity-Specific Items (based on {interests_str})

Add ✅ checkbox format. Include quantities where relevant.
At the end, add a "**Don't Forget**" section with 5 India-specific travel tips.
"""

    interaction = client.interactions.create(
        model=settings.GEMMA_MODEL,
        input=prompt,
        system_instruction=_build_system_prompt(language),
    )

    return {
        "packing_list": interaction.output_text,
        "interaction_id": interaction.id,
    }


# ──────────────────────────────────────────────
# CORE FEATURE 5: Budget Optimizer
# ──────────────────────────────────────────────
def optimize_budget(
    destination: str,
    num_days: int,
    budget: float,
    num_travelers: int,
    current_plan: str,
    language: str = "english",
) -> dict:
    """Analyze and optimize the trip budget using Gemma 4."""
    client = _get_client()
    lang_instruction = "Respond in Hindi." if language == "hindi" else "Respond in English."

    prompt = f"""
{lang_instruction}
Analyze and optimize the budget for this trip:
- Destination: {destination}
- Duration: {num_days} days
- Budget: ₹{budget:,.0f} for {num_travelers} traveler(s)
- Per person: ₹{budget/num_travelers:,.0f}

Current plan:
{current_plan[:2000]}

Provide:
## 💡 Budget Optimization Report

### 💰 Cost-Saving Opportunities
List specific ways to save money on this trip.

### 🔄 Budget Reallocation Suggestions
How to redistribute budget for best experience.

### 🏷️ Best Value Activities
Top 5 high-value, low-cost activities for this destination.

### 🍜 Budget-Friendly Food Guide
Where to eat well without overspending.

### 🚌 Smart Transport Tips
Cheapest ways to get around.

### 📊 Revised Budget Table
| Category | Original | Optimized | Savings |
|---|---|---|---|
"""

    interaction = client.interactions.create(
        model=settings.GEMMA_MODEL,
        input=prompt,
        system_instruction=_build_system_prompt(language),
    )

    return {
        "optimization": interaction.output_text,
        "interaction_id": interaction.id,
    }
