"""
LLM-powered conversation memory system that builds context progressively.
Uses the LLM to understand, synthesize, and evaluate the entire conversation.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from llm.ollama_client import get_ollama_client
from vector.embeddings import embed_text
from vector.storage import get_vector_store


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""
    turn_id: str
    timestamp: datetime
    question_id: str
    question_text: str
    raw_answer: str
    final_answer: str
    suggestions_offered: List[str]
    llm_analysis: Dict[str, Any]  # LLM's analysis of this turn


class ConversationMemory:
    """
    Manages conversation memory using LLM for understanding and synthesis.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.conversation_history: List[ConversationTurn] = []
        self.vector_store = get_vector_store()
        self.client = get_ollama_client()

    def add_turn(self, question_id: str, question_text: str,
                 raw_answer: str, final_answer: str,
                 suggestions_offered: List[str] = None) -> ConversationTurn:
        """Add a new conversation turn and analyze with LLM."""

        # Get LLM analysis of this turn in context
        llm_analysis = self._analyze_turn_with_llm(
            question_id, question_text, final_answer
        )

        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            question_id=question_id,
            question_text=question_text,
            raw_answer=raw_answer,
            final_answer=final_answer,
            suggestions_offered=suggestions_offered or [],
            llm_analysis=llm_analysis
        )

        self.conversation_history.append(turn)
        return turn

    def _analyze_turn_with_llm(self, question_id: str, question_text: str,
                              answer: str) -> Dict[str, Any]:
        """Use LLM to analyze this turn in conversation context."""

        conversation_context = self._build_conversation_context()

        analysis_prompt = f"""
Analyze this turn in the hotel preference conversation:

CONVERSATION SO FAR:
{conversation_context}

CURRENT TURN:
Question: {question_text}
Answer: {answer}

Please analyze this turn and provide:
1. Key information extracted from this answer
2. How this connects to previous answers
3. Any preferences or requirements this reveals
4. Useful keywords or concepts for hotel search

Respond in this JSON format:
{{
    "extracted_info": ["list", "of", "key", "facts"],
    "connections": "how this relates to previous answers",
    "revealed_preferences": ["preference1", "preference2"],
    "search_keywords": ["keyword1", "keyword2"],
    "overall_coherence": "assessment of how this fits the conversation"
}}
"""

        system_prompt = """
You are analyzing a hotel preference interview conversation. Extract meaningful information
that would help match the customer with suitable hotels. Focus on understanding the customer's
real intent and preferences, not just surface details.
"""

        try:
            response = self.client.generate(
                prompt=analysis_prompt,
                system_prompt=system_prompt
            )

            # Try to parse JSON response
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                # Fallback to simple analysis if JSON parsing fails
                analysis = {
                    "extracted_info": [answer],
                    "connections": "Unable to parse detailed analysis",
                    "revealed_preferences": [],
                    "search_keywords": answer.split()[:5],
                    "overall_coherence": "Parsed as fallback"
                }

            return analysis

        except Exception as e:
            print(f"Warning: Could not analyze turn with LLM: {e}")
            return {
                "extracted_info": [answer],
                "connections": "Analysis failed",
                "revealed_preferences": [],
                "search_keywords": [],
                "overall_coherence": "Analysis unavailable"
            }

    def _build_conversation_context(self) -> str:
        """Build conversation context for LLM analysis."""
        if not self.conversation_history:
            return "No previous conversation."

        context_parts = []
        for i, turn in enumerate(self.conversation_history, 1):
            context_parts.append(f"{i}. Q: {turn.question_text}")
            context_parts.append(f"   A: {turn.final_answer}")
            if turn.llm_analysis.get("extracted_info"):
                context_parts.append(f"   Key info: {', '.join(turn.llm_analysis['extracted_info'])}")

        return "\n".join(context_parts)

    def check_contextual_coherence(self, question_id: str, answer: str) -> Tuple[bool, str]:
        """Use LLM to check if answer is coherent in conversation context."""

        conversation_context = self._build_conversation_context()

        coherence_prompt = f"""
Evaluate this answer in the context of the ongoing hotel preference conversation:

CONVERSATION CONTEXT:
{conversation_context}

CURRENT QUESTION: {question_id}
CURRENT ANSWER: {answer}

Evaluate this answer for:
1. Does it provide useful information for hotel matching?
2. Does it make sense given the conversation so far?
3. Is it specific enough to be actionable?

Consider that:
- Short answers can be fine if they're specific and in context
- Answers should build on what we already know
- Perfect consistency isn't required, but major contradictions are problematic

Respond with either:
"COHERENT: [brief reason why it's good]"
or
"NEEDS_DETAIL: [brief reason why more detail would help]"
"""

        system_prompt = """
You are evaluating hotel preference answers for usefulness in conversation context.
Be reasonably lenient - focus on whether the answer moves the conversation forward
and provides actionable information for hotel matching.
"""

        try:
            response = self.client.generate(
                prompt=coherence_prompt,
                system_prompt=system_prompt
            )

            response = response.strip()

            if response.startswith("COHERENT"):
                return True, response[9:].strip()
            elif response.startswith("NEEDS_DETAIL"):
                return False, response[13:].strip()
            else:
                # Default assessment based on length if LLM response is unclear
                return len(answer.strip()) > 3, "Fallback assessment"

        except Exception as e:
            print(f"Warning: Could not check coherence with LLM: {e}")
            # Fallback to simple length check
            return len(answer.strip()) > 3, "LLM check failed, using fallback"

    def check_conversation_consistency(self) -> Tuple[bool, List[str]]:
        """Use LLM to check consistency across entire conversation."""

        if len(self.conversation_history) < 2:
            return True, []

        conversation_summary = self._build_conversation_summary()

        consistency_prompt = f"""
Review this hotel preference conversation for logical consistency:

{conversation_summary}

Look for significant contradictions that would make it impossible or very difficult
to find a suitable hotel. For example:
- Wanting luxury amenities with a very low budget
- Wanting beach activities in a landlocked city
- Wanting quiet retreat but also nightlife

DO NOT flag as inconsistent:
- Wanting multiple types of activities (people do many things on trips)
- Slight variations in preferences (preferences can be multifaceted)
- Different aspects of the same location (places can have beaches AND history)

If you find significant contradictions, list them. Otherwise, respond "CONSISTENT".

Format:
Either: "CONSISTENT"
Or: "INCONSISTENT: [specific contradiction 1]; [specific contradiction 2]"
"""

        system_prompt = """
You are checking hotel preferences for major logical contradictions.
Be lenient and only flag clear, significant contradictions that would make
hotel recommendations impossible or very difficult.
"""

        try:
            response = self.client.generate(
                prompt=consistency_prompt,
                system_prompt=system_prompt
            )

            response = response.strip()

            if response.startswith("CONSISTENT"):
                return True, []
            elif response.startswith("INCONSISTENT"):
                issues = response[13:].strip()
                issue_list = [issue.strip() for issue in issues.split(';') if issue.strip()]
                return False, issue_list
            else:
                # Default to consistent if unclear
                return True, []

        except Exception as e:
            print(f"Warning: Could not check consistency with LLM: {e}")
            return True, []  # Default to consistent

    def generate_improvement_suggestions(self, question_id: str, answer: str) -> List[str]:
        """Use LLM to generate contextual improvement suggestions."""

        conversation_context = self._build_conversation_context()

        suggestion_prompt = f"""
The user gave this answer in a hotel preference conversation:

CONVERSATION CONTEXT:
{conversation_context}

CURRENT QUESTION: {question_id}
CURRENT ANSWER: {answer}

The answer could use more detail to help find better hotel matches. Generate 2 brief,
helpful suggestions that would provide genuinely useful additional information.

Consider what we already know and what would be most valuable to learn next.
Keep suggestions encouraging and specific.

Format as:
1. [specific suggestion]
2. [specific suggestion]
"""

        system_prompt = """
You are helping travelers provide more useful hotel preferences.
Generate practical suggestions that would genuinely help with hotel matching,
considering the conversation context.
"""

        try:
            response = self.client.generate(
                prompt=suggestion_prompt,
                system_prompt=system_prompt
            )

            # Parse numbered suggestions
            suggestions = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    suggestion = line[line.find(' ')+1:].strip().rstrip('.:;,')
                    if suggestion:
                        suggestions.append(suggestion)

            return suggestions[:2]  # Limit to 2

        except Exception as e:
            print(f"Warning: Could not generate suggestions with LLM: {e}")
            return ["Could you provide a bit more detail?"]

    def synthesize_conversation_insights(self) -> Dict[str, Any]:
        """Use LLM to synthesize insights from the complete conversation."""

        conversation_summary = self._build_conversation_summary()

        synthesis_prompt = f"""
Analyze this complete hotel preference conversation and provide insights:

{conversation_summary}

Please provide:
1. The customer's primary destination and any specific areas mentioned
2. Type of trip and who's traveling
3. Budget range and category (budget/mid-range/luxury)
4. Key amenities and features they want
5. Preferred hotel style and atmosphere
6. Main activities they plan to do
7. Any special requirements or constraints
8. Search keywords that would help find matching hotels

Be specific and actionable. Extract real insights, not just repeat what was said.

Respond in JSON format:
{{
    "destination": "primary location",
    "trip_type": "type and travelers",
    "budget": "range and category",
    "amenities": ["key", "amenities"],
    "style": "preferred hotel style",
    "activities": ["planned", "activities"],
    "requirements": ["special", "needs"],
    "search_keywords": ["keyword1", "keyword2", "keyword3"]
}}
"""

        system_prompt = """
You are synthesizing hotel preference conversations into actionable insights.
Focus on extracting information that would help match the customer with suitable hotels.
Be specific and practical.
"""

        try:
            response = self.client.generate(
                prompt=synthesis_prompt,
                system_prompt=system_prompt
            )

            # Try to parse JSON
            try:
                insights = json.loads(response)
            except json.JSONDecodeError:
                # Fallback parsing
                insights = {
                    "destination": "Not specified",
                    "trip_type": "Not specified",
                    "budget": "Not specified",
                    "amenities": [],
                    "style": "Not specified",
                    "activities": [],
                    "requirements": [],
                    "search_keywords": []
                }

            return insights

        except Exception as e:
            print(f"Warning: Could not synthesize insights with LLM: {e}")
            return {"error": "Could not analyze conversation"}

    def _build_conversation_summary(self) -> str:
        """Build complete conversation summary."""
        if not self.conversation_history:
            return "No conversation yet."

        summary_parts = []
        summary_parts.append(f"Hotel Preference Interview (Session: {self.session_id})")
        summary_parts.append("=" * 50)

        for i, turn in enumerate(self.conversation_history, 1):
            summary_parts.append(f"\n{i}. {turn.question_text}")
            summary_parts.append(f"Answer: {turn.final_answer}")

            if turn.llm_analysis.get("extracted_info"):
                summary_parts.append(f"Key info: {', '.join(turn.llm_analysis['extracted_info'])}")

        return "\n".join(summary_parts)

    def get_conversation_embedding(self) -> Optional[Any]:
        """Get embedding for the synthesized conversation."""
        insights = self.synthesize_conversation_insights()

        # Create a rich text summary for embedding
        embedding_text = f"""
Hotel preference conversation summary:
Destination: {insights.get('destination', 'Not specified')}
Trip type: {insights.get('trip_type', 'Not specified')}
Budget: {insights.get('budget', 'Not specified')}
Amenities: {', '.join(insights.get('amenities', []))}
Style: {insights.get('style', 'Not specified')}
Activities: {', '.join(insights.get('activities', []))}
Requirements: {', '.join(insights.get('requirements', []))}

Full conversation:
{self._build_conversation_summary()}
"""

        try:
            return embed_text(embedding_text)
        except Exception as e:
            print(f"Warning: Could not embed conversation: {e}")
            return None

    def save_conversation(self, file_path: Optional[Path] = None) -> Path:
        """Save the complete conversation with LLM insights."""
        if file_path is None:
            file_path = Path(f"data/conversations/{self.session_id}.json")

        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Get final insights
        final_insights = self.synthesize_conversation_insights()

        conversation_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "conversation_history": [asdict(turn) for turn in self.conversation_history],
            "final_insights": final_insights,
            "conversation_summary": self._build_conversation_summary()
        }

        # Convert datetime objects to strings for JSON serialization
        for turn in conversation_data["conversation_history"]:
            turn["timestamp"] = turn["timestamp"].isoformat()

        with open(file_path, 'w') as f:
            json.dump(conversation_data, f, indent=2, default=str)

        return file_path


