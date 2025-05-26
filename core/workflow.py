"""
Main workflow for the hotel recommendation system.
"""
from typing import Dict, List, Tuple, Any

from questions.question_bank import get_questions
from questions.suggestion import generate_suggestions
from llm.coherence import check_coherence, check_logical_consistency
from vector.embeddings import embed_text
from vector.storage import store_vector


class InterviewWorkflow:
    """
    Manages the workflow of the hotel preference interview process.
    """

    def __init__(self):
        """Initialize the interview workflow."""
        self.questions = get_questions()
        self.collected_answers = {}

    def get_questions(self) -> List[Dict]:
        """
        Get the list of questions to ask.

        Returns:
            List[Dict]: List of question dictionaries with id and text
        """
        return self.questions

    def validate_answer(self, question_id: str, answer: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Validate the answer and provide suggestions for improvement if needed.

        Args:
            question_id: The ID of the question being answered
            answer: The customer's answer

        Returns:
            Tuple[str, List[Dict[str, str]]]:
                - Validated answer
                - List of suggestions with type and text
        """
        # Store the answer in the collected answers
        self.collected_answers[question_id] = answer

        # Check if the answer is coherent
        is_coherent = check_coherence(question_id, answer)

        # List to store suggestions with types
        suggestions = []

        # Generate suggestions if the answer needs improvement
        if not is_coherent:
            improvement_suggestions = generate_suggestions(question_id, answer)
            for suggestion in improvement_suggestions:
                suggestions.append({
                    "type": "detail",
                    "text": suggestion
                })

        # Check logical consistency with previous answers
        if len(self.collected_answers) > 1:
            is_consistent, inconsistency_reason = check_logical_consistency(self.collected_answers)
            if not is_consistent:
                if inconsistency_reason:
                    suggestion_text = f"Your answer seems inconsistent: {inconsistency_reason}"
                else:
                    suggestion_text = "Your answer seems inconsistent with your previous responses. Please review and make sure your preferences align."

                suggestions.append({
                    "type": "inconsistency",
                    "text": suggestion_text
                })

        return answer, suggestions

    def process_preferences(self, preferences: Dict[str, str]) -> Dict[str, Any]:
        """
        Process the collected preferences.

        Args:
            preferences: Dictionary of collected preferences

        Returns:
            Dict[str, Any]: Processed preferences with additional metadata
        """
        processed_data = {}

        # For each preference, add the processed data
        for question_id, answer in preferences.items():
            # Embed the answer text
            embedding = embed_text(answer)

            # Store the embedding
            vector_id = store_vector(question_id, embedding)

            # Add to processed data
            processed_data[question_id] = {
                "text": answer,
                "vector_id": vector_id,
                "embedding": embedding,
            }

        return processed_data
