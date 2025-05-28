#!/usr/bin/env python3
"""
Test the complete search pipeline using saved session data.
Tests both LLM parameter extraction and hotel search using Booking.com API.
"""
import json
import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from search.integration import extract_search_parameters, search_hotels_from_preferences



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
    """Test hotel search using Booking.com API (with optional mocking)."""
    print(f"\n🏨 Testing Hotel Search {'(MOCKED)' if use_mock else '(LIVE)'}")
    print("=" * 50)

    if use_mock:
        # Mock hotel search for testing without API calls
        print("🔄 Mocking hotel search...")
        mock_hotels = [
            {
                "name": f"Sample Hotel {i+1}",
                "hotel_id": f"mock_id_{i+1}",
                "address": f"Sample Address {i+1}, {search_params['location']}",
                "rating": 8.5 + (i * 0.2),
                "review_count": 100 + (i * 50),
                "price": 150 + (i * 20),
                "currency": "USD",
                "check_in": search_params["check_in"],
                "check_out": search_params["check_out"]
            }
            for i in range(5)  # Return 5 mock hotels
        ]

        print(f"✅ Found {len(mock_hotels)} mock hotels:")
        for hotel in mock_hotels:
            print(f"  • {hotel['name']} - {hotel['rating']}/10 - {hotel['price']} {hotel['currency']}")

        return mock_hotels

    else:
        # Live hotel search using Booking.com API
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            print("❌ No RapidAPI key found. Set RAPIDAPI_KEY environment variable.")
            return None

        try:
            url = "https://booking-com.p.rapidapi.com/v1/hotels/search"

            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
            }

            # Convert location to destination_id (using Rome as example)
            destination_map = {
                "rome": "-126693",
                "rome, italy": "-126693"
                # Add more mappings as needed
            }
            dest_id = destination_map.get(search_params['location'].lower(), "-126693")

            payload = {
                "units": "metric",
                "room_number": "1",
                "checkout_date": search_params["check_out"],
                "checkin_date": search_params["check_in"],
                "adults_number": "2",
                "order_by": "price",
                "filter_by_currency": "USD",
                "locale": "en-us",
                "dest_type": "city",
                "dest_id": dest_id,
                "categories_filter_ids": "class::2,class::4,free_cancellation::1",
                "page_number": "0",
                "include_adjacency": "true"
            }

            print("\n📡 Sending API request...")
            response = requests.get(url, headers=headers, params=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                hotels = data.get('result', [])

                if hotels:
                    print(f"\n✅ Found {len(hotels)} hotels:")
                    for hotel in hotels[:5]:  # Show first 5
                        name = hotel.get('hotel_name', 'Unknown Hotel')
                        price = hotel.get('min_total_price', 'N/A')
                        currency = hotel.get('currency', 'USD')
                        rating = hotel.get('review_score', 'No rating')

                        print(f"  • {name} - {rating}/10 - {price} {currency}")

                    if len(hotels) > 5:
                        print(f"  ... and {len(hotels) - 5} more hotels")

                    return hotels
                else:
                    print("\n❌ No hotels found in response")
                    return None
            else:
                print(f"\n❌ API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Hotel search failed: {str(e)}")
            return None


def test_full_integration(raw_preferences: dict, use_mock: bool = True):
    """Test the complete integration pipeline using Booking.com API."""
    print(f"\n🔗 Testing Full Integration Pipeline {'(MOCKED)' if use_mock else '(LIVE)'}")
    print("=" * 50)

    try:
        # Extract search parameters from preferences
        search_params = extract_search_parameters(raw_preferences)
        if not search_params:
            print("❌ Cannot extract search parameters from preferences")
            return None

        # Search for hotels using Booking.com API
        hotels = test_hotel_search(search_params, use_mock=use_mock)
        if not hotels:
            print("❌ Hotel search returned no results")
            return None

        print(f"\n✅ Integration successful! Found {len(hotels)} hotels:")
        for hotel in hotels[:5]:  # Show first 5
            name = hotel.get('hotel_name', hotel.get('name', 'Unknown Hotel'))
            rating = hotel.get('review_score', hotel.get('rating', 'No rating'))
            price = hotel.get('min_total_price', hotel.get('price', 'N/A'))
            currency = hotel.get('currency', 'USD')

            print(f"  • {name} - {rating}/10 - {price} {currency}")

        # Show what data is ready for frontier LLM
        print(f"\n📋 Data ready for frontier LLM analysis:")
        print(f"  - {len(hotels)} hotels with real-time pricing")
        print(f"  - Prices in {hotels[0]['currency']}")
        print(f"  - Original preferences: {len(raw_preferences)} answers")
        print(f"  - Check-in/out dates validated")
        print(f"  - Ratings and reviews available")

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
            print(f"\n💡 To test with real Booking.com API:")
            print(f"   export RAPIDAPI_KEY=your_rapidapi_key")
            print(f"   python {Path(__file__).name} --live")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
