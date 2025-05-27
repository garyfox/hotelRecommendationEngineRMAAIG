"""
Complete CLI interface for hotel recommendation system with conversation logging.
"""
from typing import Dict, List
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

from core.workflow import InterviewWorkflow
from cli.display import format_question, format_response, display_summary

console = Console()


def run_cli() -> Dict:
    """
    Run the CLI interface for the hotel recommendation system.

    Returns:
        Dict: Collected customer preferences
    """
    console.print("[bold blue]Welcome to gatherHotelPreferences![/bold blue]")
    console.print(
        "I'll ask you 5 questions to understand your hotel preferences. "
        "Please provide detailed answers to help find the best match.\n"
    )

    # Initialize the workflow
    workflow = InterviewWorkflow()

    # Start the interview process
    preferences = {}

    try:
        # Run through the questions
        for question_data in workflow.get_questions():
            # Display the question
            question_id = question_data["id"]
            question_text = question_data["text"]

            # Log the question
            workflow.log_question(question_id, question_text)

            console.print(format_question(question_text))

            # Get the user's answer using standard Python input instead of Rich
            try:
                # Use standard Python input to avoid backspace issues
                console.print("[green]Your answer[/green]:", end=" ")
                answer = input()
            except EOFError:
                # Handle Ctrl+D gracefully
                console.print("\n[yellow]Input interrupted. Exiting...[/yellow]")
                raise KeyboardInterrupt()

            # Validate and potentially enhance the answer
            validated_answer, suggestions = workflow.validate_answer(question_id, answer)

            # If there are suggestions to improve the answer, show them
            if suggestions:
                console.print(
                    "\n[yellow]Your answer could use more detail. Consider:[/yellow]"
                )

                for suggestion in suggestions:
                    # Check suggestion type and format accordingly
                    if isinstance(suggestion, dict) and "type" in suggestion and "text" in suggestion:
                        # New format with type and text
                        suggestion_type = suggestion["type"]
                        suggestion_text = suggestion["text"]

                        if suggestion_type == "inconsistency":
                            console.print(f"[bold red]- {suggestion_text}[/bold red]")
                        else:
                            console.print(f"[yellow]- {suggestion_text}[/yellow]")
                    else:
                        # Handle old format for backward compatibility
                        console.print(f"[yellow]- {suggestion}[/yellow]")

                # Ask for an improved answer
                console.print("[green]Would you like to provide more details?[/green]", end=" ")
                console.print(f"({answer}): ", end="")
                try:
                    improved_answer = input()
                    # If user just pressed Enter, keep the original answer
                    if not improved_answer:
                        improved_answer = answer
                except EOFError:
                    improved_answer = answer

                if improved_answer != answer:
                    # Log the revision
                    workflow.log_answer_revision(question_id, answer, improved_answer)
                    validated_answer, _ = workflow.validate_answer(
                        question_id, improved_answer
                    )

            # Store the answer
            preferences[question_id] = validated_answer

            # Provide feedback
            console.print(format_response("Thank you for your response!\n"))

        # Process the collected preferences
        processed_preferences = workflow.process_preferences(preferences)

        # Display a summary - use only the text part of processed preferences
        text_preferences = {k: data["text"] if isinstance(data, dict) and "text" in data else data
                           for k, data in processed_preferences.items()}
        display_summary(text_preferences)

        console.print(
            "\n[bold green]Thank you for completing the interview![/bold green]"
        )

        # Ask about hotel search
        console.print("\nWould you like to search for hotels with current pricing?")
        console.print("[dim](This uses the Booking.com API)[/dim]")
        search_hotels = input("Search for hotels? (y/n): ").lower().strip()

        if search_hotels in ['y', 'yes']:
            console.print("\n[blue]Searching for hotels...[/blue]")

            try:
                # Import here to avoid circular imports
                from hotel_search import search_hotels_for_session

                # Get the current session directory from workflow
                session_dir_path = workflow.get_session_directory()
                session_dir = Path(session_dir_path)

                success = search_hotels_for_session(session_dir)
                if success:
                    console.print("[green]✓ Hotel search completed! Results saved to session directory.[/green]")
                else:
                    console.print("[yellow]⚠ Hotel search completed but no results found.[/yellow]")

            except Exception as e:
                console.print(f"[red]✗ Hotel search failed: {str(e)}[/red]")

        console.print(
            "\nYour preferences have been saved and will be used to find "
            "hotel recommendations that match your needs."
        )

        return processed_preferences

    except Exception as e:
        console.print(f"[bold red]Error during interview: {str(e)}[/bold red]")
        raise
