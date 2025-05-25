"""
Search term generation from customer preferences.
"""
from typing import Dict, List, Set

from llm.ollama_client import get_ollama_client


# System prompt for generating search terms
SEARCH_TERMS_SYSTEM_PROMPT = """
You are an AI assistant helping to extract useful search terms from hotel preferences.
Your task is to generate a set of search terms that could be used to find hotels
matching the given preferences.

Focus on:
1. Location keywords (cities, neighborhoods, landmarks)
2. Hotel types and styles (boutique, resort, business hotel)
3. Amenities and features (pool, spa, pet-friendly)
4. Experience descriptors (luxury, family-friendly, romantic)
5. Specific requirements or constraints

Generate terms that would be found in hotel descriptions or reviews.
"""


# Prompt template for generating search terms
SEARCH_TERMS_PROMPT_TEMPLATE = """
Here are the hotel preferences provided by a customer:

{preferences_summary}

Based on these preferences, generate a list of 10-15 search terms or phrases that
would be useful for finding matching hotels in reviews and descriptions.

For each term, provide a simple category label (e.g., Location, Amenity, Style, etc.).
Format your response as a simple list with category labels:

Location: downtown
Amenity: free breakfast
Style: modern decor

Only include terms that genuinely reflect the stated preferences.
"""


def generate_search_terms(preferences: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Generate search terms from customer preferences.

    Args:
        preferences: Dictionary of question IDs to answers

    Returns:
        Dict[str, List[str]]: Dictionary mapping categories to lists of search terms
    """
    # Format the preferences into a summary
    preferences_summary = ""
    for q_id, answer in preferences.items():
        # Make the question ID more readable
        readable_q = q_id.replace("_", " ").title()
        preferences_summary += f"{readable_q}: {answer}\n\n"

    # Get the Ollama client
    client = get_ollama_client()

    # Send the prompt to the LLM
    response = client.generate(
        prompt=SEARCH_TERMS_PROMPT_TEMPLATE.format(
            preferences_summary=preferences_summary
        ),
        system_prompt=SEARCH_TERMS_SYSTEM_PROMPT
    )

    # Parse the response to extract search terms by category
    search_terms: Dict[str, List[str]] = {}

    for line in response.strip().split('\n'):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Try to parse "Category: term" format
        if ':' in line:
            parts = line.split(':', 1)
            category = parts[0].strip()
            term = parts[1].strip()

            # Add to the search terms dict
            if category not in search_terms:
                search_terms[category] = []

            search_terms[category].append(term)

    # If no structured terms were found, create a generic category
    if not search_terms:
        search_terms["General"] = [line.strip() for line in response.strip().split('\n') if line.strip()]

    return search_terms


def extract_keywords(preferences: Dict[str, str]) -> Set[str]:
    """
    Extract keyword tokens from customer preferences.

    Args:
        preferences: Dictionary of question IDs to answers

    Returns:
        Set[str]: Set of extracted keywords
    """
    # Generate search terms
    search_terms = generate_search_terms(preferences)

    # Flatten the search terms into a set of keywords
    keywords = set()
    for category, terms in search_terms.items():
        for term in terms:
            # Split multi-word terms into individual words
            words = term.lower().split()
            keywords.update(words)

    return keywords
