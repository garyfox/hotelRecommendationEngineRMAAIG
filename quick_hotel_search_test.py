#!/usr/bin/env python3
"""
Quick hotel search test - bypass interview, test pagination/rows parameters.
Tests both current API and with additional parameters.
"""
import os
import requests
import json
from datetime import datetime, timedelta

def test_booking_api_pagination():
    """Test Booking.com API with different pagination parameters."""

    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        print("❌ No RAPIDAPI_KEY environment variable set")
        print("Set with: export RAPIDAPI_KEY='your_key_here'")
        return

    print("🏨 Testing Booking.com API Pagination")
    print("=" * 50)

    # Test parameters
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
    }

    # Test dates (2 weeks from now)
    checkin = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    checkout = (datetime.now() + timedelta(days=16)).strftime("%Y-%m-%d")

    # Base parameters
    base_params = {
        "units": "metric",
        "room_number": "1",
        "checkout_date": checkout,
        "checkin_date": checkin,
        "adults_number": "2",
        "order_by": "price",
        "filter_by_currency": "USD",
        "locale": "en-us",
        "dest_type": "city",
        "dest_id": "-126693",  # Rome
        "categories_filter_ids": "class::2,class::4,free_cancellation::1",
        "include_adjacency": "true"
    }

    print(f"🗓️ Search dates: {checkin} to {checkout}")
    print(f"📍 Destination: Rome (ID: -126693)")
    print()

    # Test 1: Current method (page 0 only)
    print("📋 Test 1: Current method (page_number=0)")
    test_params = base_params.copy()
    test_params["page_number"] = "0"

    try:
        response = requests.get(url, headers=headers, params=test_params, timeout=30)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            hotels = data.get('result', [])
            print(f"   ✅ Found {len(hotels)} hotels")

            # Show first few hotel names
            for i, hotel in enumerate(hotels[:5]):
                name = hotel.get('hotel_name', 'Unknown')
                price = hotel.get('min_total_price', 'N/A')
                print(f"      {i+1}. {name} - ${price}")

            if len(hotels) > 5:
                print(f"      ... and {len(hotels) - 5} more")
        else:
            print(f"   ❌ Error: {response.text[:100]}")
            return

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return

    print()

    # Test 2: Try adding 'rows' parameter
    print("📋 Test 2: Try adding 'rows' parameter (rows=50)")
    test_params = base_params.copy()
    test_params["page_number"] = "0"
    test_params["rows"] = "50"  # Try to get 50 results

    try:
        response = requests.get(url, headers=headers, params=test_params, timeout=30)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            hotels = data.get('result', [])
            print(f"   ✅ Found {len(hotels)} hotels")

            if len(hotels) > 20:
                print(f"   🎉 SUCCESS! Got more than 20 results with 'rows' parameter")
            else:
                print(f"   📝 Still {len(hotels)} results - 'rows' parameter might not work")

        else:
            print(f"   ❌ Error: {response.text[:100]}")

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

    print()

    # Test 3: Try pagination (multiple pages)
    print("📋 Test 3: Try pagination (pages 0, 1, 2)")
    all_hotels = []

    for page in range(3):
        print(f"   📄 Requesting page {page}...")
        test_params = base_params.copy()
        test_params["page_number"] = str(page)

        try:
            response = requests.get(url, headers=headers, params=test_params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                page_hotels = data.get('result', [])
                print(f"      Page {page}: {len(page_hotels)} hotels")

                if len(page_hotels) == 0:
                    print(f"      No more results on page {page}")
                    break

                all_hotels.extend(page_hotels)
            else:
                print(f"      Error on page {page}: {response.status_code}")
                break

        except Exception as e:
            print(f"      Exception on page {page}: {str(e)}")
            break

    print(f"   ✅ Total from pagination: {len(all_hotels)} hotels")

    if len(all_hotels) > 20:
        print(f"   🎉 SUCCESS! Pagination gives us {len(all_hotels)} total results")

    print()

    # Test 4: Alternative parameter names
    print("📋 Test 4: Try alternative parameter names")

    alternative_params = [
        {"offset": "0", "limit": "50"},
        {"page_size": "50"},
        {"per_page": "50"},
        {"count": "50"}
    ]

    for i, alt_params in enumerate(alternative_params):
        test_params = base_params.copy()
        test_params["page_number"] = "0"
        test_params.update(alt_params)

        param_desc = ", ".join([f"{k}={v}" for k, v in alt_params.items()])
        print(f"   Testing: {param_desc}")

        try:
            response = requests.get(url, headers=headers, params=test_params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                hotels = data.get('result', [])
                print(f"      ✅ {len(hotels)} hotels")

                if len(hotels) > 20:
                    print(f"      🎉 SUCCESS! {param_desc} gives {len(hotels)} results")
                    break
            else:
                print(f"      ❌ Error: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")

    print()
    print("🏁 Test Summary:")
    print("=" * 30)
    print("If any test showed >20 results, use that method in your code!")
    print("If all tests showed ~20 results, the API is limited to 20 per page.")
    print("Pagination (Test 3) is your best bet for more results.")


if __name__ == "__main__":
    test_booking_api_pagination()
