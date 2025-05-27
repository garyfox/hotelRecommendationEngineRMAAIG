#!/usr/bin/env python3
"""
Simple test script for Booking.com API hotel pricing.
Tests hotel lookups in Rome to verify the API works.
"""
import os
import requests
from datetime import datetime, timedelta

def test_hotel_price():
    """Test getting hotel prices in Rome."""
    # Get API key from environment variable
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    if not rapidapi_key:
        print("\n❌ Error: RAPIDAPI_KEY environment variable not set")
        print("Please set your RapidAPI key with: export RAPIDAPI_KEY='your-key-here'")
        return
    
    # Test dates (2 months from now)
    today = datetime.now()
    check_in = (today + timedelta(days=60)).strftime("%Y-%m-%d")
    check_out = (today + timedelta(days=62)).strftime("%Y-%m-%d")
    
    print(f"\n🔍 Testing Booking.com API")
    print(f"Check-in: {check_in}")
    print(f"Check-out: {check_out}")
    
    try:
        url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
        
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
        }
        
        # Rome search parameters
        payload = {
            "units": "metric",
            "room_number": "1",
            "checkout_date": check_out,
            "checkin_date": check_in,
            "adults_number": "2",
            "order_by": "price",
            "filter_by_currency": "EUR",  # Change to EUR for more accurate local prices
            "locale": "en-us",
            "dest_type": "city",
            "dest_id": "-126693", # Rome city ID
            "categories_filter_ids": "class::2,class::4,free_cancellation::1",
            "page_number": "0",
            "include_adjacency": "true"
        }
        
        print("\n📡 Sending API request...")
        response = requests.get(url, headers=headers, params=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            properties = data.get('result', [])
            
            if properties:
                print(f"\n✅ Found {len(properties)} hotels!")
                
                # Show all hotels with prices
                for prop in properties:
                    name = prop.get('hotel_name', 'Unknown Hotel')
                    price = prop.get('min_total_price', 'N/A')
                    currency = prop.get('currency', 'EUR')
                    rating = prop.get('review_score', 'No rating')
                    nights = prop.get('nights', 2)  # Number of nights in stay
                    price_per_night = float(price) / nights if price != 'N/A' else 'N/A'
                    is_tax_included = prop.get('taxes_and_fees_are_included', False)
                    
                    print(f"\n🏨 {name}")
                    print(f"  Total Price: {price} {currency} ({nights} nights)")
                    print(f"  Price per night: {price_per_night:.2f} {currency}" if price_per_night != 'N/A' else "  Price per night: N/A")
                    print(f"  Rating: {rating}/10" if rating != 'No rating' else f"  Rating: {rating}")
                    print(f"  Taxes & Fees: {'Included' if is_tax_included else 'Not included'}")
            else:
                print("\n❌ No hotels found in response")
                print(f"Response data: {data}")
        else:
            print(f"\n❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    test_hotel_price()