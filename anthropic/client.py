"""
Anthropic Claude API client for hotel recommendation analysis.
"""
import os
import json
from typing import Dict, Optional, Any
from pathlib import Path
import requests
from datetime import datetime

from config import DATA_DIR


class AnthropicClient:
    """
    Client for interacting with Claude API for hotel recommendation analysis.
    """

    def __init__(self):
        """Initialize the Anthropic client."""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Get your API key from: https://console.anthropic.com/"
            )

        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"  # Latest Claude Sonnet model
        self.max_tokens = 2500
        self.temperature = 0.4

    def analyze_hotel_session(self, session_dir: Path) -> Dict[str, Any]:
        """
        Analyze a complete hotel session using Claude.

        Args:
            session_dir: Path to session directory containing conversation and hotel data

        Returns:
            Dict containing Claude's analysis and metadata
        """
        # Load session data
        session_data = self._load_session_data(session_dir)

        # Create the analysis prompt
        prompt = self._create_analysis_prompt(session_data)

        # Send to Claude
        response = self._call_claude_api(prompt)

        # Package results
        analysis_result = {
            "session_id": session_data.get("session_id"),
            "analyzed_at": datetime.now().isoformat(),
            "claude_model": self.model,
            "analysis": response,
            "session_summary": {
                "destination": session_data.get("destination"),
                "dates": session_data.get("dates"),
                "budget": session_data.get("budget"),
                "hotels_found": session_data.get("hotels_found", 0)
            }
        }

        # Save analysis to session directory
        self._save_analysis(session_dir, analysis_result)

        return analysis_result

    def _load_session_data(self, session_dir: Path) -> Dict[str, Any]:
        """Load and combine all session data for analysis."""
        session_data = {}

        # Load conversation
        conversation_file = session_dir / "conversation_only.txt"
        if conversation_file.exists():
            with open(conversation_file, 'r', encoding='utf-8') as f:
                session_data["conversation"] = f.read()

        # Load hotel results
        hotel_data_file = session_dir / "hotel_data.json"
        hotel_text_file = session_dir / "hotel_results.txt"

        if hotel_data_file.exists():
            with open(hotel_data_file, 'r', encoding='utf-8') as f:
                hotel_data = json.load(f)
                session_data["hotel_data"] = hotel_data
                session_data["destination"] = hotel_data.get("search_info", {}).get("city")
                session_data["dates"] = f"{hotel_data.get('search_info', {}).get('checkin')} to {hotel_data.get('search_info', {}).get('checkout')}"
                session_data["hotels_found"] = hotel_data.get("search_info", {}).get("hotels_found", 0)

        if hotel_text_file.exists():
            with open(hotel_text_file, 'r', encoding='utf-8') as f:
                session_data["hotel_results_text"] = f.read()

        # Load final responses for budget info
        final_responses_file = session_dir / "final_responses.txt"
        if final_responses_file.exists():
            with open(final_responses_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract budget from final responses
                for line in content.split('\n'):
                    if line.startswith('BUDGET PREFERENCE:'):
                        session_data["budget"] = line.split(':', 1)[1].strip()
                        break

        # Load metadata
        metadata_file = session_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                session_data["session_id"] = metadata.get("session_id")

        return session_data

    def _create_analysis_prompt(self, session_data: Dict[str, Any]) -> str:
        """Create the analysis prompt for Claude."""

        conversation = session_data.get("conversation", "No conversation data available")
        hotel_results = session_data.get("hotel_results_text", "No hotel data available")
        destination = session_data.get("destination", "Unknown")
        dates = session_data.get("dates", "Unknown")
        budget = session_data.get("budget", "Not specified")
        hotels_found = session_data.get("hotels_found", 0)

        prompt = f"""You are an expert travel psychology analyst and hotel consultant. Read between the lines of this conversation and provide brutally honest analysis of what the customer ACTUALLY needs vs what they're saying.

CUSTOMER CONVERSATION:
{conversation}

HOTEL SEARCH RESULTS:
Location: {destination}
Dates: {dates}
Customer's Stated Budget: {budget}
Hotels Found: {hotels_found}

{hotel_results}

ANALYSIS TASK:
1. Decode their real motivations and concerns
2. Challenge their assumptions with evidence
3. Provide honest pros/cons for realistic options

RESPONSE FORMAT:

## READING BETWEEN THE LINES
**What they're really telling me:** [2-3 psychological insights about their travel experience, hidden priorities, or unspoken concerns]

**The contradiction that reveals everything:** [Their biggest inconsistency and what it tells you about their real situation]

**What they're actually optimizing for:** [Their true priority that they haven't explicitly stated]

## REALITY CHECK: YOUR BUDGET VS {destination.upper()}
**The math:** [Brutal honest calculation of what their budget gets them]
**What this suggests about your experience level:** [Inference about their travel sophistication]
**The conversation you need to have with yourself:** [Questions they should ask themselves]

## HONEST RECOMMENDATIONS

### Option 1: Face Reality - [Hotel Name] ($X/night)
**Why this is actually perfect for you:**
[How this solves their real problem, not stated wants]

**PROS:**
- [Specific advantage that addresses their actual needs]
- [Another concrete benefit based on their psychology]
- [Third pro that challenges their assumptions]

**CONS:**
- [Honest drawback they need to accept]
- [Another limitation with why it matters]
- [Third con that reveals their true priorities]

**What choosing this says about you:** [Personality insight]

### Option 2: The Expensive Truth - [Hotel Name] ($X/night)
**Why you might actually want this despite the cost:**
[Challenge their budget constraints with real value analysis]

**PROS:**
- [Benefit that justifies the extra cost]
- [Advantage that addresses their unspoken needs]
- [Value proposition they haven't considered]

**CONS:**
- [Financial reality check]
- [Opportunity cost analysis]
- [What they sacrifice for this choice]

**What choosing this says about you:** [What this reveals about their priorities]

### Option 3: The Compromise You Don't Want to Hear - [Hotel Name] ($X/night)
**Why this might be your best option even though it contradicts what you said:**
[How this serves their actual needs despite surface conflicts]

**PROS:**
- [Unexpected advantage they didn't consider]
- [Benefit that solves their real problem]
- [Why this is smarter than their stated preference]

**CONS:**
- [What they give up from their wishlist]
- [Reality they need to accept]
- [Trade-off that reveals their true values]

**What choosing this says about you:** [Character/priority insight]

## THE UNCOMFORTABLE QUESTIONS
**About your budget:** [Challenge their financial assumptions]
**About your destination choice:** [Question why they picked {destination}]
**About your priorities:** [What they should reconsider]
**About this trip's real purpose:** [What this trip is actually about for them]

## BOTTOM LINE TRUTH
[One paragraph of honest advice about what they should actually do, based on reading between the lines of their entire conversation]"""

        return prompt

    def _call_claude_api(self, prompt: str) -> str:
        """Make API call to Claude."""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()

            # Extract the response text
            if "content" in result and len(result["content"]) > 0:
                return result["content"][0]["text"]
            else:
                raise Exception("Unexpected response format from Claude API")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Claude API: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected response format: {str(e)}")

    def _save_analysis(self, session_dir: Path, analysis_result: Dict[str, Any]) -> None:
        """Save Claude's analysis to the session directory."""

        # Save the full analysis as JSON
        analysis_file = session_dir / "claude_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2)

        # Save just the analysis text for easy reading
        analysis_text_file = session_dir / "claude_analysis.txt"
        with open(analysis_text_file, 'w', encoding='utf-8') as f:
            f.write("=== CLAUDE HOTEL RECOMMENDATION ANALYSIS ===\n")
            f.write(f"Session: {analysis_result.get('session_id')}\n")
            f.write(f"Analyzed: {analysis_result.get('analyzed_at')}\n")
            f.write(f"Model: {analysis_result.get('claude_model')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(analysis_result.get('analysis', ''))


# Convenience function for easy integration
def analyze_session_with_claude(session_dir: Path) -> Dict[str, Any]:
    """
    Analyze a hotel session using Claude.

    Args:
        session_dir: Path to session directory

    Returns:
        Dict containing Claude's analysis
    """
    client = AnthropicClient()
    return client.analyze_hotel_session(session_dir)
