"""
Prompt templates for interactions with the LLM.
"""
from typing import Dict


# System prompt for coherence checking
COHERENCE_SYSTEM_PROMPT = """
You are an AI assistant helping to evaluate the quality of answers to hotel preference questions.
Your task is to determine if an answer is coherent, detailed, and useful enough.
A good answer should provide specific preferences and enough context to understand what the person wants.
"""

# Optimized system prompt for coherence checking
COHERENCE_SYSTEM_PROMPT = """
You are an AI assistant helping to evaluate hotel preference answers that will be used for matching with reviews.
Your task is to determine if an answer is coherent AND useful for search and matching purposes.

A GOOD ANSWER should:
1. Be clearly related to the question being asked
2. Contain specific, actionable preferences that could be matched against hotel reviews
3. Provide enough concrete details to narrow down hotel options
4. Include keywords or criteria that could be used in a search

Importantly, the answer must include SPECIFIC PREFERENCES rather than just general statements.
For example, "I want a hotel near the beach" is more useful than just "a nice location."
"A modern boutique hotel with local character" is better than just "a nice hotel."

Evaluate the answers based on their search utility, not their length or eloquence.
"""

# Optimized prompt template for checking answer usefulness
COHERENCE_PROMPT_TEMPLATE = """
Question: {question}

Answer: {answer}

Is this answer coherent AND useful for hotel matching/searching purposes?
Focus on whether it contains specific preferences that could be used to match against hotel reviews and descriptions.

Respond with 'Yes' if the answer provides SPECIFIC, SEARCHABLE criteria.
Respond with 'No' if the answer is too vague, generic, or lacks specific preferences that would help with matching.
"""


# System prompt for logical consistency checking
CONSISTENCY_SYSTEM_PROMPT = """
You are an AI assistant helping to evaluate the logical consistency of hotel preferences.
Your task is to determine if the answers to different questions are logically consistent with each other.
For example, wanting a budget hotel but expecting 5-star amenities would be inconsistent.
Wanting to go skiing but choosing a tropical beach destination would be inconsistent.
"""


# Prompt template for checking logical consistency
CONSISTENCY_PROMPT_TEMPLATE = """
Here are the answers provided to hotel preference questions:

{answer_summary}

Are these preferences logically consistent with each other?
Respond with 'Yes' if they are consistent or 'No' if there are logical contradictions.
"""


# System prompt for generating suggestions
SUGGESTIONS_SYSTEM_PROMPT = """
You are an AI assistant helping travelers provide detailed hotel preferences.
Your task is to generate helpful suggestions to improve an answer that lacks detail.
Focus on asking for specifics that would help match the traveler with suitable hotels.
"""


# Prompt template for generating suggestions
SUGGESTIONS_PROMPT_TEMPLATE = """
Question: {question}

Answer: {answer}

This answer needs more detail. Generate 2 specific suggestions that would help the traveler
provide more useful information. Each suggestion should be a question or prompt that
encourages more specific details. Keep suggestions brief and helpful.
"""


def get_coherence_prompt(question: str, answer: str) -> Dict[str, str]:
    """
    Get the prompt for checking answer coherence.

    Args:
        question: The question being answered
        answer: The answer to check

    Returns:
        Dict[str, str]: Dictionary with system and user prompts
    """
    return {
        "system": COHERENCE_SYSTEM_PROMPT,
        "user": COHERENCE_PROMPT_TEMPLATE.format(
            question=question,
            answer=answer
        )
    }


def get_consistency_prompt(answers: Dict[str, str]) -> Dict[str, str]:
    """
    Get the prompt for checking logical consistency.

    Args:
        answers: Dictionary of question IDs to answers

    Returns:
        Dict[str, str]: Dictionary with system and user prompts
    """
    # Format the answers into a summary
    answer_summary = ""
    for q_id, answer in answers.items():
        # Make the question ID more readable
        readable_q = q_id.replace("_", " ").title()
        answer_summary += f"{readable_q}: {answer}\n\n"

    return {
        "system": CONSISTENCY_SYSTEM_PROMPT,
        "user": CONSISTENCY_PROMPT_TEMPLATE.format(
            answer_summary=answer_summary
        )
    }


def get_suggestions_prompt(question: str, answer: str) -> Dict[str, str]:
    """
    Get the prompt for generating suggestions.

    Args:
        question: The question being answered
        answer: The answer that needs improvement

    Returns:
        Dict[str, str]: Dictionary with system and user prompts
    """
    return {
        "system": SUGGESTIONS_SYSTEM_PROMPT,
        "user": SUGGESTIONS_PROMPT_TEMPLATE.format(
            question=question,
            answer=answer
        )
    }
