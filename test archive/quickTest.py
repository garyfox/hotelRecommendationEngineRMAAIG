#!/usr/bin/env python3
"""
Quick test of hotel search without doing the full interview.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from hotel_search import HotelSearcher

def test_hotel_search():
    """Test hotel search with known good session."""

    # Use the known good session
    session_path = Path("data/sessions/20250526_211306")

    if not session_path.exists():
        print(f"❌ Session not found: {session_path}")
        return

    print(f"📁 Testing hotel search with: {session_path}")

    # Create searcher and test
    searcher = HotelSearcher()

    print("🏨 Starting hotel search test...")
    success = searcher.search_hotels_for_session(session_path)

    if success:
        print("✅ Hotel search completed successfully!")

        # Check results
        results_file = session_path / "hotel_results.txt"
        if results_file.exists():
            print(f"📄 Results saved to: {results_file}")
            print("\n📋 First few lines of results:")
            with open(results_file, 'r') as f:
                lines = f.readlines()
                for line in lines[:10]:
                    print(f"   {line.strip()}")
        else:
            print("❌ No results file found")
    else:
        print("❌ Hotel search failed")

if __name__ == "__main__":
    test_hotel_search()
