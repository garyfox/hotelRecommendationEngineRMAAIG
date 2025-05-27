"""
Suggestion generation for improving answers.
"""
from typing import List

from llm.ollama_client import get_ollama_client
from llm.prompt_templates import get_suggestions_prompt
from questions.question_bank import get_question_by_id


def generate_suggestions(question_id: str, answer: str) -> List[str]:
    """
    Generate suggestions to improve an answer.

    Args:
        question_id: The ID of the question being answered
        answer: The answer that needs improvement

    Returns:
        List[str]: List of suggestions for improving the answer
    """
    # Get the question text
    question = get_question_by_id(question_id)["text"]

    # Get the Ollama client
    client = get_ollama_client()

    # Get the prompt for generating suggestions
    prompt_data = get_suggestions_prompt(question, answer)

    # Send the prompt to the LLM with logging context
    response = client.generate(
        prompt=prompt_data["user"],
        system_prompt=prompt_data["system"],
        interaction_type="suggestion_generation",
        context=f"Generating suggestions for question: {question_id}"
    )

    # Parse the suggestions from the response
    suggestions = []

    # Split the response into lines and look for numbered or bullet points
    lines = response.strip().split('\n')
    for line in lines:
        line = line.strip()

        # Check for numbered lists (1., 2., etc.)
        if line and (line[0].isdigit() and line[1:].startswith('. ') or
                    line.startswith('- ') or
                    line.startswith('* ')):
            # Remove the list marker and any trailing punctuation
            suggestion = line[line.find(' ')+1:].rstrip('.:;,')
            suggestions.append(suggestion)

    # If we couldn't detect any formatted suggestions, just return the whole response
    if not suggestions and response.strip():
        # Limit to a reasonable length and add as a single suggestion
        suggestions = [response.strip()[:100]]

    # Limit to at most 2 suggestions
    return suggestions[:2]
