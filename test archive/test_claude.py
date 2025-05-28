#!/usr/bin/env python3
"""
Test script for Claude integration.
Tests the Anthropic analysis on an existing session.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from anthropic.client import analyze_session_with_claude


def test_claude_integration():
    """Test Claude analysis on an existing session."""

    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your_key_here'")
        print("Get your API key from: https://console.anthropic.com/")
        return False

    print("✅ API key found")

    # Look for existing sessions
    data_dir = Path("data/sessions")
    if not data_dir.exists():
        print("❌ No data/sessions directory found")
        print("Run the main interview first to create a session")
        return False

    # Find the most recent session
    sessions = list(data_dir.glob("*"))
    if not sessions:
        print("❌ No sessions found in data/sessions/")
        print("Run the main interview first to create a session")
        return False

    # Use the most recent session (highest timestamp)
    latest_session = max(sessions, key=lambda x: x.name)
    print(f"🔍 Testing with session: {latest_session.name}")

    # Check required files exist
    required_files = ["conversation_only.txt", "hotel_results.txt", "hotel_data.json"]
    missing_files = []

    for file_name in required_files:
        if not (latest_session / file_name).exists():
            missing_files.append(file_name)

    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Make sure the session completed hotel search")
        return False

    print("✅ All required files present")

    # Test the analysis
    try:
        print("\n🧠 Sending to Claude for analysis...")
        print("(This may take 10-30 seconds)")

        result = analyze_session_with_claude(latest_session)

        print("✅ Claude analysis completed!")
        print(f"📄 Analysis saved to: {latest_session / 'claude_analysis.txt'}")

        # Show a preview of the analysis
        analysis_file = latest_session / "claude_analysis.txt"
        with open(analysis_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print("\n" + "="*50)
        print("PREVIEW OF CLAUDE ANALYSIS:")
        print("="*50)

        # Show first 20 lines
        for line in lines[:20]:
            print(line.rstrip())

        if len(lines) > 20:
            print(f"\n... and {len(lines) - 20} more lines in the full file")

        print("\n" + "="*50)
        print(f"✅ Full analysis available at: {analysis_file}")

        return True

    except Exception as e:
        print(f"❌ Claude analysis failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Claude Integration")
    print("="*40)

    success = test_claude_integration()

    if success:
        print("\n🎉 Claude integration test PASSED!")
        print("You can now use Claude analysis in the main CLI")
    else:
        print("\n💥 Claude integration test FAILED")
        print("Check the error messages above for troubleshooting")

    # Always show usage instructions
    show_usage_instructions()


def show_usage_instructions():
    """Show how to use the Claude integration."""
    print("\n" + "="*60)
    print("CLAUDE INTEGRATION USAGE INSTRUCTIONS")
    print("="*60)

    print("\n1. SET UP API KEY:")
    print("   export ANTHROPIC_API_KEY='your_api_key_here'")
    print("   Get your key from: https://console.anthropic.com/")

    print("\n2. RUN COMPLETE INTERVIEW:")
    print("   python main.py interview")
    print("   - Answer all 6 questions")
    print("   - Say 'yes' to hotel search")
    print("   - Say 'yes' to Claude analysis")

    print("\n3. OR TEST ON EXISTING SESSION:")
    print("   python test_claude_integration.py")

    print("\n4. EXPECTED FILES IN SESSION DIRECTORY:")
    print("   - conversation_only.txt")
    print("   - hotel_results.txt")
    print("   - hotel_data.json")
    print("   - claude_analysis.txt (after analysis)")

    print("\n5. COST ESTIMATE:")
    print("   - ~2000-3000 tokens per analysis")
    print("   - Approximately $0.15 per session")
    print("   - Claude Sonnet 4 via API")

    print("\n" + "="*60)
