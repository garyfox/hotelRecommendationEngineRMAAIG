"""
Test CLI to demonstrate conversation logging functionality
"""
from typing import Dict

from rich.console import Console
from rich.prompt import Prompt

from core.workflow import InterviewWorkflow
from cli.display import format_question, format_response, display_summary
from conversation.logger import get_conversation_logger
from vector.search import generate_search_terms

console = Console()


def run_conversation_test() -> Dict:
    """
    Run a test of the conversation logging system.

    Returns:
        Dict: Session results with file paths
    """
    # Initialize conversation logger
    logger = get_conversation_logger()

    console.print("[bold blue]Testing Conversation Logging System[/bold blue]")
    console.print(f"Session ID: [cyan]{logger.session_id}[/cyan]")
    console.print(
        "I'll ask you the hotel preference questions and log everything "
        "according to our storage schema.\n"
    )

    # Initialize the workflow
    workflow = InterviewWorkflow()
    preferences = {}

    try:
        # Run through the questions
        for question_data in workflow.get_questions():
            question_id = question_data["id"]
            question_text = question_data["text"]

            # Log the question
            logger.log_question(question_id, question_text)

            # Display the question
            console.print(format_question(question_text))

            # Get the user's answer
            try:
                console.print("[green]Your answer[/green]:", end=" ")
                answer = input()
            except EOFError:
                console.print("\n[yellow]Input interrupted. Exiting...[/yellow]")
                raise KeyboardInterrupt()

            # Log the initial response
            logger.log_user_response(question_id, answer, is_revision=False)

            # Validate and potentially enhance the answer
            validated_answer, suggestions = workflow.validate_answer(question_id, answer)

            # Handle suggestions
            if suggestions:
                # Log the suggestions
                logger.log_suggestions(question_id, suggestions)

                console.print("\n[yellow]Your answer could use more detail. Consider:[/yellow]")
                for suggestion in suggestions:
                    if isinstance(suggestion, dict):
                        suggestion_type = suggestion.get("type", "general")
                        suggestion_text = suggestion.get("text", str(suggestion))
                        if suggestion_type == "inconsistency":
                            console.print(f"[bold red]- {suggestion_text}[/bold red]")
                        else:
                            console.print(f"[yellow]- {suggestion_text}[/yellow]")
                    else:
                        console.print(f"[yellow]- {suggestion}[/yellow]")

                # Ask for an improved answer
                console.print("[green]Would you like to provide more details?[/green]", end=" ")
                console.print(f"Press Enter to keep ({answer}) or type new answer: ", end="")
                try:
                    improved_answer = input()
                    if not improved_answer.strip():
                        improved_answer = answer
                except EOFError:
                    improved_answer = answer

                if improved_answer != answer:
                    # Log the revised response
                    logger.log_user_response(question_id, improved_answer, is_revision=True)
                    validated_answer, _ = workflow.validate_answer(question_id, improved_answer)

            # Store the final answer
            preferences[question_id] = validated_answer

            # Provide feedback
            console.print(format_response("Thank you! Answer logged.\n"))

        # Generate search terms
        console.print("[bold blue]Generating search terms...[/bold blue]")
        search_terms = generate_search_terms(preferences)

        # Process preferences for vector storage
        processed_preferences = workflow.process_preferences(preferences)

        # Display summary
        text_preferences = {k: data["text"] if isinstance(data, dict) and "text" in data else data
                           for k, data in processed_preferences.items()}
        display_summary(text_preferences)

        # Show search terms
        if search_terms:
            console.print("\n[bold cyan]Generated Search Terms:[/bold cyan]")
            for category, terms in search_terms.items():
                console.print(f"[cyan]{category}:[/cyan] {', '.join(terms)}")

        # Finalize the session
        logger.finalize_session(search_terms)

        # Show session info
        session_info = logger.get_session_info()

        console.print(f"\n[bold green]Session Complete![/bold green]")
        console.print(f"[blue]Session ID:[/blue] {session_info['session_id']}")
        console.print(f"[blue]Session Directory:[/blue] {session_info['session_dir']}")
        console.print(f"\n[bold blue]Files Created:[/bold blue]")

        for file_type, file_path in session_info['files'].items():
            readable_name = file_type.replace('_', ' ').title()
            console.print(f"[blue]{readable_name}:[/blue] {file_path}")

        console.print(f"\n[bold blue]Session Stats:[/bold blue]")
        metadata = session_info['metadata']
        console.print(f"Questions: {metadata['total_questions']}")
        console.print(f"Revisions: {metadata['total_revisions']}")
        console.print(f"LLM Interactions: {metadata['llm_interactions']}")

        return session_info

    except Exception as e:
        console.print(f"[bold red]Error during conversation: {str(e)}[/bold red]")

        # Try to save what we have
        try:
            logger.finalize_session()
        except:
            pass

        raise


if __name__ == "__main__":
    try:
        session_info = run_conversation_test()
        print(f"\nTest completed successfully!")
        print(f"Check the files in: {session_info['session_dir']}")
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed: {str(e)}")
