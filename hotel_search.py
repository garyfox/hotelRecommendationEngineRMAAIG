"""
Hotel search integration for the interview workflow.
Extracts city/dates from conversation and searches for hotels.
FIXED: Added missing locale parameter to API calls.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from pathlib import Path

from llm.ollama_client import get_ollama_client


class HotelSearcher:
    """Searches for hotels based on conversation data."""

    def __init__(self):
        self.client = get_ollama_client()
        self.api_key = os.getenv('RAPIDAPI_KEY')

    def search_hotels_for_session(self, session_dir: Path) -> bool:
        """
        Search for hotels based on conversation in session directory.

        Args:
            session_dir: Path to session directory

        Returns:
            bool: True if search was successful, False otherwise
        """
        try:
            # BYPASS THE CLASS METHOD - use embedded working function
            print("🚨 BYPASSING CLASS METHOD - USING EMBEDDED WORKING FUNCTION")

            def working_extract(session_dir: Path):
                """Working extraction function embedded directly."""
                conversation_file = session_dir / "conversation_only.txt"
                if not conversation_file.exists():
                    return None, None, None, None

                with open(conversation_file, 'r', encoding='utf-8') as f:
                    conversation = f.read()

                prompt = f"""
Extract the destination city, travel dates, and appropriate locale from this hotel conversation.

{conversation}

Return in this exact format:
CITY: [just the city name, like "Vail" or "Paris"]
CHECKIN: [YYYY-MM-DD format]
CHECKOUT: [YYYY-MM-DD format]
LOCALE: [appropriate locale code like "en-us", "fr-fr", "de-de", "es-es", "it-it", etc.]

For LOCALE, use:
- "en-us" for USA/Canada destinations
- "en-gb" for UK destinations
- "fr-fr" for France
- Default to "en-us" if country is unclear

