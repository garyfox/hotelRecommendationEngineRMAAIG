#!/usr/bin/env python3
"""
Test the LLM extraction function directly to debug the unpacking error.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from hotel_search import HotelSearcher

def test_extraction():
    """Test the extraction function directly."""

    # Use the specific session we know works
    target_session = "20250526_211306"
    sessions_dir = Path("data/sessions")
    session_path = sessions_dir / target_session

    if not session_path.exists():
        print(f"❌ Target session not found: {session_path}")
        print("Available sessions:")
        for session_dir in sessions_dir.iterdir():
            if session_dir.is_dir():
                print(f"  - {session_dir.name}")
        return

    print(f"📁 Testing with known good session: {target_session}")

    # Test the extraction
    searcher = HotelSearcher()

    try:
        print("🔍 Testing _extract_from_conversation...")
        result = searcher._extract_from_conversation(session_path)
        print(f"🔍 DEBUG: Immediately after call: {result}")
        print(f"🔍 DEBUG: Type immediately after: {type(result)}")
        print(f"✅ Extraction successful!")
        print(f"📋 Result type: {type(result)}")
        print(f"📋 Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        print(f"📋 Result: {result}")

        # Try to unpack
        print("🔍 Testing unpacking...")
        city, checkin, checkout, locale = result
        print(f"✅ Unpacking successful!")
        print(f"   City: {city}")
        print(f"   Check-in: {checkin}")
        print(f"   Check-out: {checkout}")
        print(f"   Locale: {locale}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extraction()
