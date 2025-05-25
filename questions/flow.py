"""
Question flow management.
"""
from typing import Dict, List, Optional

from questions.question_bank import get_questions, get_question_by_id


class QuestionFlow:
    """
    Manages the flow of questions during the interview.
    """

    def __init__(self):
        """Initialize the question flow."""
        self.questions = get_questions()
        self.current_index = 0
        self.answers = {}

    def get_next_question(self) -> Optional[Dict]:
        """
        Get the next question in the flow.

        Returns:
            Optional[Dict]: The next question or None if all questions have been asked
        """
        if self.current_index >= len(self.questions):
            return None

        question = self.questions[self.current_index]
        self.current_index += 1
        return question

    def add_answer(self, question_id: str, answer: str) -> None:
        """
        Add an answer to a question.

        Args:
            question_id: The ID of the question being answered
            answer: The answer provided
        """
        self.answers[question_id] = answer

    def get_answers(self) -> Dict[str, str]:
        """
        Get all collected answers.

        Returns:
            Dict[str, str]: Dictionary of question IDs to answers
        """
        return self.answers

    def reset(self) -> None:
        """Reset the question flow to the beginning."""
        self.current_index = 0
        self.answers = {}
