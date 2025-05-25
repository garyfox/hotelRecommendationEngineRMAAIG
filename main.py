#!/usr/bin/env python3
"""
Main entry point for the hotel recommendation system.
"""
import sys
from pathlib import Path

# Add project root to Python path to allow imports from modules
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

import click
from rich.console import Console

from cli.interface import run_cli
from config import CLI_CONFIG

console = Console()


@click.group()
@click.version_option(CLI_CONFIG["app_version"])
def app():
    """gatherHotelPreferences - An LLM-powered hotel preference collection tool."""
    pass


@app.command()
def interview():
    """Start the hotel preference interview process."""
    console.print("\n[bold green]Starting Hotel Preference Interview[/bold green]")
    try:
        run_cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interview interrupted by user. Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)


@app.command()
def setup():
    """Set up the application environment."""
    console.print("\n[bold green]Setting up environment...[/bold green]")
    # Future implementation for setup tasks like downloading models, etc.
    console.print("[green]Setup complete![/green]")


if __name__ == "__main__":
    app()
