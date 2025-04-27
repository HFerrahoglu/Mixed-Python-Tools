import json
import os
import time
import sys
from colorama import init, Fore, Style
import re

init(autoreset=True)

def setup_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

setup_terminal()

banner = r'''
 .--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--. 
/ .. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \
\ \/\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ \/ /
 \/ /`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'\/ / 
 / /\                                                                            / /\ 
/ /\ \        _____           _    _     _           _ ____   ___  _   _        / /\ \
\ \/ /       |_   _|   _ _ __| | _(_)___| |__       | / ___| / _ \| \ | |       \ \/ /
 \/ /          | || | | | '__| |/ / / __| '_ \   _  | \___ \| | | |  \| |        \/ / 
 / /\          | || |_| | |  |   <| \__ \ | | | | |_| |___) | |_| | |\  |        / /\ 
/ /\ \         |_| \__,_|_|  |_|\_\_|___/_| |_|  \___/|____/ \___/|_| \_|       / /\ \
\ \/ /   ____ _                          _              _____ _                 \ \/ /
 \/ /   / ___| |__   __ _ _ __ __ _  ___| |_ ___ _ __  |  ___(_)_  _____ _ __    \/ / 
 / /\  | |   | '_ \ / _` | '__/ _` |/ __| __/ _ \ '__| | |_  | \ \/ / _ \ '__|   / /\ 
/ /\ \ | |___| | | | (_| | | | (_| | (__| ||  __/ |    |  _| | |>  <  __/ |     / /\ \
\ \/ /  \____|_| |_|\__,_|_|  \__,_|\___|\__\___|_|    |_|   |_/_/\_\___|_|     \ \/ /
 \/ /                                                                            \/ / 
 / /\.--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--./ /\ 
/ /\ \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \/\ \
\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `' /
 `--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'
     x/HFerrahoglu
 
 '''

colors = [Fore.RED, Fore.RED + Style.BRIGHT, Fore.YELLOW, Fore.YELLOW + Style.BRIGHT]

def print_colored_banner(banner_text):
    lines = banner_text.splitlines()
    
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        print(color + line)
        time.sleep(0.1)

print_colored_banner(banner)

input_dir = "json_files"
output_dir = "corrected_json_files"

os.makedirs(output_dir, exist_ok=True)

def fix_turkish_characters(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    data_str = json.dumps(data, ensure_ascii=False, indent=4)
    
    data_str = re.sub(r'\\n', ' ', data_str)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(data_str)

def loading_animation(text="Processing", duration=5):
    chars = "/—\\|"
    for i in range(duration):
        sys.stdout.write(Fore.YELLOW + f"\r{text}... {chars[i % len(chars)]}")
        sys.stdout.flush()
        time.sleep(0.1)

json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

if not json_files:
    print(Fore.RED + "No JSON files found in the input directory.")
    sys.exit(1)

for i, filename in enumerate(json_files):
    input_file = os.path.join(input_dir, filename)
    output_file = os.path.join(output_dir, filename)

    loading_animation(f"Processing {filename}")

    fix_turkish_characters(input_file, output_file)

    sys.stdout.write(Fore.GREEN + f"\r{filename} fixed and saved to {output_file}\n")
    sys.stdout.flush()

print(Fore.CYAN + "\nAll files have been processed successfully!")

