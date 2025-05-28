#!/usr/bin/env python3
"""
Direct test of the extraction method without imports to check for caching issues.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def test_direct():
    """Test by importing fresh."""

    # Clear any cached modules
    if 'hotel_search' in sys.modules:
        del sys.modules['hotel_search']

    # Fresh import
    from hotel_search import HotelSearcher

    # Test the specific session
    session_path = Path("data/sessions/20250526_211306")

    if not session_path.exists():
        print(f"❌ Session not found: {session_path}")
        return

    print(f"📁 Testing with: {session_path}")

    # Create fresh searcher
    searcher = HotelSearcher()

    # Test directly
    print("🔍 Calling _extract_from_conversation directly...")
    print("🚨 ABOUT TO CALL _extract_from_conversation")
    result = searcher._extract_from_conversation(session_path)
    print(f"🚨 IMMEDIATELY AFTER CALL: {result}")
    print(f"🚨 TYPE IMMEDIATELY AFTER: {type(result)}")
    print(f"🚨 LENGTH IMMEDIATELY AFTER: {len(result)}")

    print(f"🔍 DIRECT RESULT: {result}")
    print(f"🔍 DIRECT TYPE: {type(result)}")
    print(f"🔍 DIRECT LENGTH: {len(result)}")

    # Try unpacking
    try:
        city, checkin, checkout, locale = result
        print(f"✅ SUCCESS!")
        print(f"   City: {city}")
        print(f"   Checkin: {checkin}")
        print(f"   Checkout: {checkout}")
        print(f"   Locale: {locale}")
    except Exception as e:
        print(f"❌ UNPACKING FAILED: {e}")

if __name__ == "__main__":
    test_direct()
