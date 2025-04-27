import cv2
import os
import tkinter as tk
from tkinter import filedialog
from rich.console import Console
from rich.table import Table
from rich.text import Text
import time

console = Console()

def print_banner():
    banner = """
__| |____________________________________________________________| |__
__   ____________________________________________________________   __
  | |                                                            | |  
  | | _____                 _       _   _             _  _______ | |  
  | ||  __ \               | |     | | (_)           (_)|__   __|| |  
  | || |__) |___  ___  ___ | |_   _| |_ _  ___  _ __  _ ___| |   | |  
  | ||  _  // _ \/ __|/ _ \| | | | | __| |/ _ \| '_ \| / __| |   | |  
  | || | \ \  __/\__ \ (_) | | |_| | |_| | (_) | | | | \__ \ |   | |  
  | ||_|  \_\___||___/\___/|_|\__,_|\__|_|\___/|_| |_|_|___/_|   | |
  | |                                   x/HFerrahoglu            | |  
__| |____________________________________________________________| |__
__   ____________________________________________________________   __
  | |                                                            | |  
    """
    console.print(Text(banner, style="bold green"))

def get_video_resolution(video_path):
    try:
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            console.print(f"[red]Video açılamadı. Lütfen dosya yolunu kontrol edin.[/red]")
            return
        
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        
        if width >= 3840:
            quality_k = "4K"
        elif width >= 2560:
            quality_k = "2.5K"
        elif width >= 1920:
            quality_k = "2K"
        else:
            quality_k = "1K veya daha düşük"
        
        if height >= 2160:
            quality_p = "2160p"
        elif height >= 1440:
            quality_p = "1440p"
        elif height >= 1080:
            quality_p = "1080p"
        elif height >= 720:
            quality_p = "720p"
        else:
            quality_p = "480p veya daha düşük"
        
        print("\n")
        console.print("—" * 50)
        print("\n")
        
        table = Table(title="Video Bilgisi", show_header=True, header_style="bold magenta")
        table.add_column("Dosya Adı", style="cyan", no_wrap=True)
        table.add_column("Çözünürlük", style="green")
        table.add_column("Kalite", style="yellow")

        table.add_row(video_name, f"{width}x{height}", f"{quality_k} ({quality_p})")
        console.print(table)
        print("\n")
        console.print("—" * 50)
        print("\n")

        video.release()
    except Exception as e:
        console.print(f"[red]Hata oluştu: {e}[/red]")
        print("\n")
        console.print("—" * 50)
        print("\n")

def select_video_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Bir video dosyası seçin", 
                                           filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov")])
    return file_path

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def ask_continue():
    while True:
        choice = console.input("[yellow]Devam etmek ister misiniz? (Evet için Enter veya e, çıkmak için q): [/yellow]").strip().lower()
        if choice == 'q':
            return False
        elif choice == '' or choice == 'e':
            return True
        else:
            console.print(f"[red]Geçersiz seçenek. Lütfen 'q' veya 'Enter' ya da 'e' girin.[/red]")


def main():
    clear_terminal()
    print_banner()

    while True:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Seçenek", style="cyan")
        table.add_column("Açıklama", style="green")

        table.add_row("1", "Bir video dosyası seç")
        table.add_row("q", "Çıkış")
        console.print(table)

        choice = console.input("Bir seçenek girin: ").strip().lower()

        if choice == '1':
            video_path = select_video_file()
            if video_path:
                get_video_resolution(video_path)
        elif choice == 'q':
            console.print(f"[yellow]Çıkılıyor...[/yellow]")
            break
        else:
            console.print(f"[red]Geçersiz seçenek. Lütfen geçerli bir seçenek girin.[/red]")

        if not ask_continue():
            console.print(f"[yellow]Çıkılıyor...[/yellow]")
            break
        else:
            clear_terminal()
            print_banner()

if __name__ == "__main__":
    main()
