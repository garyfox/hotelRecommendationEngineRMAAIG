"""
Modified OllamaClient in llm/ollama_client.py with visual status indicators
"""
import json
import time
import requests
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.spinner import Spinner

from config import OLLAMA_CONFIG


class OllamaClient:
    """
    Client for interacting with Ollama LLM.
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
        self.console = Console()  # Initialize console once

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the model
            system_prompt: Optional system prompt to set context

        Returns:
            str: The generated response

        Raises:
            Exception: If there's an error communicating with Ollama
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
                    self.console.print(Panel(system_prompt, border_style="cyan", padding=(1, 2)))

                self.console.print("[bold cyan]User prompt:[/bold cyan]")
                self.console.print(Panel(prompt, border_style="cyan", padding=(1, 2)))

            # Add a small delay to make the spinner visible
            time.sleep(0.5)

            try:
                # Update status to show we're waiting for the response
                status.update(status="[bold yellow]Waiting for Ollama response...")

                # Send the request
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()

                # Update status to show we're processing the response
                status.update(status="[bold green]Processing response...")

                result = response.json()
                response_text = result.get("response", "")

                # Print the response if verbose mode is enabled
                if self.verbose:
                    self.console.print("[bold cyan]Ollama response:[/bold cyan]")
                    self.console.print(Panel(response_text, border_style="green", padding=(1, 2)))
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

    Raises:
        Exception: If the Ollama server is not running
    """
    # Enable verbose mode by checking a config or environment variable
    # For simplicity, we'll just set it to True for now
    verbose = True  # You could also use an environment variable or config setting

    client = OllamaClient(verbose=verbose)

    if not client.is_server_running():
        raise Exception(
            "Ollama server is not running. "
            "Please start the Ollama server with 'ollama serve'."
        )

    return client