If anything is unclear or missing, use NONE for that field.
"""

                response = self.client.generate(
                    prompt=prompt,
                    system_prompt="Extract city, dates, and locale for hotel search."
                )

                city = checkin = checkout = locale = None
                for line in response.strip().split('\n'):
                    line = line.strip()
                    if line.startswith('CITY:'):
                        city = line.split(':', 1)[1].strip()
                        city = city if city != 'NONE' else None
                    elif line.startswith('CHECKIN:'):
                        checkin = line.split(':', 1)[1].strip()
                        checkin = checkin if checkin != 'NONE' else None
                    elif line.startswith('CHECKOUT:'):
                        checkout = line.split(':', 1)[1].strip()
                        checkout = checkout if checkout != 'NONE' else None
                    elif line.startswith('LOCALE:'):
                        locale = line.split(':', 1)[1].strip()
                        locale = locale if locale != 'NONE' else None

                if not locale:
                    locale = "en-us"

                print(f"🚨 EMBEDDED FUNCTION RETURNING: ({city}, {checkin}, {checkout}, {locale})")
                return (city, checkin, checkout, locale)

            extraction_result = working_extract(session_dir)
            print(f"🚨 EMBEDDED RESULT: {extraction_result}")
            print(f"🚨 TYPE: {type(extraction_result)}, LENGTH: {len(extraction_result)}")

            city, checkin, checkout, locale = extraction_result
            print(f"🎯 Extracted: City='{city}', Check-in='{checkin}', Check-out='{checkout}', Locale='{locale}'")

            if not city or not checkin or not checkout:
                self._save_no_results(session_dir, "Could not extract city and dates from conversation")
                return False

            # Search for hotels
            hotels = self._search_booking_com(city, checkin, checkout, locale)
            print(f"🏨 Search result: {len(hotels)} hotels found")

            if not hotels:
                self._save_no_results(session_dir, f"No hotels found for {city} on {checkin} to {checkout}")
                return False

            # Save results
            self._save_results(session_dir, city, checkin, checkout, hotels, locale)
            return True

        except Exception as e:
            print(f"❌ Error during hotel search: {str(e)}")
            self._save_no_results(session_dir, f"Error during hotel search: {str(e)}")
            return False

    def _extract_conversation_data_FIXED(self, session_dir: Path) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Extract city, dates, and locale from conversation file."""
        print("🚨 CALLING THE FIXED VERSION OF _extract_from_conversation")

        conversation_file = session_dir / "conversation_only.txt"

        if not conversation_file.exists():
            return None, None, None, None

        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation = f.read()

        # Enhanced LLM call to extract city, dates, and locale
        prompt = f"""
Extract the destination city, travel dates, and appropriate locale from this hotel conversation.

{conversation}

Return in this exact format:
CITY: [just the city name, like "Vail" or "Paris"]
CHECKIN: [YYYY-MM-DD format]
CHECKOUT: [YYYY-MM-DD format]
LOCALE: [appropriate locale code like "en-us", "fr-fr", "de-de", "es-es", "it-it", etc.]

For LOCALE, use:
- "en-us" for USA/Canada destinations
- "en-gb" for UK destinations
- "fr-fr" for France
- "de-de" for Germany
- "es-es" for Spain
- "it-it" for Italy
- "ja-jp" for Japan
- "zh-cn" for China
- Default to "en-us" if country is unclear

If anything is unclear or missing, use NONE for that field.
"""

        response = self.client.generate(
            prompt=prompt,
            system_prompt="Extract city, dates, and locale for hotel search. Be precise with formats and choose appropriate locale based on destination country."
        )

        # Initialize all variables
        city = None
        checkin = None
        checkout = None
        locale = None

        # Parse LLM response
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('CITY:'):
                city = line.split(':', 1)[1].strip()
                city = city if city != 'NONE' else None
            elif line.startswith('CHECKIN:'):
                checkin = line.split(':', 1)[1].strip()
                checkin = checkin if checkin != 'NONE' else None
            elif line.startswith('CHECKOUT:'):
                checkout = line.split(':', 1)[1].strip()
                checkout = checkout if checkout != 'NONE' else None
            elif line.startswith('LOCALE:'):
                locale = line.split(':', 1)[1].strip()
                locale = locale if locale != 'NONE' else None

        # Auto-generate checkout if only checkin provided
        if checkin and not checkout:
            try:
                checkin_dt = datetime.strptime(checkin, '%Y-%m-%d')
                checkout_dt = checkin_dt + timedelta(days=2)
                checkout = checkout_dt.strftime('%Y-%m-%d')
                print(f"🗓️ Auto-generated checkout: {checkout}")
            except ValueError:
                pass

        # Set default locale if not provided
        if not locale:
            locale = "en-us"

        print(f"🚨 FIXED VERSION: Returning ({city}, {checkin}, {checkout}, {locale})")
        return (city, checkin, checkout, locale), locale

    def _search_booking_com(self, city: str, checkin: str, checkout: str, locale: str = "en-us") -> List[Dict]:
        """Search Booking.com for hotels."""
        if not self.api_key:
            print("⚠️ No RAPIDAPI_KEY found - cannot search hotels")
            return []

        # Get destination ID
        dest_id = self._get_destination_id(city, locale)
        print(f"🎯 Destination lookup: '{city}' -> ID: {dest_id} (locale: {locale})")

        if not dest_id:
            print(f"❌ Could not find destination ID for '{city}'")
            return []

        # Search hotels
        url = "https://booking-com.p.rapidapi.com/v1/hotels/search"

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
        }

        # Use the EXACT same parameters that work in test_booking_api.py
        params = {
            "units": "metric",
            "room_number": "1",
            "checkout_date": checkout,
            "checkin_date": checkin,
            "adults_number": "2",
            "order_by": "price",
            "filter_by_currency": "USD",
            "locale": locale,
            "dest_type": "city",
            "dest_id": dest_id,
            "categories_filter_ids": "class::2,class::4,free_cancellation::1",
            "page_number": "0",
            "include_adjacency": "true"
        }

        try:
            print(f"📡 Searching hotels for dest_id {dest_id}...")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            print(f"📡 API Response: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                hotels = data.get('result', [])
                print(f"✅ API returned {len(hotels)} hotels")

                # Format hotel data
                hotel_list = []

                # Calculate actual nights from our dates
                try:
                    checkin_dt = datetime.strptime(checkin, '%Y-%m-%d')
                    checkout_dt = datetime.strptime(checkout, '%Y-%m-%d')
                    actual_nights = (checkout_dt - checkin_dt).days
                    print(f"📅 Calculated nights: {actual_nights} ({checkin} to {checkout})")
                except:
                    actual_nights = 1  # Fallback

                for hotel in hotels[:40]:  # Limit to 40 hotels
                    price = hotel.get('min_total_price', 0)
                    api_nights = hotel.get('nights', actual_nights)  # API nights (might be wrong)

                    # Use our calculated nights for pricing
                    price_per_night = 0
                    if price and actual_nights:
                        try:
                            # If API gave us total price for different nights, recalculate
                            if api_nights and api_nights != actual_nights:
                                # API price might be for different duration
                                api_price_per_night = float(price) / api_nights
                                price_per_night = api_price_per_night
                                total_price = api_price_per_night * actual_nights
                                print(f"🔢 {hotel.get('hotel_name', 'Hotel')}: API nights={api_nights}, our nights={actual_nights}")
                            else:
                                price_per_night = float(price) / actual_nights
                                total_price = price
                        except:
                            price_per_night = 0
                            total_price = price
                    else:
                        total_price = price

                    hotel_list.append({
                        "name": hotel.get('hotel_name', ''),
                        "total_price": total_price,
                        "price_per_night": round(price_per_night, 0) if price_per_night else 0,
                        "currency": hotel.get('currency', 'USD'),
                        "rating": hotel.get('review_score', 0),
                        "nights": actual_nights  # Use our calculated nights
                    })

                return hotel_list
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Hotel search exception: {str(e)}")

        return []

    def _get_destination_id(self, city: str, locale: str = "en-us") -> Optional[str]:
        """Get Booking.com destination ID for city."""
        url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
        }

        # Try multiple variations of the city name
        search_variations = [
            city,
            f"{city}, Colorado" if "colorado" not in city.lower() else city,
            f"{city}, CO" if "co" not in city.lower() else city,
            f"{city}, USA" if "usa" not in city.lower() else city
        ]

        for search_term in search_variations:
            try:
                print(f"🔍 Trying destination lookup: '{search_term}'")

                # Use LLM-determined locale
                params = {
                    "name": search_term,
                    "locale": locale
                }

                response = requests.get(url, headers=headers, params=params, timeout=15)
                print(f"   Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        dest_id = str(data[0].get('dest_id'))
                        location_name = data[0].get('name', 'Unknown')
                        print(f"   ✅ Found: {location_name} (ID: {dest_id})")
                        return dest_id
                    else:
                        print(f"   ❌ No results for '{search_term}'")
                else:
                    print(f"   ❌ API Error: {response.text[:100]}")

            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")

        return None

    def _save_results(self, session_dir: Path, city: str, checkin: str, checkout: str, hotels: List[Dict], locale: str = "en-us") -> None:
        """Save hotel search results."""

        # Human-readable text file
        text_file = session_dir / "hotel_results.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"HOTEL SEARCH RESULTS\n")
            f.write(f"Location: {city}\n")
            f.write(f"Dates: {checkin} to {checkout}\n")
            f.write(f"Locale: {locale}\n")
            f.write(f"Found: {len(hotels)} hotels\n")
            f.write("=" * 50 + "\n\n")

            for i, hotel in enumerate(hotels, 1):
                name = hotel['name']
                price_per_night = hotel['price_per_night']
                total_price = hotel['total_price']
                rating = hotel['rating']
                nights = hotel.get('nights', 1)

                f.write(f"{i:2d}. {name}\n")
                if price_per_night:
                    f.write(f"    💰 ${price_per_night:.0f}/night × {nights} nights = ${total_price} total\n")
                if rating:
                    f.write(f"    ⭐ Rating: {rating}/10\n")
                f.write("\n")

        # JSON backup for future LLM consumption
        json_file = session_dir / "hotel_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "search_info": {
                    "city": city,
                    "checkin": checkin,
                    "checkout": checkout,
                    "locale": locale,
                    "hotels_found": len(hotels),
                    "searched_at": datetime.now().isoformat()
                },
                "hotels": hotels
            }, f, indent=2)

    def _save_no_results(self, session_dir: Path, reason: str) -> None:
        """Save when no results found."""
        text_file = session_dir / "hotel_results.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("HOTEL SEARCH RESULTS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"No hotels found.\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"\nDebugging info:\n")
            f.write(f"- Check if RAPIDAPI_KEY is set\n")
            f.write(f"- Verify destination exists in Booking.com\n")
            f.write(f"- Try running: python3 test_booking_api.py\n")


def search_hotels_for_session(session_dir: Path) -> bool:
    """
    Search for hotels for a given session.

    Args:
        session_dir: Path to session directory

    Returns:
        bool: True if search was successful
    """
    searcher = HotelSearcher()
    return searcher.search_hotels_for_session(session_dir)
