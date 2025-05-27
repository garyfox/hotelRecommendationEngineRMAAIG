#!/usr/bin/env python3
"""
Quick debug script to see why Vail hotel search is failing.
"""
import os
import requests

def debug_vail_lookup():
    """Debug the Vail destination lookup specifically."""

    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        print("❌ No RAPIDAPI_KEY set")
        print("💡 Set with: export RAPIDAPI_KEY='your-key'")
        return

    print("🎿 Debugging Vail hotel search...")
    print(f"🔑 API Key present: {'Yes' if api_key else 'No'}")

    # Test the destination lookup that's failing
    url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
    }

    # Try different variations of Vail
    test_queries = [
        "Vail",
        "Vail, Colorado",
        "Vail, CO",
        "Vail, Colorado, USA",
        "Vail Village"
    ]

    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")

        try:
            response = requests.get(url, headers=headers, params={"name": query}, timeout=15)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    for i, location in enumerate(data[:3]):  # Show top 3 results
                        name = location.get('name', 'Unknown')
                        dest_id = location.get('dest_id', 'No ID')
                        country = location.get('country', 'No country')
                        print(f"   {i+1}. {name} (ID: {dest_id}) in {country}")
                else:
                    print("   ❌ No results returned")
            else:
                print(f"   ❌ API Error: {response.text[:100]}")

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

    # Test if we can find ANY Colorado ski resorts
    print(f"\n🏔️ Testing other Colorado ski resorts...")
    ski_resorts = ["Aspen", "Breckenridge", "Steamboat Springs"]

    for resort in ski_resorts:
        try:
            response = requests.get(url, headers=headers, params={"name": resort}, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    print(f"   ✅ {resort}: Found (ID: {data[0].get('dest_id')})")
                else:
                    print(f"   ❌ {resort}: Not found")
        except:
            print(f"   ❌ {resort}: Error")

if __name__ == "__main__":
    debug_vail_lookup()
