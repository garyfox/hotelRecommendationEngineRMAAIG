#!/usr/bin/env python3
"""
Completely isolated test - copy the function directly here.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from llm.ollama_client import get_ollama_client

def isolated_extract_from_conversation(session_dir: Path) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Completely isolated copy of the extraction function."""
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

    client = get_ollama_client()
    response = client.generate(
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

    # Debug output before return
    print(f"🔍 ISOLATED DEBUG: About to return 4 values:")
    print(f"   city = {repr(city)}")
    print(f"   checkin = {repr(checkin)}")
    print(f"   checkout = {repr(checkout)}")
    print(f"   locale = {repr(locale)}")

    # Return exactly 4 values - use explicit tuple construction
    result_tuple = (city, checkin, checkout, locale)
    print(f"🔍 ISOLATED DEBUG: Created tuple: {result_tuple}")
    print(f"🔍 ISOLATED DEBUG: Tuple length: {len(result_tuple)}")

    return result_tuple

def test_isolated():
    """Test the isolated function."""
    session_path = Path("data/sessions/20250526_211306")

    if not session_path.exists():
        print(f"❌ Session not found: {session_path}")
        return

    print(f"📁 Testing isolated function with: {session_path}")

    result = isolated_extract_from_conversation(session_path)

    print(f"🔍 ISOLATED RESULT: {result}")
    print(f"🔍 ISOLATED TYPE: {type(result)}")
    print(f"🔍 ISOLATED LENGTH: {len(result)}")

    # Try unpacking
    try:
        city, checkin, checkout, locale = result
        print(f"✅ ISOLATED SUCCESS!")
        print(f"   City: {city}")
        print(f"   Checkin: {checkin}")
        print(f"   Checkout: {checkout}")
        print(f"   Locale: {locale}")
    except Exception as e:
        print(f"❌ ISOLATED UNPACKING FAILED: {e}")

if __name__ == "__main__":
    test_isolated()
