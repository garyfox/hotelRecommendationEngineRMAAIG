"""
Complete CLI interface for hotel recommendation system - WITH CLAUDE INTEGRATION.
Nuclear Option: Pure Python input() with Rich only for display.
"""
from typing import Dict, List
from pathlib import Path
import sys

from rich.console import Console

from core.workflow import InterviewWorkflow
from cli.display import format_question, format_response, display_summary

console = Console()


def safe_input(prompt_text: str) -> str:
    """
    True separation: Rich for display, pure input() on clean line.

    Args:
        prompt_text: Text to display as prompt

    Returns:
        str: User input
    """
    # Rich displays the prompt on its own line
    console.print(f"[green]{prompt_text}[/green]")

    # Pure input() on a completely fresh line
    try:
        user_input = input("> ")  # Simple prompt on clean line
        return user_input.strip()
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]Input interrupted. Exiting...[/yellow]")
        raise KeyboardInterrupt()


def safe_yes_no_input(prompt_text: str, default: str = "n") -> bool:
    """
    Yes/no input with complete line separation.

    Args:
        prompt_text: Question to ask
        default: Default answer if user just presses Enter

    Returns:
        bool: True for yes, False for no
    """
    while True:
        # Rich displays the question
        console.print(f"[cyan]{prompt_text}[/cyan] [dim](y/n, default: {default})[/dim]")

        # Pure input on fresh line
        try:
            response = input("> ").strip().lower()

            # Handle empty input (just Enter)
            if not response:
                response = default.lower()

            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                console.print("[yellow]Please answer y or n[/yellow]")
                continue

        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Input interrupted. Exiting...[/yellow]")
            raise KeyboardInterrupt()


