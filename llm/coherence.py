"""
Functions for checking answer coherence and logical consistency.
"""
from typing import Dict, Tuple, Optional

from llm.ollama_client import get_ollama_client
from llm.prompt_templates import get_coherence_prompt, get_consistency_prompt
from questions.question_bank import get_question_by_id


# System prompt for logical consistency checking
CONSISTENCY_SYSTEM_PROMPT = """
You are an AI assistant helping to evaluate the logical consistency of hotel preferences.
Your task is to determine if the answers to different questions are logically consistent with each other.
For example, wanting a budget hotel but expecting 5-star amenities would be inconsistent.
Wanting to go skiing but choosing a tropical beach destination would be inconsistent.
"""


def check_coherence(question_id: str, answer: str) -> bool:
    """
    Check if an answer is coherent, detailed, and useful.

    Args:
        question_id: The ID of the question being answered
        answer: The answer to check

    Returns:
        bool: True if the answer is coherent, False otherwise
    """
    # Short answers are automatically considered not coherent enough
    if len(answer) < 10:
        return False

    # Get the question text with safety check
    question_obj = get_question_by_id(question_id)
    if question_obj is None:
        # Handle the case where question is not found
        return False

    question_text = question_obj["text"]

    # Get the Ollama client
    client = get_ollama_client()

    # Get the prompt for coherence checking
    prompt_data = get_coherence_prompt(question_text, answer)

    # Send the prompt to the LLM
    response = client.generate(
        prompt=prompt_data["user"],
        system_prompt=prompt_data["system"]
    )

    # Check if the response indicates the answer is coherent
    return "yes" in response.lower()


def check_logical_consistency(answers: Dict[str, str]) -> Tuple[bool, Optional[str]]:
    """
    Check if the collected answers are logically consistent with each other.

    Args:
        answers: Dictionary of question IDs to answers

    Returns:
        Tuple[bool, Optional[str]]:
            - Boolean indicating if answers are consistent
            - String explaining inconsistency (if any)
    """
    # If there's only one answer, it's consistent by default
    if len(answers) <= 1:
        return True, None

    # Get the Ollama client
    client = get_ollama_client()

    # Update the consistency prompt template to request an explanation
    CONSISTENCY_PROMPT_TEMPLATE = """
    Here are the answers provided to hotel preference questions:

    {answer_summary}

    Are these preferences logically consistent with each other?
    If YES, respond with just 'Yes'.
    If NO, respond with 'No: ' followed by a brief explanation of the inconsistency.
    """

    # Format the answers into a summary
    answer_summary = ""
    for q_id, answer in answers.items():
        # Make the question ID more readable
        readable_q = q_id.replace("_", " ").title()
        answer_summary += f"{readable_q}: {answer}\n\n"

    # Send the prompt to the LLM
    response = client.generate(
        prompt=CONSISTENCY_PROMPT_TEMPLATE.format(answer_summary=answer_summary),
        system_prompt=CONSISTENCY_SYSTEM_PROMPT
    )

    # Parse the response
    response = response.strip().lower()

    if response.startswith("yes"):
        return True, None
    elif response.startswith("no:"):
        # Extract the explanation part
        explanation = response[3:].strip()
        return False, explanation
    else:
        # Default case if response doesn't match expected format
        return "yes" in response, None

    decision = "COHERENT = True" if "yes" in response.lower() else "COHERENT = False"

    # The ollama client will automatically log, but you can add the decision context:
    response = client.generate(
        prompt=prompt_data["user"],
        system_prompt=prompt_data["system"],
        interaction_type="coherence_check",
        context=f"Checking coherence for question: {question_id}"
    )

    # Then manually log the decision if needed:
    try:
        from conversation.logger import get_conversation_logger
        logger = get_conversation_logger()
        logger.log_llm_reasoning(
            interaction_type="coherence_decision",
            system_prompt="",
            user_prompt="",
            llm_response=f"Decision: {decision}",
            context=f"Final coherence decision for {question_id}",
            decision=decision
        )
    except ImportError:
        pass
