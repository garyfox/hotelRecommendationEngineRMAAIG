"""
Modified OllamaClient with conversation logging integration
"""
import json
import time
import requests
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.status import Status

from config import OLLAMA_CONFIG


class OllamaClient:
    """
    Client for interacting with Ollama LLM with automatic conversation logging.
    """

    def __init__(self, verbose=False):
        """
        Initialize the Ollama client.

        Args:
            verbose: Whether to print debug information
        """
        self.base_url = OLLAMA_CONFIG["base_url"]
        self.model = OLLAMA_CONFIG["model"]
        self.timeout = OLLAMA_CONFIG["timeout"]
        self.verbose = verbose
        self.console = Console()

    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                interaction_type: str = "general", context: Optional[str] = None) -> str:
        """
        Generate a response from the LLM with automatic conversation logging.

        Args:
            prompt: The prompt to send to the model
            system_prompt: Optional system prompt to set context
            interaction_type: Type of interaction for logging
            context: Optional context about this interaction

        Returns:
            str: The generated response
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        if system_prompt:
            payload["system"] = system_prompt

        # Create a spinner for visual feedback
        with self.console.status(f"[bold blue]Thinking with {self.model}...", spinner="dots") as status:
            # Print debug information if verbose mode is enabled
            if self.verbose:
                self.console.print("\n[bold blue]Sending request to Ollama:[/bold blue]")
                if system_prompt:
                    self.console.print("[bold cyan]System prompt:[/bold cyan]")
                    system_display = system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt
                    self.console.print(Panel(system_display, border_style="cyan", padding=(1, 2)))
                self.console.print("[bold cyan]User prompt:[/bold cyan]")
                prompt_display = prompt[:200] + "..." if len(prompt) > 200 else prompt
                self.console.print(Panel(prompt_display, border_style="cyan", padding=(1, 2)))

            # Add a small delay to make the spinner visible
            time.sleep(0.5)

            try:
                # Update status
                status.update(status="[bold yellow]Waiting for Ollama response...")

                # Send the request
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()

                # Process response
                status.update(status="[bold green]Processing response...")
                result = response.json()
                response_text = result.get("response", "")

                # Log the interaction to conversation logger
                try:
                    from conversation.logger import get_conversation_logger
                    logger = get_conversation_logger()
                    logger.log_llm_reasoning(
                        interaction_type=interaction_type,
                        system_prompt=system_prompt or "",
                        user_prompt=prompt,
                        llm_response=response_text,
                        context=context
                    )
                except ImportError:
                    # If logging module isn't available, continue without logging
                    pass
                except Exception:
                    # If any other logging error, continue without logging
                    pass

                # Print the response if verbose mode is enabled
                if self.verbose:
                    self.console.print("[bold cyan]Ollama response:[/bold cyan]")
                    response_display = response_text[:300] + "..." if len(response_text) > 300 else response_text
                    self.console.print(Panel(response_display, border_style="green", padding=(1, 2)))
                    self.console.print()

                return response_text

            except requests.exceptions.RequestException as e:
                raise Exception(f"Error communicating with Ollama: {str(e)}")

    def is_server_running(self) -> bool:
        """
        Check if the Ollama server is running.

        Returns:
            bool: True if the server is running, False otherwise
        """
        try:
            with self.console.status("[bold blue]Checking Ollama server...", spinner="dots"):
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                running = response.status_code == 200

                if running:
                    self.console.print("[bold green]✓ Ollama server is running.[/bold green]")
                else:
                    self.console.print("[bold red]✗ Ollama server is not responding.[/bold red]")

                return running
        except requests.exceptions.RequestException:
            self.console.print("[bold red]✗ Ollama server is not running.[/bold red]")
            return False


def get_ollama_client() -> OllamaClient:
    """
    Get a configured Ollama client.

    Returns:
        OllamaClient: A configured Ollama client
    """
    verbose = True  # Could be configurable
    client = OllamaClient(verbose=verbose)

    if not client.is_server_running():
        raise Exception(
            "Ollama server is not running. "
            "Please start the Ollama server with 'ollama serve'."
        )

    return client
