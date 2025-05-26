#!/usr/bin/env python3
"""
Clean Google Maps Hotel Search Client
"""
import googlemaps
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class HotelSearchClient:
    def __init__(self, api_key: str):
        """Initialize Google Maps client."""
        self.client = googlemaps.Client(key=api_key)

def _get_booking_pricing(self, place_id: str, location: str, check_in: str, check_out: str) -> Optional[Dict]:
    """Get real pricing from Booking.com API."""
    import requests
    from datetime import datetime

    # Your RapidAPI key
    rapidapi_key = "e3f0e954fbmsh9c1492cd7d84c3dp15a808jsn5f0c61cca308"  # Replace with your actual key

    try:
        # Booking.com API endpoint for hotel search
        url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"

        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
        }

        # Calculate nights
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days

        # API parameters
        params = {
            "dest_id": location,  # You might need to convert location to dest_id
            "search_type": "city",
            "arrival_date": check_in,
            "departure_date": check_out,
            "adults": "1",
            "children_age": "",
            "room_qty": "1",
            "page_number": "1",
            "languagecode": "en-us",
            "currency_code": "USD"
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Extract pricing from the first available hotel
            if data.get("data") and len(data["data"]) > 0:
                hotel_data = data["data"][0]
                price_per_night = hotel_data.get("min_total_price", 0) / nights if nights > 0 else 0

                return {
                    "total_price": hotel_data.get("min_total_price", 0),
                    "price_per_night": round(price_per_night, 2),
                    "currency": hotel_data.get("currency", "USD"),
                    "nights": nights,
                    "booking_source": "booking_com_api"
                }

    except Exception as e:
        print(f"⚠️ Booking API error: {str(e)}")

    return None

    def search_hotels(
        self,
        location: str,
        check_in: str,
        check_out: str,
        radius_km: float = 5.0,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search for hotels with basic info.

        Args:
            location: Location string or "lat,lng"
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            radius_km: Search radius in kilometers
            max_results: Maximum hotels to return

        Returns:
            List of hotel dictionaries with name, place_id, address, rating
        """
        try:
            # Geocode if needed
            if not self._is_coordinates(location):
                geocode_result = self.client.geocode(location)
                if not geocode_result:
                    raise Exception(f"Could not geocode location: {location}")
                lat = geocode_result[0]['geometry']['location']['lat']
                lng = geocode_result[0]['geometry']['location']['lng']
            else:
                lat, lng = map(float, location.split(','))

            # Search for hotels
            hotels = []
            next_page_token = None
            search_count = 0

            while len(hotels) < max_results and search_count < 3:
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

                for place in response['results']:
                    if len(hotels) >= max_results:
                        break

                    hotel_data = {
                        'name': place.get('name', 'Unknown Hotel'),
                        'place_id': place.get('place_id', ''),
                        'address': place.get('vicinity', ''),
                        'rating': place.get('rating'),
                        'user_rating_count': place.get('user_ratings_total', 0),
                        'check_in': check_in,
                        'check_out': check_out
                    }

                    # Try to get real pricing
                    pricing_data = self._get_booking_pricing(
                        hotel_data['place_id'],
                        location,
                        check_in,
                        check_out
                    )

                    if pricing_data:
                        hotel_data['pricing_data'] = pricing_data
                        hotel_data['has_pricing_info'] = True
                    else:
                        # Fallback to mock pricing if API fails
                        hotel_data['pricing_data'] = self._get_mock_pricing(check_in, check_out)
                        hotel_data['has_pricing_info'] = False  # Mark as fallback

                next_page_token = response.get('next_page_token')
                search_count += 1

                if not next_page_token:
                    break

                if next_page_token:
                    import time
                    time.sleep(2)

            return hotels

        except Exception as e:
            raise Exception(f"Error searching {location}: {str(e)}")

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
