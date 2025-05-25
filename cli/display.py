"""
Display formatting for the CLI interface.
"""
from typing import Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def format_question(question_text: str) -> Panel:
    """
    Format a question for display in the CLI.

    Args:
        question_text: The text of the question to display

    Returns:
        Panel: A rich Panel object containing the formatted question
    """
    return Panel(
        question_text,
        title="Question",
        border_style="blue",
        padding=(1, 2),
    )


def format_response(response_text: str) -> str:
    """
    Format a system response for display in the CLI.

    Args:
        response_text: The text of the response to display

    Returns:
        str: The formatted response
    """
    return f"[italic]{response_text}[/italic]"


def display_summary(preferences: Dict) -> None:
    """
    Display a summary of the collected preferences.

    Args:
        preferences: Dictionary of processed preferences
    """
    table = Table(title="Your Hotel Preferences Summary")

    table.add_column("Question", style="cyan")
    table.add_column("Your Response", style="green")

    # Extract just the text responses for display
    for question_id, data in preferences.items():
        # Format the question ID to be more readable
        readable_question = question_id.replace("_", " ").title()

        # Get the text response (original answer)
        if isinstance(data, dict) and "text" in data:
            answer = data["text"]  # Extract the text from the processed data
        else:
            answer = str(data)  # Fallback if structure is different

        # Truncate very long answers for display
        display_answer = answer
        if len(answer) > 100:
            display_answer = answer[:97] + "..."

        table.add_row(readable_question, display_answer)

    console.print("\n")
    console.print(table)
    console.print("\n")


def display_error(error_message: str) -> None:
    """
    Display an error message in the CLI.

    Args:
        error_message: The error message to display
    """
    error_panel = Panel(
        error_message,
        title="Error",
        border_style="red",
        padding=(1, 2),
    )
    console.print(error_panel)
