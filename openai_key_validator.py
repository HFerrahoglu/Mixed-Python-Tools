from openai import OpenAI, AuthenticationError
from colorama import init
from rich.console import Console
import os

os.system('cls' if os.name == 'nt' else 'clear')
init(autoreset=True)
console = Console()

banner_text = """
░█▀█░█▀█░█▀▀░█▀█░█▀█░▀█▀░░░█▀█░█▀█░▀█▀░░░█░█░█▀▀░█░█░░░▀█▀░█▀▀░█▀▀░▀█▀
░█░█░█▀▀░█▀▀░█░█░█▀█░░█░░░░█▀█░█▀▀░░█░░░░█▀▄░█▀▀░░█░░░░░█░░█▀▀░▀▀█░░█░
░▀▀▀░▀░░░▀▀▀░▀░▀░▀░▀░▀▀▀░░░▀░▀░▀░░░▀▀▀░░░▀░▀░▀▀▀░░▀░░░░░▀░░▀▀▀░▀▀▀░░▀░
                                      x/HFerrahoglu
"""
console.print(banner_text, style="yellow")

api_key = input("Please enter your OpenAI API key: ")

client = OpenAI(api_key=api_key)

try:
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
    )
    console.print("[bold green]API key is valid. Request successful.[/bold green]")

except AuthenticationError:
    console.print("[bold red]Invalid API key. Please check and try again.[/bold red]")
except Exception as e:
    console.print(f"[bold red]An error occurred: {str(e)}[/bold red]")