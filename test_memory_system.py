#!/usr/bin/env python3
"""
Test script for the LLM memory system.
Run this from the project root directory.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def test_memory_system():
    """Test the LLM memory system with sample data."""

    print("🧠 Testing LLM Memory System...")

    try:
        from memory.simple_memory_workflow import LLMMemoryWorkflow
        print("✅ Successfully imported LLMMemoryWorkflow")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

    try:
        # Create workflow
        workflow = LLMMemoryWorkflow()
        print("✅ Successfully created workflow")

        # Check questions
        questions = workflow.get_questions()
        print(f"✅ Loaded {len(questions)} questions")

        # Test with sample conversation
        print("\n📝 Testing sample conversation...")

        test_qa = [
            ("destination", "Where are you planning to travel?", "Santa Barbara, CA"),
            ("trip_purpose", "What's the main purpose of your trip?", "family vacation"),
            ("budget_preference", "What's your budget range per night?", "$200 per night"),
            ("amenities_features", "What hotel amenities are important?", "pool and breakfast"),
            ("stay_experience", "Describe your ideal hotel experience.", "family-friendly boutique hotel")
        ]

        for i, (q_id, q_text, answer) in enumerate(test_qa, 1):
            print(f"\n{i}. Testing question: {q_id}")
            print(f"   Answer: {answer}")

            try:
                validated, suggestions = workflow.validate_answer(q_id, q_text, answer)
                print(f"   ✅ Validated: {validated}")
                if suggestions:
                    print(f"   💡 Suggestions: {len(suggestions)} offered")
                else:
                    print(f"   ✅ No suggestions needed")
            except Exception as e:
                print(f"   ❌ Validation failed: {e}")
                return False

        # Test conversation processing
        print("\n🔄 Processing complete conversation...")
        try:
            results = workflow.process_conversation()
            print("✅ Conversation processed successfully")

            # Show insights if available
            insights = results.get("llm_insights", {})
            if insights and not insights.get("error"):
                print("\n🎯 LLM Insights:")
                for key, value in insights.items():
                    if value and value != "Not specified":
                        print(f"   {key}: {value}")
            else:
                print("⚠️  LLM insights not generated (check Ollama connection)")

            print(f"✅ Conversation consistent: {results.get('is_consistent', 'Unknown')}")

            if results.get("conversation_file"):
                print(f"✅ Conversation saved to: {results['conversation_file']}")

        except Exception as e:
            print(f"❌ Conversation processing failed: {e}")
            return False

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_ollama_connection():
    """Test if Ollama is available."""
    print("\n🔌 Testing Ollama connection...")

    try:
        from llm.ollama_client import get_ollama_client
        client = get_ollama_client()
        print("✅ Ollama client created successfully")
        return True
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return False


def main():
    """Main test function."""
    print("🚀 Hotel Preference Memory System Test")
    print("=" * 50)

    # Test Ollama first
    ollama_ok = test_ollama_connection()

    # Test memory system
    memory_ok = test_memory_system()

    print("\n" + "=" * 50)
    if memory_ok:
        print("🎉 Memory system is working!")
        if not ollama_ok:
            print("⚠️  Note: Some LLM features may not work without Ollama")
    else:
        print("❌ Memory system has issues")

    return memory_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
