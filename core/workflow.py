"""
Main workflow for the hotel recommendation system with conversation logging.
"""
from typing import Dict, List, Tuple, Any

from questions.question_bank import get_questions, get_question_by_id
from questions.suggestion import generate_suggestions
from llm.coherence import check_coherence, check_logical_consistency
from vector.embeddings import embed_text
from vector.storage import store_vector
from logger import get_conversation_logger


class InterviewWorkflow:
    """
    Manages the workflow of the hotel preference interview process.
    """

    def __init__(self):
        """Initialize the interview workflow."""
        self.questions = get_questions()
        self.collected_answers = {}
        self.logger = get_conversation_logger()

    def get_questions(self) -> List[Dict]:
        """
        Get the list of questions to ask.

        Returns:
            List[Dict]: List of question dictionaries with id and text
        """
        return self.questions

    def log_question(self, question_id: str, question_text: str):
        """Log a question being asked."""
        self.logger.log_question(question_id, question_text)

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

        # Log the user response
        self.logger.log_user_response(question_id, answer)

        # Check if the answer is coherent
        is_coherent = check_coherence(question_id, answer)

        # Log the coherence check
        question_obj = get_question_by_id(question_id)
        question_text = question_obj["text"] if question_obj else f"Question {question_id}"
        self.logger.log_llm_reasoning(
            "coherence_check",
            "Evaluate hotel preference answer quality",
            f"Question: {question_text} Answer: {answer}",
            f"{'Yes' if is_coherent else 'No'}",
            context=f"Checking if answer is useful for hotel matching"
        )

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

            # Log the consistency check
            self.logger.log_llm_reasoning(
                "consistency_check",
                "Evaluate logical consistency of preferences",
                f"All answers: {self.collected_answers}",
                f"{'Yes' if is_consistent else f'No: {inconsistency_reason}'}",
                context="Checking if preferences are logically consistent"
            )

            if not is_consistent:
                if inconsistency_reason:
                    suggestion_text = f"Your answer seems inconsistent: {inconsistency_reason}"
                else:
                    suggestion_text = "Your answer seems inconsistent with your previous responses. Please review and make sure your preferences align."

                suggestions.append({
                    "type": "inconsistency",
                    "text": suggestion_text
                })

        # Log suggestions if any
        if suggestions:
            self.logger.log_suggestions(question_id, suggestions)

        return answer, suggestions

    def log_answer_revision(self, question_id: str, original_answer: str, revised_answer: str):
        """Log when an answer gets revised."""
        self.collected_answers[question_id] = revised_answer
        self.logger.log_user_response(question_id, revised_answer, is_revision=True)

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

        # Finalize the conversation session
        self.logger.finalize_session()

        return processed_data

    def get_session_directory(self):
        """Get the current session directory."""
        session_info = self.logger.get_session_info()
        return session_info['session_dir']
