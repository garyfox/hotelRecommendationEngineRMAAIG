#!/usr/bin/env python3
"""
Test the complete search pipeline using saved session data.
Tests both LLM parameter extraction and hotel search.
"""
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from search.integration import extract_search_parameters, search_hotels_from_preferences
from search.hotel_client import HotelSearchClient


def load_latest_conversation() -> dict:
    """Load the most recent conversation data."""
    conversations_dir = Path("data/conversations")

    if not conversations_dir.exists():
        raise FileNotFoundError("No conversations directory found. Run an interview first.")

    # Look for conversation files (could be .jsonl or .json)
    conversation_files = list(conversations_dir.glob("*.json*"))
    if not conversation_files:
        raise FileNotFoundError("No saved conversations found. Run an interview first.")

    # Get the most recent conversation
    latest_conversation = max(conversation_files, key=lambda x: x.stat().st_mtime)

    print(f"📁 Loading conversation: {latest_conversation.name}")

    # Handle different file formats
    if latest_conversation.suffix == '.jsonl':
        # Read JSONL format (multiple JSON objects, one per line)
        conversation_data = []
        with open(latest_conversation) as f:
            for line in f:
                if line.strip():
                    conversation_data.append(json.loads(line))
        return {"conversation_steps": conversation_data}
    else:
        # Read regular JSON
        with open(latest_conversation) as f:
            return json.load(f)


def extract_raw_preferences(conversation_data: dict) -> dict:
    """Extract raw text preferences from conversation data."""

    # Check if this is a complete session format
    if "processed_preferences" in conversation_data:
        processed_prefs = conversation_data["processed_preferences"]
        raw_preferences = {}
        for key, value in processed_prefs.items():
            if isinstance(value, dict) and "text" in value:
                raw_preferences[key] = value["text"]
            else:
                raw_preferences[key] = str(value)
        return raw_preferences

    # Check if this is conversation steps format
    elif "conversation_steps" in conversation_data:
        # Extract final answers from conversation steps
        raw_preferences = {}
        for step in conversation_data["conversation_steps"]:
            if "question_id" in step and "answer" in step:
                raw_preferences[step["question_id"]] = step["answer"]
        return raw_preferences

    # Fallback: use hardcoded preferences from your conversation
    else:
        print("⚠️ Unknown conversation format, using hardcoded preferences")
        return {
            "destination": "rome, italy",
            "travel_dates": "october 2 to october 8, 2025",
            "trip_purpose": "buisiness",
            "budget_preference": "$240 a night",
            "amenities_features": "room service, gym, and restaurants can walk to",
            "stay_experience": "historic is great"
        }


def test_parameter_extraction(raw_preferences: dict):
    """Test LLM parameter extraction."""
    print("\n🧪 Testing LLM Parameter Extraction")
    print("=" * 50)

    print("Input preferences:")
    for key, value in raw_preferences.items():
        if key in ["destination", "travel_dates"]:
            print(f"  {key}: {value}")

    try:
        params = extract_search_parameters(raw_preferences)
        print(f"\n✅ Extracted parameters:")
        print(f"  Location: {params['location']}")
        print(f"  Check-in: {params['check_in']}")
        print(f"  Check-out: {params['check_out']}")
        return params

    except Exception as e:
        print(f"❌ Parameter extraction failed: {str(e)}")
        return None


