"""
Hotel search integration for the interview workflow.
Extracts city/dates from conversation and searches for hotels.
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
            # Extract city and dates from conversation
            city, checkin, checkout = self._extract_from_conversation(session_dir)

            if not city or not checkin or not checkout:
                self._save_no_results(session_dir, "Could not extract city and dates from conversation")
                return False

            # Search for hotels
            hotels = self._search_booking_com(city, checkin, checkout)

            if not hotels:
                self._save_no_results(session_dir, f"No hotels found for {city} on {checkin} to {checkout}")
                return False

            # Save results
            self._save_results(session_dir, city, checkin, checkout, hotels)
            return True

        except Exception as e:
            self._save_no_results(session_dir, f"Error during hotel search: {str(e)}")
            return False

    def _extract_from_conversation(self, session_dir: Path) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract city and dates from conversation file."""
        conversation_file = session_dir / "conversation_only.txt"

        if not conversation_file.exists():
            return None, None, None

        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation = f.read()

        # Single LLM call to extract essentials
        prompt = f"""
Extract the destination city and travel dates from this hotel conversation.

{conversation}

Return in this exact format:
CITY: [just the city name, like "Vail" or "New York"]
CHECKIN: [YYYY-MM-DD format]
CHECKOUT: [YYYY-MM-DD format]

If anything is unclear or missing, use NONE for that field.
"""

        response = self.client.generate(
            prompt=prompt,
            system_prompt="Extract city and dates for hotel search. Be precise and use exact formats requested."
        )

        # Parse response
        city = checkin = checkout = None

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

        # Auto-generate checkout if only checkin provided
        if checkin and not checkout:
            try:
                checkin_dt = datetime.strptime(checkin, '%Y-%m-%d')
                checkout_dt = checkin_dt + timedelta(days=2)
                checkout = checkout_dt.strftime('%Y-%m-%d')
            except ValueError:
                pass

        return city, checkin, checkout

    def _search_booking_com(self, city: str, checkin: str, checkout: str) -> List[Dict]:
        """Search Booking.com for hotels."""
        if not self.api_key:
            return []

        # Get destination ID
        dest_id = self._get_destination_id(city)
        if not dest_id:
            return []

        # Search hotels
        url = "https://booking-com.p.rapidapi.com/v1/hotels/search"

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
        }

        params = {
            "dest_id": dest_id,
            "checkin_date": checkin,
            "checkout_date": checkout,
            "adults_number": "2",
            "room_number": "1",
            "filter_by_currency": "USD",
            "order_by": "price",
            "page_number": "0"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                hotels = data.get('result', [])

                # Format hotel data
                hotel_list = []
                for hotel in hotels[:40]:  # Limit to 40 hotels
                    price = hotel.get('min_total_price', 0)
                    nights = hotel.get('nights', 2)

                    # Calculate per-night price
                    price_per_night = 0
                    if price and nights:
                        try:
                            price_per_night = round(float(price) / nights, 0)
                        except:
                            price_per_night = 0

                    hotel_list.append({
                        "name": hotel.get('hotel_name', ''),
                        "total_price": price,
                        "price_per_night": price_per_night,
                        "currency": hotel.get('currency', 'USD'),
                        "rating": hotel.get('review_score', 0),
                        "nights": nights
                    })

                return hotel_list
        except Exception:
            pass

        return []

    def _get_destination_id(self, city: str) -> Optional[str]:
        """Get Booking.com destination ID for city."""
        url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
        }

        try:
            response = requests.get(url, headers=headers, params={"name": city}, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return str(data[0].get('dest_id'))
        except Exception:
            pass

        return None

    def _save_results(self, session_dir: Path, city: str, checkin: str, checkout: str, hotels: List[Dict]) -> None:
        """Save hotel search results."""

        # Human-readable text file
        text_file = session_dir / "hotel_results.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"HOTEL SEARCH RESULTS\n")
            f.write(f"Location: {city}\n")
            f.write(f"Dates: {checkin} to {checkout}\n")
            f.write(f"Found: {len(hotels)} hotels\n")
            f.write("=" * 50 + "\n\n")

            for i, hotel in enumerate(hotels, 1):
                name = hotel['name']
                price_per_night = hotel['price_per_night']
                rating = hotel['rating']

                f.write(f"{i:2d}. {name}")
                if price_per_night:
                    f.write(f" - ${price_per_night:.0f}/night")
                if rating:
                    f.write(f" ({rating}/10)")
                f.write("\n")

        # JSON backup for future LLM consumption
        json_file = session_dir / "hotel_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "search_info": {
                    "city": city,
                    "checkin": checkin,
                    "checkout": checkout,
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
