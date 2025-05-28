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

    def _get_hotel_pricing(self, location: str, hotels: List[Dict], check_in: str, check_out: str) -> None:
        """Get real pricing from Booking.com API for multiple hotels."""
        import requests
        import os
        from datetime import datetime
        
        print("\n💰 Starting price lookup for hotels...")

        # Get API key from environment or use default test key
        rapidapi_key = os.getenv("RAPIDAPI_KEY", "e3f0e954fbmsh9c1492cd7d84c3dp15a808jsn5f0c61cca308")

        try:
            # Use Booking.com API endpoint
            url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"

            headers = {
                "X-RapidAPI-Key": rapidapi_key,
                "X-RapidAPI-Host": "booking-com15.p.rapidapi.com",
                "content-type": "application/json"
            }

            # Calculate nights for price per night calculation
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (check_out_date - check_in_date).days

            # Extract lat/lng from first hotel that has them
            lat = lng = None
            for hotel in hotels:
                if 'location' in hotel and isinstance(hotel['location'], dict):
                    lat = hotel['location'].get('lat')
                    lng = hotel['location'].get('lng')
                    if lat and lng:
                        break

            if not (lat and lng):
                raise Exception("No valid coordinates found in hotel data")

            # Search parameters for Booking.com
            params = {
                "dest_id": "-126693",  # Rome's dest_id
                "dest_type": "city",
                "arrival_date": check_in,
                "departure_date": check_out,
                "adults": "2",
                "room_qty": "1",
                "children_qty": "0",
                "search_type": "city",
                "offset": "0",
                "currency": "USD",
                "categories_filter": "class::2,class::4,class::5",  # 2+ star hotels
                "languagecode": "en-us",
                "page_number": "1",
                "sort_by": "popularity",
                "guest_qty": "2"
            }

            print(f"🔍 Searching for hotels in {location}")
            response = requests.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                properties = data.get('result', [])
                
                # Create a mapping of hotel names to their pricing data
                pricing_map = {}
                for prop in properties:
                    name = prop.get('hotel_name', '').lower()
                    
                    try:
                        min_price = float(prop.get('min_total_price', 0))
                        if min_price > 0:
                            price_per_night = min_price / nights if nights > 0 else 0
                            
                            pricing_map[name] = {
                                "total_price": min_price,
                                "price_per_night": round(price_per_night, 2),
                                "currency": prop.get('currency_code', 'USD'),
                                "nights": nights,
                                "booking_source": "booking_com_api",
                                "hotel_id": prop.get('hotel_id')
                            }
                            print(f"💵 Found price for {name}: ${min_price}")
                    except (ValueError, TypeError, AttributeError) as e:
                        print(f"⚠️ Error processing price for {name}: {str(e)}")

                # Update hotels with pricing data if available
                matches = 0
                for hotel in hotels:
                    hotel_name = hotel.get('name', '').lower()
                    if hotel_name in pricing_map:
                        hotel['pricing_data'] = pricing_map[hotel_name]
                        hotel['has_pricing_info'] = True
                        matches += 1
                    else:
                        hotel['pricing_data'] = self._get_mock_pricing(check_in, check_out, hotel.get('rating'))
                        hotel['has_pricing_info'] = False
                print(f"✓ Matched prices for {matches} out of {len(hotels)} hotels")

        except Exception as e:
            print(f"⚠️ Expedia API error: {str(e)}")
            # Try fuzzy matching hotel names and apply pricing
            from difflib import SequenceMatcher

            def similar(a, b):
                return SequenceMatcher(None, a.lower(), b.lower()).ratio()

            for hotel in hotels:
                hotel_name = hotel['name'].lower()
                best_match = None
                best_ratio = 0
                
                for booking_name in pricing_map:
                    ratio = similar(hotel_name, booking_name)
                    if ratio > 0.8 and ratio > best_ratio:  # 80% similarity threshold
                        best_match = booking_name
                        best_ratio = ratio
                
                if best_match:
                    hotel['pricing_data'] = pricing_map[best_match]
                    hotel['has_pricing_info'] = True
                    print(f"✓ Matched {hotel_name} to {best_match} (similarity: {best_ratio:.2%})")
                else:
                    hotel['pricing_data'] = self._get_mock_pricing(check_in, check_out, hotel.get('rating'))
                    hotel['has_pricing_info'] = False
                    print(f"⚠️ No match found for {hotel_name}, using mock pricing")

    def _get_mock_pricing(self, check_in: str, check_out: str, hotel_rating: float = None) -> Dict:
        """Generate realistic mock pricing data for testing based on hotel rating."""
        from datetime import datetime
        import random
        
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        
        # Base price ranges based on rating
        price_ranges = {
            5: (250, 800),    # 5 star hotels
            4: (150, 400),    # 4 star hotels
            3: (80, 200),     # 3 star hotels
            2: (50, 120),     # 2 star hotels
            1: (30, 80),      # 1 star hotels
            None: (70, 300)   # Unknown rating
        }
        
        # Get appropriate price range based on rating
        rating_key = round(hotel_rating) if hotel_rating else None
        min_price, max_price = price_ranges.get(rating_key, price_ranges[None])
        
        # Generate slightly random price within range
        price_per_night = round(random.uniform(min_price, max_price), 2)
        total_price = round(price_per_night * nights, 2)
        
        return {
            "total_price": total_price,
            "price_per_night": price_per_night,
            "currency": "USD",
            "nights": nights,
            "booking_source": "mock_data",
            "confidence": "low"
        }
        
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
            print("\n🔍 Starting hotel search...")

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

                    print(f"\n📍 Raw place data: {place}")
                    location_data = place.get('geometry', {}).get('location', {})
                    hotel_data = {
                        'name': place.get('name', 'Unknown Hotel'),
                        'place_id': place.get('place_id', ''),
                        'address': place.get('vicinity', ''),
                        'rating': place.get('rating'),
                        'user_rating_count': place.get('user_ratings_total', 0),
                        'check_in': check_in,
                        'check_out': check_out,
                        'location': {
                            'lat': location_data.get('lat'),
                            'lng': location_data.get('lng')
                        }
                    }
                    print(f"🏨 Processed hotel data: {hotel_data}")

                    hotels.append(hotel_data)  # Add the hotel to the list

                # Get pricing data for all hotels in one batch
                if hotels:
                    print(f"\n💰 Getting pricing for {len(hotels)} hotels...")
                    self._get_hotel_pricing(location, hotels, check_in, check_out)
                    print("\n📊 Hotels with pricing:")
                    for hotel in hotels:
                        print(f"  - {hotel['name']}: {hotel.get('pricing_data', 'No pricing')} (Has real pricing: {hotel.get('has_pricing_info', False)})")

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
