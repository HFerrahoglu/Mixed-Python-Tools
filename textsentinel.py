import os
import tkinter as tk
from tkinter import filedialog
from collections import Counter
from rich.console import Console
from rich.table import Table
from colorama import init

init(autoreset=True)

console = Console()
banner_text = ["""
__ __|             |     ___|                |   _)               |
   |   _ \ \ \  /  __| \___ \    _ \  __ \   __|  |  __ \    _ \  |
   |   __/  `  <   |         |   __/  |   |  |    |  |   |   __/  |
  _| \___|  _/\_\ \__| _____/  \___| _|  _| \__| _| _|  _| \___| _|
  
  x/HFerrahoglu
"""]
colors = ["yellow"]

os.system('cls' if os.name == 'nt' else 'clear')

def print_gradient_banner():
    console.print("") 
    for line, color in zip(banner_text, colors):
        console.print(f"[{color}]{line}[/]")

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select a file")
    return file_path

def list_files_in_directory():
    current_dir = os.getcwd()
    files = [f for f in os.listdir(current_dir) if os.path.isfile(f) and f.split('.')[-1] in ['txt', 'json', 'jsonl', 'md']]
    return files

def choose_file():
    files = list_files_in_directory()
    table = Table(title="Available Files in Directory", style="bold cyan")
    table.add_column("Index", style="bold magenta", width=10, justify="center")
    table.add_column("File Name", style="bold green")

    for idx, file in enumerate(files, start=1):
        table.add_row(str(idx), file)
    
    table.add_row(str(len(files) + 1), "Select file via file manager")
    console.print(table)
    console.print("[bold yellow]Press 'q' to quit.[/bold yellow]")

    choice = input("Choose a file by entering its number or 'q' to quit: ").strip().lower()
    console.print("\n")
    
    if choice == 'q':
        console.print("[bold red]Exiting...[/bold red]")
        exit()
    
    try:
        choice = int(choice)
        if 1 <= choice <= len(files):
            return files[choice - 1]
        elif choice == len(files) + 1:
            return select_file()
        else:
            console.print("[bold red]Invalid choice! Please try again.[/bold red]")
            console.print("\n")
            return None
    except ValueError:
        console.print("[bold red]Please enter a valid number or 'q' to quit![/bold red]")
        return None

def find_duplicate_sentences(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    sentence_counts = Counter()
    sentence_lines = {}

    for line_num, line in enumerate(lines, start=1):
        sentences = line.split('.')
        for sentence in sentences:
            sentence = sentence.strip().lower()
            if sentence:
                sentence_counts[sentence] += 1
                if sentence_counts[sentence] == 1:
                    sentence_lines[sentence] = line_num
    
    duplicates = {sentence: (count, sentence_lines[sentence]) for sentence, count in sentence_counts.items() if count > 1}
    
    return duplicates

def main():
    print_gradient_banner()
    while True:
        file_path = choose_file()
        
        if file_path:
            duplicates = find_duplicate_sentences(file_path)

            if duplicates:
                table = Table(title="Duplicate Sentences", style="bold cyan")
                table.add_column("Sentence", style="bold red", width=50)
                table.add_column("Repetitions", justify="center", style="bold green")
                table.add_column("Line Number", justify="center", style="bold yellow")
                
                for sentence, (count, line_num) in duplicates.items():
                    table.add_row(sentence, str(count), str(line_num))
                
                console.print(table)
            else:
                console.print("[bold green]No duplicate sentences found.[/bold green]")
            
            console.print("\n")
            console.rule("[bold yellow]End of current operation[/bold yellow]")
            console.print("\n")
        else:
            console.print("[bold red]No valid file selected![/bold red]")
            console.print("\n")

main()

