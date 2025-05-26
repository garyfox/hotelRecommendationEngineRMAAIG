"""
Improved prompt templates for interactions with the LLM.
"""
from typing import Dict


# Relaxed system prompt for coherence checking
COHERENCE_SYSTEM_PROMPT = """
You are an AI assistant helping to evaluate hotel preference answers.
Your task is to determine if an answer provides enough useful information for hotel matching.

A GOOD ANSWER should:
1. Be clearly related to the question being asked
2. Provide at least one specific, actionable preference
3. Give enough information to help narrow down hotel options

Be generous in your evaluation. Simple, clear answers are often perfectly adequate.
For example: "Santa Barbara CA" is sufficient for location, "museums and beach" is sufficient for trip purpose.

Only flag answers as insufficient if they are truly vague or off-topic.
"""

# Simplified prompt template for checking answer usefulness
COHERENCE_PROMPT_TEMPLATE = """
Question: {question}
Answer: {answer}

Is this answer useful for hotel matching?
- Does it answer the question asked?
- Does it provide at least one specific preference or detail?

Respond with 'Yes' for most reasonable answers that relate to the question.
Respond with 'No' only if the answer is completely vague, off-topic, or uninformative.
"""


# Much more relaxed consistency checking
CONSISTENCY_SYSTEM_PROMPT = """
You are an AI assistant helping to evaluate hotel preferences for obvious contradictions.
Your task is to identify only CLEAR, OBVIOUS inconsistencies that would make recommendations impossible.

Examples of ACTUAL inconsistencies:
- Wanting a $50 budget but expecting luxury 5-star amenities
- Going skiing in a tropical beach destination
- Wanting a quiet retreat but also requesting to be in the middle of nightlife

Be very generous. Most travel preferences are compatible even if they seem unusual.
Santa Barbara has both beaches AND museums, boutique hotels can be mid-range, etc.
"""


# Simplified consistency prompt
CONSISTENCY_PROMPT_TEMPLATE = """
Here are the hotel preferences:

{answer_summary}

Are there any OBVIOUS, MAJOR contradictions that would make hotel recommendations impossible?

Respond with 'Yes' if the preferences are workable (even if unusual).
Respond with 'No: [brief reason]' only for clear, serious contradictions.
"""


# More helpful suggestions system prompt
SUGGESTIONS_SYSTEM_PROMPT = """
You are an AI assistant helping travelers provide more specific hotel preferences.
Your task is to generate 1-2 brief, helpful questions that encourage useful details.

Focus on practical details that would help with hotel matching:
- Specific amenities or features
- Location preferences within the destination
- Style or atmosphere preferences
- Budget considerations

Keep suggestions brief, friendly, and genuinely helpful.
"""


# Simplified suggestions prompt
SUGGESTIONS_PROMPT_TEMPLATE = """
Question: {question}
Answer: {answer}

This answer could be more specific. Generate 1-2 brief questions that would help get useful details for hotel matching.

Focus on practical specifics, not philosophical depth.
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
        answer_summary += f"{readable_q}: {answer}\n"

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


# Optional: Configuration to reduce LLM calls
VALIDATION_CONFIG = {
    "skip_coherence_for_basic_questions": True,  # Skip coherence check for obvious answers
    "minimum_answer_length": 3,  # Only check coherence if answer is very short
    "skip_consistency_until_question": 3,  # Only start consistency checking after 3 questions
}
