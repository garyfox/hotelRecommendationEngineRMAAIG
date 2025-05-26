#!/usr/bin/env python3
"""
Test script for Google Maps API hotel search functionality.
This script helps test the Google Places API for finding hotels with pricing info.
"""
import os
import json
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Hotel:
    """Data class for hotel information."""
    name: str
    place_id: str
    address: str
    rating: Optional[float] = None
    price_level: Optional[str] = None  # Changed from int to str to handle both formats
    types: List[str] = None
    location: Optional[Dict] = None  # lat/lng


class GoogleMapsHotelSearch:
    """Simple Google Maps API client for hotel searches."""

    def __init__(self, api_key: str):
        """
        Initialize the Google Maps client.

        Args:
            api_key: Your Google Maps API key
        """
        self.api_key = api_key
        self.base_url = "https://places.googleapis.com/v1/places"

    def search_hotels_nearby(
        self,
        location: str,
        radius_km: float = 5.0,
        max_results: int = 20
    ) -> Tuple[List[Hotel], Dict]:
        """
        Search for hotels near a location.

        Args:
            location: Location string (e.g., "New York, NY" or "latitude,longitude")
            radius_km: Search radius in kilometers (max 50km for Places API)
            max_results: Maximum number of results to return (max 20 per request)

        Returns:
            Tuple[List[Hotel], Dict]: List of hotels and raw API response metadata
        """
        # First, we need to geocode the location if it's not coordinates
        lat, lng = self._geocode_location(location)

        if lat is None or lng is None:
            raise ValueError(f"Could not geocode location: {location}")

        # Convert km to meters (API expects meters)
        radius_meters = int(radius_km * 1000)

        # Ensure radius doesn't exceed API limit (50km = 50000m)
        radius_meters = min(radius_meters, 50000)

        # Prepare the search request
        url = f"{self.base_url}:searchNearby"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.types,places.location,places.id"
        }

        payload = {
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": radius_meters
                }
            },
            "includedTypes": ["lodging"],  # This targets hotels, motels, B&Bs, etc.
            "maxResultCount": max_results
        }

        try:
            print(f"🔍 Searching for hotels near {location} (radius: {radius_km}km)...")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            hotels = self._parse_hotel_results(data.get("places", []))

            # Return hotels and some metadata
            metadata = {
                "search_location": {"lat": lat, "lng": lng},
                "radius_km": radius_km,
                "total_results": len(hotels),
                "api_response_size": len(str(data))
            }

            return hotels, metadata

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def _geocode_location(self, location: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert a location string to latitude/longitude coordinates.

        Args:
            location: Location string or "lat,lng"

        Returns:
            Tuple[Optional[float], Optional[float]]: (latitude, longitude) or (None, None)
        """
        # Check if it's already coordinates
        if "," in location and location.replace(",", "").replace(".", "").replace("-", "").isdigit():
            try:
                lat, lng = map(float, location.split(","))
                return lat, lng
            except ValueError:
                pass

        # Use Geocoding API
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": location,
            "key": self.api_key
        }

        try:
            response = requests.get(geocode_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "OK" and data["results"]:
                result = data["results"][0]
                lat = result["geometry"]["location"]["lat"]
                lng = result["geometry"]["location"]["lng"]
                print(f"📍 Geocoded '{location}' to ({lat}, {lng})")
                return lat, lng
            else:
                print(f"❌ Geocoding failed: {data.get('status', 'Unknown error')}")
                return None, None

        except requests.exceptions.RequestException as e:
            print(f"❌ Geocoding request failed: {str(e)}")
            return None, None

    def _parse_hotel_results(self, places: List[Dict]) -> List[Hotel]:
        """
        Parse the API response into Hotel objects.

        Args:
            places: List of place objects from API response

        Returns:
            List[Hotel]: Parsed hotel objects
        """
        hotels = []

        for place in places:
            try:
                # Debug: print the raw price level to see what we're getting
                raw_price_level = place.get("priceLevel")
                print(f"DEBUG: Raw price level from API: {raw_price_level} (type: {type(raw_price_level)})")

                hotel = Hotel(
                    name=place.get("displayName", {}).get("text", "Unknown"),
                    place_id=place.get("id", ""),
                    address=place.get("formattedAddress", ""),
                    rating=place.get("rating"),
                    price_level=raw_price_level,  # Store exactly what API returns
                    types=place.get("types", []),
                    location=place.get("location")
                )
                hotels.append(hotel)
            except Exception as e:
                print(f"⚠️  Error parsing hotel data: {e}")
                print(f"⚠️  Place data: {place}")
                continue

        return hotels


def print_hotel_results(hotels: List[Hotel], metadata: Dict):
    """Pretty print the hotel search results."""
    print(f"\n🏨 Found {len(hotels)} hotels:")
    print("=" * 80)

    for i, hotel in enumerate(hotels, 1):
        print(f"\n{i}. {hotel.name}")
        print(f"   📍 {hotel.address}")

        if hotel.rating:
            print(f"   ⭐ Rating: {hotel.rating}/5")

        if hotel.price_level is not None:
            price_symbols = ["Free", "$", "$", "$$", "$$"]
            # Convert to int in case it's a string
            price_level = int(hotel.price_level) if isinstance(hotel.price_level, str) else hotel.price_level
            price_desc = price_symbols[price_level] if price_level < len(price_symbols) else "Unknown"
            print(f"   💰 Price Level: {price_desc} ({price_level}/4)")

        # Show some relevant types
        if hotel.types:
            relevant_types = [t for t in hotel.types if t in ["hotel", "lodging", "resort", "motel", "bed_and_breakfast"]]
            if relevant_types:
                print(f"   🏷️  Type: {', '.join(relevant_types)}")

    print(f"\n📊 Search Metadata:")
    print(f"   Location: {metadata['search_location']}")
    print(f"   Radius: {metadata['radius_km']}km")
    print(f"   API Response Size: {metadata['api_response_size']} chars")


def test_api_usage():
    """Test function to check API usage and costs."""

    # Get API key from environment variable
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        print("❌ Please set GOOGLE_MAPS_API_KEY environment variable")
        print("   Example: export GOOGLE_MAPS_API_KEY='your-api-key-here'")
        return

    # Initialize the search client
    search_client = GoogleMapsHotelSearch(api_key)

    # Test locations - feel free to modify these
    test_locations = [
        "Manhattan, New York, NY",
        "40.7589,-73.9851",  # Times Square coordinates
        # "Paris, France",  # Uncomment to test international
    ]

    for location in test_locations:
        try:
            print(f"\n{'='*60}")
            print(f"Testing location: {location}")

            # Search for hotels
            hotels, metadata = search_client.search_hotels_nearby(
                location=location,
                radius_km=3.0,  # 3km radius
                max_results=10   # Limit results
            )

            # Display results
            print_hotel_results(hotels, metadata)

            # API usage info
            print(f"\n💸 API Usage for this search:")
            print(f"   - Geocoding API: 1 request (if location wasn't coordinates)")
            print(f"   - Places API (Search Nearby): 1 request")
            print(f"   - Total cost: ~$0.017 (Geocoding $0.005 + Places $0.012)")

        except Exception as e:
            print(f"❌ Error searching {location}: {str(e)}")

    print(f"\n💡 API Limits & Costs (as of 2024):")
    print(f"   - Places API (New) Search Nearby: $12 per 1000 requests")
    print(f"   - Geocoding API: $5 per 1000 requests")
    print(f"   - Your estimated cost for 300 searches: ~$5.10")
    print(f"   - Monthly limit: Usually $200 free credit for new accounts")


if __name__ == "__main__":
    print("🗺️  Google Maps Hotel Search Test")
    print("=" * 40)

    test_api_usage()

    # Example of how to integrate with your existing preference system
    print(f"\n🔗 Integration Example:")
    print(f"   # You could call this from your main workflow like:")
    print(f"   # hotels, meta = search_client.search_hotels_nearby(")
    print(f"   #     location=preferences['destination'],")
    print(f"   #     radius_km=5.0")
    print(f"   # )")
