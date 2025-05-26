"""
Date validation using LLM for the travel dates question.
"""

from llm.ollama_client import get_ollama_client


def check_dates_captured(answer: str) -> bool:
    """
    Use LLM to check if the travel dates answer contains both check-in and check-out dates.

    Args:
        answer: The user's answer to the travel dates question

    Returns:
        bool: True if both dates are captured, False otherwise
    """
    client = get_ollama_client()

    system_prompt = """
    You are checking if a user's answer contains BOTH a check-in date AND a check-out date for hotel travel.

    Look for:
    - Two distinct dates (check-in and check-out)
    - Dates can be in any format (August 1, 2025 / 8/1/25 / Aug 1st, etc.)
    - Phrases like "from X to Y" or "checking in X, checking out Y"

    Respond with ONLY "YES" if both dates are present, "NO" if missing one or both dates.
    """

    user_prompt = f"""
    Does this answer contain both a check-in date AND a check-out date?

    Answer: "{answer}"

    Respond with only YES or NO.
    """

    response = client.generate(
        prompt=user_prompt,
        system_prompt=system_prompt
    )

    return "yes" in response.lower()


def extract_dates_simple(answer: str) -> dict:
    """
    Simple date extraction for later processing.

    Args:
        answer: The user's travel dates answer

    Returns:
        dict: Contains the raw answer and whether dates were detected
    """
    has_dates = check_dates_captured(answer)

    return {
        "raw_answer": answer,
        "has_both_dates": has_dates,
        "ready_for_search": has_dates
    }
