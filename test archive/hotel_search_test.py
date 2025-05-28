#!/usr/bin/env python3
"""
Updated Google Maps Hotel Search Test
Returns up to 50 hotels with pricing for specific dates (Aug 1-8, 2025)
"""

import googlemaps
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

class HotelSearchClient:
    def __init__(self, api_key: str):
        """Initialize Google Maps client."""
        self.client = googlemaps.Client(key=api_key)

    def search_hotels_with_pricing(
        self,
        location: str,
        radius_km: float = 5.0,
        check_in: str = "2025-08-01",
        check_out: str = "2025-08-08",
        max_results: int = 50
    ) -> Tuple[List[Dict], Dict]:
        """
        Search for hotels with pricing for specific dates.

        Args:
            location: Location string or "lat,lng"
            radius_km: Search radius in kilometers
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            max_results: Maximum hotels to return

        Returns:
            Tuple of (hotels list, metadata dict)
        """
        try:
            # Geocode if location is not coordinates
            if not self._is_coordinates(location):
                geocode_result = self.client.geocode(location)
                if not geocode_result:
                    raise Exception(f"Could not geocode location: {location}")

                lat = geocode_result[0]['geometry']['location']['lat']
                lng = geocode_result[0]['geometry']['location']['lng']
                print(f"📍 Geocoded '{location}' to ({lat}, {lng})")
            else:
                lat, lng = map(float, location.split(','))

            # Search for hotels using Places API (New)
            print(f"🔍 Searching for hotels near {location} (radius: {radius_km}km)")
            print(f"📅 Dates: {check_in} to {check_out}")

            hotels = []
            next_page_token = None
            search_count = 0

            while len(hotels) < max_results and search_count < 3:  # Limit API calls
                # Use the correct Places API method
                if next_page_token:
                    response = self.client.places_nearby(
                        location=(lat, lng),
                        radius=radius_km * 1000,
                        type='lodging',
                        page_token=next_page_token
                    )
                else:
                    response = self.client.places_nearby(
                        location=(lat, lng),
                        radius=radius_km * 1000,
                        type='lodging'
                    )

                if not response.get('results'):
                    break

                print(f"🔍 Found {len(response['results'])} hotels in batch {search_count + 1}")

                # Process results
                for place in response['results']:
                    if len(hotels) >= max_results:
                        break

                    hotel_data = self._process_hotel_result(place, check_in, check_out)
                    if hotel_data:
                        hotels.append(hotel_data)

                # Check for next page
                next_page_token = response.get('next_page_token')
                search_count += 1

                if not next_page_token:
                    break

                # Add delay between paginated requests (required by Google API)
                if next_page_token:
                    import time
                    time.sleep(2)

            # Sort by rating and availability
            hotels.sort(key=lambda h: (
                h.get('has_pricing_info', False),  # Prioritize hotels with pricing
                h.get('rating', 0)
            ), reverse=True)

            metadata = {
                'total_found': len(hotels),
                'search_location': location,
                'radius_km': radius_km,
                'check_in': check_in,
                'check_out': check_out,
                'hotels_with_pricing': sum(1 for h in hotels if h.get('has_pricing_info')),
                'search_timestamp': datetime.now().isoformat()
            }

            return hotels, metadata

        except Exception as e:
            print(f"❌ Error searching {location}: {str(e)}")
            return [], {'error': str(e)}

    def _is_coordinates(self, location: str) -> bool:
        """Check if location string is coordinates."""
        try:
            parts = location.split(',')
            return len(parts) == 2 and all(self._is_float(p.strip()) for p in parts)
        except:
            return False

    def _is_float(self, value: str) -> bool:
        """Check if string can be converted to float."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _process_hotel_result(self, place: Dict, check_in: str, check_out: str) -> Optional[Dict]:
        """Process a single hotel result."""
        try:
            hotel_info = {
                'name': place.get('name', 'Unknown Hotel'),
                'place_id': place.get('place_id', ''),
                'address': place.get('vicinity', 'Address not available'),
                'rating': place.get('rating'),
                'user_rating_count': place.get('user_ratings_total', 0),
                'check_in': check_in,
                'check_out': check_out,
                'has_pricing_info': False,
                'pricing_data': None
            }

            # Try to get pricing information
            # Note: Google Maps API doesn't directly provide hotel pricing
            # You'd typically need to integrate with booking APIs like:
            # - Booking.com API
            # - Expedia API
            # - Hotel.com API
            # For now, we'll simulate this with a placeholder

            pricing_info = self._get_hotel_pricing_placeholder(
                hotel_info['place_id'],
                check_in,
                check_out
            )

            if pricing_info:
                hotel_info['pricing_data'] = pricing_info
                hotel_info['has_pricing_info'] = True

            return hotel_info

        except Exception as e:
            print(f"⚠️ Error processing hotel: {str(e)}")
            return None

    def _get_hotel_pricing_placeholder(self, place_id: str, check_in: str, check_out: str) -> Optional[Dict]:
        """
        Placeholder for hotel pricing data.
        In production, this would call booking APIs.
        """
        # Simulate pricing data for demonstration
        # In reality, you'd call booking.com, expedia, etc. APIs here

        import random

        # Randomly simulate if pricing is available (70% chance)
        if random.random() < 0.7:
            base_price = random.randint(80, 400)
            nights = 7  # Aug 1-8 is 7 nights

            return {
                'total_price': base_price * nights,
                'price_per_night': base_price,
                'currency': 'USD',
                'nights': nights,
                'booking_source': 'placeholder_api',
                'last_updated': datetime.now().isoformat()
            }

        return None


def format_hotel_results(hotels: List[Dict], metadata: Dict) -> None:
    """Format and display hotel results."""
    print(f"\n🏨 Found {len(hotels)} hotels:")
    print("=" * 80)

    hotels_with_pricing = [h for h in hotels if h.get('has_pricing_info')]
    hotels_without_pricing = [h for h in hotels if not h.get('has_pricing_info')]

    # Display hotels with pricing first
    if hotels_with_pricing:
        print(f"\n💰 Hotels with pricing ({len(hotels_with_pricing)}):")
        print("-" * 50)

        for i, hotel in enumerate(hotels_with_pricing, 1):
            print(f"{i}. {hotel['name']}")
            print(f"   📍 {hotel['address']}")
            if hotel['rating']:
                print(f"   ⭐ Rating: {hotel['rating']}/5")

            pricing = hotel.get('pricing_data', {})
            if pricing:
                print(f"   💵 ${pricing['price_per_night']}/night × {pricing['nights']} nights = ${pricing['total_price']} total")

            print(f"   📅 {hotel['check_in']} to {hotel['check_out']}")
            print()

    # Display hotels without pricing
    if hotels_without_pricing:
        print(f"\n🏨 Hotels without pricing data ({len(hotels_without_pricing)}):")
        print("-" * 50)

        for i, hotel in enumerate(hotels_without_pricing, 1):
            print(f"{i}. {hotel['name']}")
            print(f"   📍 {hotel['address']}")
            if hotel['rating']:
                print(f"   ⭐ Rating: {hotel['rating']}/5")
            print(f"   📅 {hotel['check_in']} to {hotel['check_out']} (pricing unavailable)")
            print()


def main():
    """Main test function."""
    import os

    # Get API key from environment variable
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY_TEST")

    if not API_KEY:
        print("❌ Please export GOOGLE_MAPS_API_KEY_TEST environment variable")
        print("   Example: export GOOGLE_MAPS_API_KEY_TEST=your_api_key_here")
        return

    search_client = HotelSearchClient(API_KEY)

    print("🗺️ Google Maps Hotel Search Test with Pricing")
    print("=" * 50)

    # Test locations
    test_locations = [
        "Manhattan, New York, NY",
        "Las Vegas, NV",
        "40.7589,-73.9851"  # NYC coordinates
    ]

    for location in test_locations:
        print(f"\n{'=' * 60}")
        print(f"Testing location: {location}")
        print("=" * 60)

        hotels, metadata = search_client.search_hotels_with_pricing(
            location=location,
            radius_km=5.0,
            check_in="2025-08-01",
            check_out="2025-08-08",
            max_results=50
        )

        if hotels:
            format_hotel_results(hotels, metadata)

            # Create simple list for LLM analysis
            simple_hotel_list = []
            for hotel in hotels:
                pricing_data = hotel.get('pricing_data')
                total_price = pricing_data.get('total_price') if pricing_data else 'Not available'

                hotel_summary = {
                    'name': hotel['name'],
                    'dates': f"{hotel['check_in']} to {hotel['check_out']}",
                    'pricing': total_price
                }
                simple_hotel_list.append(hotel_summary)

            print(f"\n📋 Simple list for LLM analysis:")
            print(json.dumps(simple_hotel_list[:10], indent=2))  # Show first 10

        else:
            print(f"❌ No hotels found for {location}")

    print(f"\n💡 Next Steps:")
    print("- Integrate with booking APIs (Booking.com, Expedia) for real pricing")
    print("- Pass the simple hotel list to Claude Sonnet 4 for preference matching")
    print("- Combine with your preference gathering system")


if __name__ == "__main__":
    main()
