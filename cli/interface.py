"""
Updated CLI interface using LLM-powered conversation memory.
"""
from typing import Dict, List

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

from memory.simple_memory_workflow import LLMMemoryWorkflow
from cli.display import format_question, format_response

console = Console()


def run_llm_memory_cli() -> Dict:
    """
    Run the LLM memory-aware CLI interface.
    """
    console.print("[bold blue]Welcome to gatherHotelPreferences![/bold blue]")
    console.print(
        "I'll ask you 5 questions to understand your hotel preferences. "
        "I'll build on your answers as we go to understand what you're looking for.\n"
    )

    # Initialize the LLM-powered workflow
    workflow = LLMMemoryWorkflow()

    try:
        # Run through the questions
        for question_data in workflow.get_questions():
            question_id = question_data["id"]
            question_text = question_data["text"]

            console.print(format_question(question_text))

            # Get the user's answer
            try:
                console.print("[green]Your answer[/green]:", end=" ")
                answer = input()
            except EOFError:
                console.print("\n[yellow]Input interrupted. Exiting...[/yellow]")
                raise KeyboardInterrupt()

            # Validate answer using LLM with conversation context
            validated_answer, suggestions = workflow.validate_answer(
                question_id, question_text, answer
            )

            # If LLM suggests improvements, show them
            if suggestions:
                console.print("\n[yellow]Your answer could be more detailed. Consider:[/yellow]")

                for suggestion in suggestions:
                    suggestion_text = suggestion.get("text", suggestion)
                    console.print(f"[yellow]- {suggestion_text}[/yellow]")

                # Ask for an improved answer
                console.print("\n[green]Would you like to provide more details?[/green]")
                console.print(f"Current answer: [dim]{validated_answer}[/dim]")
                console.print("[green]Additional details (or press Enter to continue)[/green]:", end=" ")

                try:
                    improved_answer = input()
                    if improved_answer.strip():
                        # Update with improved answer
                        validated_answer = workflow.update_answer(
                            question_id, question_text,
                            f"{answer} {improved_answer}".strip()
                        )
                except EOFError:
                    pass  # Continue with original answer

            # Show simple feedback
            console.print(format_response("Thank you!\n"))

        # Process the completed conversation with LLM
        console.print("[bold blue]Processing your preferences...[/bold blue]")
        processed_results = workflow.process_conversation()

        # Display LLM insights
        display_llm_insights(processed_results)

        # Check consistency
        if not processed_results["is_consistent"]:
            console.print("\n[yellow]Note: I noticed some potential inconsistencies:[/yellow]")
            for issue in processed_results["consistency_issues"]:
                console.print(f"[yellow]- {issue}[/yellow]")

        console.print("\n[bold green]Thank you for completing the interview![/bold green]")
        console.print("Your preferences have been analyzed and will be used to find hotel recommendations.")

        return processed_results

    except Exception as e:
        console.print(f"[bold red]Error during interview: {str(e)}[/bold red]")
        raise


def display_llm_insights(results: Dict) -> None:
    """Display the LLM-generated insights in a nice format."""

    insights = results.get("llm_insights", {})

    if not insights or insights.get("error"):
        console.print("[yellow]Could not generate insights summary.[/yellow]")
        return

    # Create insights table
    table = Table(title="Your Hotel Preferences (LLM Analysis)")
    table.add_column("Aspect", style="cyan", width=15)
    table.add_column("Details", style="green")

    # Add insights to table
    if insights.get("destination") and insights["destination"] != "Not specified":
        table.add_row("Destination", insights["destination"])

    if insights.get("trip_type") and insights["trip_type"] != "Not specified":
        table.add_row("Trip Type", insights["trip_type"])

    if insights.get("budget") and insights["budget"] != "Not specified":
        table.add_row("Budget", insights["budget"])

    if insights.get("amenities"):
        amenities_text = ", ".join(insights["amenities"])
        table.add_row("Key Amenities", amenities_text)

    if insights.get("style") and insights["style"] != "Not specified":
        table.add_row("Hotel Style", insights["style"])

    if insights.get("activities"):
        activities_text = ", ".join(insights["activities"])
        table.add_row("Planned Activities", activities_text)

    if insights.get("requirements"):
        requirements_text = ", ".join(insights["requirements"])
        table.add_row("Special Requirements", requirements_text)

    console.print("\n")
    console.print(table)

    # Show search keywords if available
    if insights.get("search_keywords"):
        console.print(f"\n[bold]Generated search keywords:[/bold] {', '.join(insights['search_keywords'])}")

    console.print("\n")


def display_conversation_analysis(results: Dict) -> None:
    """Display detaile
