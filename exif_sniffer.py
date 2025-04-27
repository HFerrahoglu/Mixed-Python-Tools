import os
import time
from PIL import Image
from exif import Image as ExifImage
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from colorama import Fore, Style, init

init(autoreset=True)
console = Console()

def setup_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

setup_terminal()

def banner():
    ascii_banner = """
    ▓█████ ▒██   ██▒ ██▓  █████▒ ██████  ███▄    █  ██▓  █████▒ █████▒▓█████  ██▀███  
    ▓█   ▀ ▒▒ █ █ ▒░▓██▒▓██   ▒▒██    ▒  ██ ▀█   █ ▓██▒▓██   ▒▓██   ▒ ▓█   ▀ ▓██ ▒ ██▒
    ▒███   ░░  █   ░▒██▒▒████ ░░ ▓██▄   ▓██  ▀█ ██▒▒██▒▒████ ░▒████ ░ ▒███   ▓██ ░▄█ ▒
    ▒▓█  ▄  ░ █ █ ▒ ░██░░▓█▒  ░  ▒   ██▒▓██▒  ▐▌██▒░██░░▓█▒  ░░▓█▒  ░ ▒▓█  ▄ ▒██▀▀█▄  
    ░▒████▒▒██▒ ▒██▒░██░░▒█░   ▒██████▒▒▒██░   ▓██░░██░░▒█░   ░▒█░    ░▒████▒░██▓ ▒██▒
    ░░ ▒░ ░▒▒ ░ ░▓ ░░▓   ▒ ░   ▒ ▒▓▒ ▒ ░░ ▒░   ▒ ▒ ░▓   ▒ ░    ▒ ░    ░░ ▒░ ░░ ▒▓ ░▒▓░
     ░ ░  ░░░   ░▒ ░ ▒ ░ ░     ░ ░▒  ░ ░░ ░░   ░ ▒░ ▒ ░ ░      ░       ░ ░  ░  ░▒ ░ ▒░
       ░    ░    ░   ▒ ░ ░ ░   ░  ░  ░     ░   ░ ░  ▒ ░ ░ ░    ░ ░       ░     ░░   ░ 
       ░  ░ ░    ░   ░               ░           ░  ░                    ░  ░   ░    
    """
    console.print(Panel.fit(ascii_banner, title="ExifSniffer", style="bold cyan", subtitle="EXIF Data Tool x/HFerrahoglu", subtitle_align="right"))

def show_exif_data(file_path):
    try:
        with open(file_path, 'rb') as img_file:
            img = ExifImage(img_file)
            if img.has_exif:
                console.print(f"\n[bold green]EXIF data for {os.path.basename(file_path)}:[/bold green]")
                table = Table(title="EXIF Information", show_header=True, header_style="bold blue")
                table.add_column("Tag", style="dim", width=30)
                table.add_column("Value", style="bold")

                for tag in img.list_all():
                    table.add_row(tag, str(img.get(tag)))

                console.print(table)
            else:
                console.print(f"[yellow]No EXIF data found in {os.path.basename(file_path)}.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error reading {os.path.basename(file_path)}: {e}[/red]")

def list_images_and_select():
    files = [f for f in os.listdir() if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if not files:
        console.print("[red]No image files found in this directory.[/red]")
        return

    console.print("[bold cyan]Select a file to view its EXIF data:[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("No", style="bold", width=5)
    table.add_column("File Name", style="bold yellow")

    for i, file in enumerate(files):
        table.add_row(str(i + 1), file)

    console.print(table)

    while True:
        selection = input(Fore.CYAN + "Select a number (or 'q' to quit): " + Style.RESET_ALL)
        if selection.lower() == 'q':
            console.print("[bold red]Exiting...[/bold red]")
            time.sleep(2)
            setup_terminal()
            break
        elif selection.isdigit() and 1 <= int(selection) <= len(files):
            selected_file = files[int(selection) - 1]
            show_exif_data(selected_file)
        else:
            console.print("[yellow]Please enter a valid number.[/yellow]")

banner()
list_images_and_select()
