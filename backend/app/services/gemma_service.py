"""
Yatra AI - Gemma 4 Service
Core AI engine using Gemma 4 via the Gemini API SDK.
Model: gemma-4-31b-it (Dense) or gemma-4-26b-a4b-it (MoE)
"""
import logging
from typing import Optional
from google import genai

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_client() -> genai.Client:
    """Return an authenticated Gemini API client."""
    if not settings.GEMMA_API_KEY:
        raise ValueError(
            "GEMMA_API_KEY is not set. Please add it to your .env file."
        )
    return genai.Client(api_key=settings.GEMMA_API_KEY)


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
    Returns a dict with itinerary, budget_breakdown, and interaction_id.
    """
    client = _get_client()
    interests_str = ", ".join(interests)
    lang_instruction = "Respond in Hindi." if language == "hindi" else "Respond in English."

    prompt = f"""
{lang_instruction}
Create a complete {num_days}-day travel itinerary for the following trip:

**Trip Details:**
- 🗺️ From: {origin}
- 📍 Destination: {destination}
- 📅 Duration: {num_days} days
- 💰 Total Budget: ₹{budget:,.0f} for {num_travelers} traveler(s) (₹{budget/num_travelers:,.0f} per person)
- 👥 Travelers: {num_travelers}
- 🎯 Interests: {interests_str}
- 🏨 Accommodation: {accommodation.replace('_', ' ').title()}
- 🍴 Food Preference: {food_preference.replace('_', ' ').title()}
{f'- 📝 Special Requests: {special_requests}' if special_requests else ''}

**Generate:**

## 🗓️ Day-by-Day Itinerary

For each day, provide:
- **Morning** (activity + estimated cost)
- **Afternoon** (activity + estimated cost)
- **Evening** (activity + estimated cost)
- **Dinner** (restaurant recommendation + cost)
- **Overnight** (accommodation + cost)

## 💰 Budget Breakdown

Provide a detailed budget breakdown:
- Transportation (to/from + local): ₹xxx
- Accommodation ({num_days} nights): ₹xxx
- Food & Dining: ₹xxx
- Entry Tickets & Activities: ₹xxx
- Shopping & Miscellaneous: ₹xxx
- **Total Estimated: ₹xxx**
- **Budget Status:** [Under/Over/On Budget]

## ✨ Pro Travel Tips

Provide 5 specific tips for this trip (best time to visit, local transport, must-try food, cultural etiquette, safety).

## 🚨 Emergency & Backup Plan

Provide 2-3 backup activities if weather or circumstances change.

Make the plan realistic, specific, and exciting!
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
    interests_str = ", ".join(interests)
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
