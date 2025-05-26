"""
LLM-based integration between preference gathering and hotel search.
"""
import json
from typing import Dict, List, Tuple, Optional

from llm.ollama_client import get_ollama_client


# System prompt for extracting search parameters
EXTRACT_SEARCH_PARAMS_SYSTEM = """
You are an AI assistant that extracts clean search parameters from hotel preferences.
Your task is to convert raw user answers into structured data for hotel search APIs.

Always respond with valid JSON in exactly this format:
{
    "location": "City, Country",
    "check_in": "YYYY-MM-DD",
    "check_out": "YYYY-MM-DD"
}

Rules:
- Clean up location names to proper format (e.g., "rome, italy" → "Rome, Italy")
- Convert all dates to YYYY-MM-DD format
- If dates are unclear, make reasonable assumptions
- If location is unclear, use the best interpretation
"""

EXTRACT_SEARCH_PARAMS_PROMPT = """
Extract search parameters from these hotel preferences:

Destination: {destination}
Travel Dates: {travel_dates}

Convert this to clean search parameters. Respond with only the JSON, no other text.
"""


def extract_search_parameters(preferences: Dict[str, str]) -> Dict[str, str]:
    """
    Use LLM to extract clean search parameters from raw preferences.

    Args:
        preferences: Raw preferences from conversation

    Returns:
        Dict with cleaned location and date parameters
    """
    # Get raw answers
    destination = preferences.get("destination", "")
    travel_dates = preferences.get("travel_dates", "")

    if not destination or not travel_dates:
        raise ValueError("Missing destination or travel_dates in preferences")

    # Get LLM client
    client = get_ollama_client()

    # Create prompt
    prompt = EXTRACT_SEARCH_PARAMS_PROMPT.format(
        destination=destination,
        travel_dates=travel_dates
    )

    # Get LLM response
    response = client.generate(
        prompt=prompt,
        system_prompt=EXTRACT_SEARCH_PARAMS_SYSTEM
    )

    try:
        # Clean up markdown code blocks that the LLM might add
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove ```
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]  # Remove ```
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove ```

        cleaned_response = cleaned_response.strip()

        # Parse JSON response
        params = json.loads(cleaned_response)

        # Validate required fields
        required_fields = ["location", "check_in", "check_out"]
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")

        return params

    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {response}") from e

def search_hotels_from_preferences(
    preferences: Dict[str, str],
    hotel_search_client,
    radius_km: float = 5.0,
    max_results: int = 20
) -> List[Dict]:
    """
    Search for hotels using raw preferences from conversation.

    Args:
        preferences: Raw preferences dict from conversation
        hotel_search_client: Your HotelSearchClient instance
        radius_km: Search radius in kilometers
        max_results: Maximum hotels to return

    Returns:
        List of hotel dictionaries
    """
    # Extract clean search parameters using LLM
    search_params = extract_search_parameters(preferences)

    # Search for hotels using the simple method
    hotels = hotel_search_client.search_hotels(
        location=search_params["location"],
        check_in=search_params["check_in"],
        check_out=search_params["check_out"],
        radius_km=radius_km,
        max_results=max_results
    )

    return hotels


def create_hotel_summary_for_llm(hotels: List[Dict], preferences: Dict[str, str]) -> Dict:
    """
    Create a summary of hotels and preferences optimized for frontier LLM analysis.

    Args:
        hotels: List of hotel results from search
        preferences: Original conversation preferences

    Returns:
        Dict containing structured data for LLM reasoning
    """
    # Extract key preference details
    budget = preferences.get("budget_preference", "")
    amenities = preferences.get("amenities_features", "")
    style = preferences.get("stay_experience", "")
    purpose = preferences.get("trip_purpose", "")

    # Create simple hotel summaries
    hotel_summaries = []
    for hotel in hotels:
        pricing_data = hotel.get("pricing_data")

        summary = {
            "name": hotel["name"],
            "rating": hotel.get("rating"),
            "address": hotel.get("address", ""),
            "total_price": pricing_data.get("total_price") if pricing_data else "Not available",
            "price_per_night": pricing_data.get("price_per_night") if pricing_data else "Not available",
            "has_pricing": hotel.get("has_pricing_info", False)
        }
        hotel_summaries.append(summary)

    return {
        "customer_preferences": {
            "budget": budget,
            "amenities": amenities,
            "style": style,
            "purpose": purpose
        },
        "search_results": {
            "total_hotels": len(hotels),
            "hotels_with_pricing": sum(1 for h in hotels if h.get("has_pricing_info")),
            "hotels": hotel_summaries
        },
        "ready_for_frontier_llm": True
    }


# Example usage function
def test_integration(preferences: Dict[str, str]):
    """
    Test the integration with sample preferences.
    """
    print("🧪 Testing LLM-based search integration")
    print("=" * 50)

    print("Raw preferences:")
    for key, value in preferences.items():
        print(f"  {key}: {value}")

    try:
        # Extract search parameters
        search_params = extract_search_parameters(preferences)
        print(f"\n✅ Extracted parameters:")
        print(f"  Location: {search_params['location']}")
        print(f"  Check-in: {search_params['check_in']}")
        print(f"  Check-out: {search_params['check_out']}")

        # Note: To actually test hotel search, you'd need:
        # from your_hotel_search_module import HotelSearchClient
        # client = HotelSearchClient(api_key)
        # hotels, metadata = search_hotels_from_preferences(preferences, client)

        print(f"\n💡 Ready to search hotels with these parameters!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    # Test with sample preferences from your conversation
    sample_preferences = {
        "destination": "rome, italy",
        "travel_dates": "october 2 to october 8, 2025",
        "trip_purpose": "buisiness",
        "budget_preference": "$240 a night",
        "amenities_features": "room service, gym, and restaurants can walk to",
        "stay_experience": "historic is great"
    }

    test_integration(sample_preferences)
