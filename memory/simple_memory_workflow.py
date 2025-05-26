"""
Simple workflow that leverages LLM-powered conversation memory.
"""
from typing import Dict, List, Tuple, Any

from questions.question_bank import get_questions
from memory.llm_conversation_memory import (
    get_conversation_memory,
    start_new_conversation,
    end_conversation
)
from vector.embeddings import embed_text
from vector.storage import store_vector


class LLMMemoryWorkflow:
    """
    Simple workflow that uses LLM for all understanding and memory.
    """

    def __init__(self, session_id: str = None):
        """Initialize with LLM-powered conversation memory."""
        self.questions = get_questions()
        self.memory = start_new_conversation(session_id)
        self.suggestion_count = {}  # Track suggestions per question

    def validate_answer(self, question_id: str, question_text: str,
                       answer: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Validate answer using LLM with full conversation context.
        """
        # Check if answer is coherent in conversation context
        is_coherent, reason = self.memory.check_contextual_coherence(question_id, answer)

        suggestions = []
        final_answer = answer

        # Only offer suggestions if:
        # 1. Answer isn't coherent AND
        # 2. We haven't already suggested for this question AND
        # 3. Answer is genuinely lacking (very short or non-responsive)
        should_suggest = (
            not is_coherent and
            self.suggestion_count.get(question_id, 0) == 0 and
            len(answer.strip()) < 8  # Very short answers
        )

        if should_suggest:
            try:
                suggestion_texts = self.memory.generate_improvement_suggestions(question_id, answer)
                suggestions = [{"type": "detail", "text": text} for text in suggestion_texts]
                self.suggestion_count[question_id] = 1
            except Exception as e:
                print(f"Warning: Could not generate suggestions: {e}")

        # Add this turn to conversation memory (let LLM analyze it)
        self.memory.add_turn(
            question_id=question_id,
            question_text=question_text,
            raw_answer=answer,
            final_answer=final_answer,
            suggestions_offered=[s.get("text", "") for s in suggestions]
        )

        return final_answer, suggestions

    def update_answer(self, question_id: str, question_text: str,
                     improved_answer: str) -> str:
        """
        Update an answer after user provides more detail.
        """
        # Replace the last turn with the improved answer
        if self.memory.conversation_history and self.memory.conversation_history[-1].question_id == question_id:
            # Remove the last turn and add updated one
            self.memory.conversation_history.pop()

        # Add the improved answer (no suggestions this time)
        self.memory.add_turn(
            question_id=question_id,
            question_text=question_text,
            raw_answer=improved_answer,
            final_answer=improved_answer,
            suggestions_offered=[]
        )

        return improved_answer

    def check_overall_consistency(self) -> Tuple[bool, List[str]]:
        """
        Check consistency across the entire conversation using LLM.
        """
        return self.memory.check_conversation_consistency()

    def process_conversation(self) -> Dict[str, Any]:
        """
        Process the completed conversation using LLM insights.
        """
        # Get LLM synthesis of the conversation
        insights = self.memory.synthesize_conversation_insights()

        # Get conversation embedding
        conversation_embedding = self.memory.get_conversation_embedding()

        # Store conversation vector if embedding successful
        conversation_vector_id = None
        if conversation_embedding is not None:
            try:
                metadata = {
                    "session_id": self.memory.session_id,
                    "conversation_type": "hotel_preference_interview",
                    "destination": insights.get("destination"),
                    "trip_type": insights.get("trip_type"),
                    "budget": insights.get("budget")
                }
                conversation_vector_id = store_vector("conversation", conversation_embedding)
            except Exception as e:
                print(f"Warning: Could not store conversation vector: {e}")

        # Check final consistency
        is_consistent, consistency_issues = self.check_overall_consistency()

        # Build comprehensive results
        processed_data = {
            # LLM-generated insights (this is the key output)
            "llm_insights": insights,

            # Conversation metadata
            "session_id": self.memory.session_id,
            "is_consistent": is_consistent,
            "consistency_issues": consistency_issues,

            # Embeddings and vectors
            "conversation_embedding": conversation_embedding,
            "conversation_vector_id": conversation_vector_id,

            # Full conversation for reference
            "conversation_summary": self.memory._build_conversation_summary(),

            # Legacy format (individual Q&A pairs)
            "preferences": {
                turn.question_id: turn.final_answer
                for turn in self.memory.conversation_history
            },

            # Rich turn-by-turn analysis
            "detailed_analysis": [
                {
                    "question_id": turn.question_id,
                    "question": turn.question_text,
                    "answer": turn.final_answer,
                    "llm_analysis": turn.llm_analysis
                }
                for turn in self.memory.conversation_history
            ]
        }

        # Save conversation to disk
        try:
            conversation_file = end_conversation()
            if conversation_file:
                processed_data["conversation_file"] = str(conversation_file)
        except Exception as e:
            print(f"Warning: Could not save conversation: {e}")

        return processed_data

    def get_questions(self) -> List[Dict]:
        """Get the list of questions."""
        return self.questions

    def get_conversation_context(self) -> str:
        """Get current conversation context for display."""
        return self.memory._build_conversation_context()


# Simple utility functions
def create_llm_workflow(session_id: str = None) -> LLMMemoryWorkflow:
    """Create a new LLM-powered workflow."""
    return LLMMemoryWorkflow(session_id)


def analyze_saved_conversation(conversation_file: str) -> Dict[str, Any]:
    """
    Analyze a saved conversation file.
    """
    import json
    from pathlib import Path

    try:
        with open(conversation_file, 'r') as f:
            data = json.load(f)

        return {
            "session_id": data.get("session_id"),
            "insights": data.get("final_insights", {}),
            "conversation_length": len(data.get("conversation_history", [])),
            "summary": data.get("conversation_summary", "")
        }
    except Exception as e:
        return {"error": f"Could not analyze conversation: {e}"}