def test_hotel_search(search_params: dict, use_mock: bool = True):
    """Test hotel search (with optional mocking)."""
    print(f"\n🏨 Testing Hotel Search {'(MOCKED)' if use_mock else '(LIVE)'}")
    print("=" * 50)

    if use_mock:
        # Mock hotel search for testing without API calls
        print("🔄 Mocking hotel search...")
        mock_hotels = [
            {
                "name": f"Sample Hotel {i+1}",
                "place_id": f"mock_id_{i+1}",
                "address": f"Sample Address {i+1}, {search_params['location']}",
                "rating": 4.0 + (i * 0.1),
                "user_rating_count": 100 + (i * 50),
                "check_in": search_params["check_in"],
                "check_out": search_params["check_out"]
            }
            for i in range(5)  # Return 5 mock hotels
        ]

        print(f"✅ Found {len(mock_hotels)} mock hotels:")
        for hotel in mock_hotels:
            print(f"  • {hotel['name']} - {hotel['rating']}⭐ - {hotel['address']}")

        return mock_hotels

    else:
        # Live hotel search
        api_key = os.getenv("GOOGLE_MAPS_API_KEY_TEST")
        if not api_key:
            print("❌ No Google Maps API key found. Set GOOGLE_MAPS_API_KEY_TEST environment variable.")
            return None

        try:
            client = HotelSearchClient(api_key)
            hotels = client.search_hotels(
                location=search_params["location"],
                check_in=search_params["check_in"],
                check_out=search_params["check_out"],
                max_results=20
            )

            print(f"✅ Found {len(hotels)} real hotels:")
            for hotel in hotels[:5]:  # Show first 5
                rating = f"{hotel['rating']}⭐" if hotel['rating'] else "No rating"
                print(f"  • {hotel['name']} - {rating} - {hotel['address']}")

            if len(hotels) > 5:
                print(f"  ... and {len(hotels) - 5} more hotels")

            return hotels

        except Exception as e:
            print(f"❌ Hotel search failed: {str(e)}")
            return None


def test_full_integration(raw_preferences: dict, use_mock: bool = True):
    """Test the complete integration pipeline."""
    print(f"\n🔗 Testing Full Integration Pipeline {'(MOCKED)' if use_mock else '(LIVE)'}")
    print("=" * 50)

    try:
        if use_mock:
            # Test with mock hotel client
            class MockHotelClient:
                def search_hotels(self, location, check_in, check_out, radius_km=5.0, max_results=20):
                    return [
                        {
                            "name": f"Integrated Hotel {i+1}",
                            "place_id": f"integrated_id_{i+1}",
                            "address": f"Address {i+1}, {location}",
                            "rating": 4.0 + (i * 0.2),
                            "user_rating_count": 200 + (i * 25),
                            "check_in": check_in,
                            "check_out": check_out
                        }
                        for i in range(3)
                    ]

            mock_client = MockHotelClient()
            hotels = search_hotels_from_preferences(raw_preferences, mock_client)

        else:
            # Test with real hotel client
            api_key = os.getenv("GOOGLE_MAPS_API_KEY_TEST")
            if not api_key:
                print("❌ No API key for live integration test")
                return None

            client = HotelSearchClient(api_key)
            hotels = search_hotels_from_preferences(raw_preferences, client)

        print(f"✅ Integration successful! Found {len(hotels)} hotels:")
        for hotel in hotels:
            rating = f"{hotel['rating']}⭐" if hotel['rating'] else "No rating"
            print(f"  • {hotel['name']} - {rating}")

        # Show what data is ready for frontier LLM
        print(f"\n📋 Data ready for frontier LLM analysis:")
        print(f"  - {len(hotels)} hotels with names, ratings, addresses")
        print(f"  - Original preferences: {len(raw_preferences)} answers")
        print(f"  - Check-in/out dates extracted and validated")

        return hotels

    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return None


def main():
    """Run all search pipeline tests."""
    print("🔍 Search Pipeline Test")
    print("=" * 60)

    try:
        # Load conversation data
        conversation_data = load_latest_conversation()
        raw_preferences = extract_raw_preferences(conversation_data)

        print(f"📊 Session contains {len(raw_preferences)} preferences")

        # Test 1: Parameter extraction
        search_params = test_parameter_extraction(raw_preferences)
        if not search_params:
            print("❌ Cannot continue without valid search parameters")
            return

        # Test 2: Hotel search (mocked by default)
        use_live_search = "--live" in sys.argv
        hotels = test_hotel_search(search_params, use_mock=not use_live_search)

        # Test 3: Full integration
        integrated_hotels = test_full_integration(raw_preferences, use_mock=not use_live_search)

        # Summary
        print(f"\n📈 Test Summary")
        print("=" * 30)
        if search_params:
            print("✅ Parameter extraction: PASSED")
        if hotels:
            print("✅ Hotel search: PASSED")
        if integrated_hotels:
            print("✅ Full integration: PASSED")
            print(f"\n🎯 Ready for frontier LLM with {len(integrated_hotels)} hotels!")

        if not use_live_search:
            print(f"\n💡 To test with real Google Maps API:")
            print(f"   export GOOGLE_MAPS_API_KEY_TEST=your_key")
            print(f"   python {Path(__file__).name} --live")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