# Global conversation memory instance
_current_conversation: Optional[ConversationMemory] = None


def get_conversation_memory() -> ConversationMemory:
    """Get or create the current conversation memory."""
    global _current_conversation
    if _current_conversation is None:
        _current_conversation = ConversationMemory()
    return _current_conversation


def start_new_conversation(session_id: Optional[str] = None) -> ConversationMemory:
    """Start a new conversation session."""
    global _current_conversation
    _current_conversation = ConversationMemory(session_id)
    return _current_conversation


def end_conversation() -> Optional[Path]:
    """End current conversation and save it."""
    global _current_conversation
    if _current_conversation is None:
        return None

    # Save conversation
    file_path = _current_conversation.save_conversation()

    # Store as vector for future similarity search
    embedding = _current_conversation.get_conversation_embedding()
    if embedding is not None:
        insights = _current_conversation.synthesize_conversation_insights()
        metadata = {
            "session_id": _current_conversation.session_id,
            "conversation_type": "hotel_preference_interview",
            "destination": insights.get("destination"),
            "trip_type": insights.get("trip_type"),
            "budget": insights.get("budget"),
            "timestamp": datetime.now().isoformat()
        }

        try:
            vector_store = get_vector_store()
            vector_store.store(embedding, metadata)
        except Exception as e:
            print(f"Warning: Could not store conversation vector: {e}")

    # Clear current conversation
    _current_conversation = None

    return file_path