def run_cli() -> Dict:
    """
    Run the CLI interface for the hotel recommendation system.
    INCLUDES: Claude analysis integration after hotel search.

    Returns:
        Dict: Collected customer preferences
    """
    console.print("[bold blue]Welcome to gatherHotelPreferences![/bold blue]")
    console.print(
        "I'll ask you 6 questions to understand your hotel preferences. "
        "Please provide detailed answers to help find the best match.\n"
    )

    # Initialize the workflow
    workflow = InterviewWorkflow()

    # Start the interview process
    preferences = {}

    try:
        # Run through the questions
        for question_data in workflow.get_questions():
            question_id = question_data["id"]
            question_text = question_data["text"]

            # Log the question
            workflow.log_question(question_id, question_text)

            # Display the question using Rich formatting
            console.print(format_question(question_text))

            # Get user's answer using NUCLEAR OPTION - pure Python input
            answer = safe_input("Your answer:")

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
                        suggestion_type = suggestion["type"]
                        suggestion_text = suggestion["text"]

                        if suggestion_type == "inconsistency":
                            console.print(f"[bold red]- {suggestion_text}[/bold red]")
                        else:
                            console.print(f"[yellow]- {suggestion_text}[/yellow]")
                    else:
                        # Handle old format for backward compatibility
                        console.print(f"[yellow]- {suggestion}[/yellow]")

                # Ask for an improved answer using nuclear option
                console.print(f"\n[dim]Current answer: {answer}[/dim]")
                improved_answer = safe_input("Would you like to provide more details? (press Enter to keep current answer):")

                # If user just pressed Enter, keep the original answer
                if not improved_answer:
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

        # Ask about hotel search using nuclear option
        console.print("\n[blue]Would you like to search for hotels with current pricing?[/blue]")
        console.print("[dim](This uses the Booking.com API)[/dim]")

        search_hotels = safe_yes_no_input("Search for hotels?", default="y")

        session_dir = None

        if search_hotels:
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

                    # Show results file location
                    results_file = session_dir / "hotel_results.txt"
                    if results_file.exists():
                        console.print(f"[blue]📄 Results saved to:[/blue] {results_file}")

                        # Ask if user wants to see results preview
                        show_preview = safe_yes_no_input("Show a preview of the results?", default="y")
                        if show_preview:
                            try:
                                with open(results_file, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    console.print("\n[bold cyan]Hotel Search Results Preview:[/bold cyan]")
                                    # Show first 15 lines
                                    for line in lines[:15]:
                                        console.print(line.rstrip())
                                    if len(lines) > 15:
                                        console.print(f"[dim]... and {len(lines) - 15} more lines in the full results file[/dim]")
                            except Exception as e:
                                console.print(f"[yellow]Could not preview results: {str(e)}[/yellow]")
                else:
                    console.print("[yellow]⚠ Hotel search completed but no results found.[/yellow]")

            except Exception as e:
                console.print(f"[red]✗ Hotel search failed: {str(e)}[/red]")
                console.print("[dim]You can try running the search again later.[/dim]")

        # NEW: Claude Analysis Integration
        if session_dir and search_hotels:
            console.print("\n" + "="*60)
            console.print("[bold magenta]🧠 CLAUDE AI ANALYSIS AVAILABLE[/bold magenta]")
            console.print("[magenta]Get expert psychological analysis of your hotel preferences[/magenta]")
            console.print("[dim]Uses Claude Sonnet 4 to read between the lines and provide brutally honest recommendations[/dim]")

            # Check if ANTHROPIC_API_KEY is available
            import os
            has_api_key = bool(os.getenv('ANTHROPIC_API_KEY'))

            if not has_api_key:
                console.print("\n[yellow]⚠ Claude analysis requires ANTHROPIC_API_KEY environment variable[/yellow]")
                console.print("[dim]Set your API key: export ANTHROPIC_API_KEY='your_key_here'[/dim]")
                console.print("[dim]Get your API key from: https://console.anthropic.com/[/dim]")
            else:
                get_claude_analysis = safe_yes_no_input("Get Claude's expert analysis of your preferences?", default="y")

                if get_claude_analysis:
                    console.print("\n[magenta]🧠 Sending your conversation to Claude for analysis...[/magenta]")
                    console.print("[dim]This may take 10-30 seconds[/dim]")

                    try:
                        # Import and run Claude analysis
                        from anthropic.client import analyze_session_with_claude

                        analysis_result = analyze_session_with_claude(session_dir)

                        console.print("[green]✓ Claude analysis completed![/green]")

                        # Show where analysis was saved
                        analysis_file = session_dir / "claude_analysis.txt"
                        console.print(f"[magenta]📄 Analysis saved to:[/magenta] {analysis_file}")

                        # Ask if user wants to see the analysis
                        show_analysis = safe_yes_no_input("Show Claude's analysis now?", default="y")

                        if show_analysis:
                            try:
                                with open(analysis_file, 'r', encoding='utf-8') as f:
                                    analysis_content = f.read()

                                console.print("\n" + "="*60)
                                console.print("[bold magenta]CLAUDE'S EXPERT ANALYSIS[/bold magenta]")
                                console.print("="*60)

                                # Display the analysis (could be long, so show it all)
                                console.print(analysis_content)

                                console.print("\n" + "="*60)
                                console.print("[magenta]End of Claude Analysis[/magenta]")

                            except Exception as e:
                                console.print(f"[yellow]Could not display analysis: {str(e)}[/yellow]")
                                console.print(f"[dim]You can read the full analysis at: {analysis_file}[/dim]")

                        else:
                            console.print(f"[dim]You can read the full analysis anytime at: {analysis_file}[/dim]")

                    except Exception as e:
                        console.print(f"[red]✗ Claude analysis failed: {str(e)}[/red]")
                        console.print("[dim]The hotel search results are still available in your session directory[/dim]")

        console.print(
            "\nYour preferences have been saved and will be used to find "
            "hotel recommendations that match your needs."
        )

        # Show session info
        session_info = workflow.logger.get_session_info()
        console.print(f"\n[dim]Session saved to: {session_info['session_dir']}[/dim]")

        return processed_preferences

    except KeyboardInterrupt:
        console.print("\n[yellow]Interview interrupted by user. Your progress has been saved.[/yellow]")
        return preferences
    except Exception as e:
        console.print(f"[bold red]Error during interview: {str(e)}[/bold red]")
        raise


# Additional helper for any other modules that might need safe input
def get_safe_input(prompt: str, allow_empty: bool = False) -> str:
    """
    Global safe input function for use throughout the application.

    Args:
        prompt: Text to show user
        allow_empty: Whether to allow empty responses

    Returns:
        str: User input
    """
    while True:
        result = safe_input(prompt)

        if not allow_empty and not result.strip():
            console.print("[yellow]Please provide an answer.[/yellow]")
            continue

        return result


if __name__ == "__main__":
    # Test the nuclear option with Claude integration
    try:
        result = run_cli()
        print("CLI completed successfully!")
    except KeyboardInterrupt:
        print("CLI interrupted.")
