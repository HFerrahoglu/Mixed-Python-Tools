import re
import os
from datetime import datetime
from collections import Counter
from colorama import Fore, init

init(autoreset=True)

print("Mevcut dosyalar:")
existing_files = os.listdir('.')
for idx, filename in enumerate(existing_files, start=1):
    print(f"{idx}. {filename}")

log_file_choice = input("\nKaydetmek istediğiniz log dosyasının numarasını girin: ").strip()

try:
    selected_index = int(log_file_choice) - 1
    log_filename = existing_files[selected_index]
except (IndexError, ValueError):
    print(Fore.RED + "Geçersiz dosya numarası!")
    exit()

try:
    with open(log_filename, 'r') as file:
        results = []
        ip_counter = Counter()

        for log_entry in file:
            pattern = r'(?P<ip>\S+) - - \[(?P<timestamp>.+?)\] "(?P<method>\S+) (?P<url>\S+) HTTP/(?P<http_version>\S+)" (?P<status>\d{3}) (?P<size>\d+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)" "(?P<ip2>\S+)" response-time=(?P<response_time>\S+)'
            match = re.match(pattern, log_entry)

            if match:
                log_data = match.groupdict()
                timestamp = datetime.strptime(log_data['timestamp'], '%d/%b/%Y:%H:%M:%S %z')

                print(Fore.GREEN + f"IP: {log_data['ip']}")
                print(Fore.CYAN + f"Timestamp: {timestamp}")
                print(Fore.YELLOW + f"Method: {log_data['method']}")
                print(Fore.BLUE + f"URL: {log_data['url']}")
                print(Fore.MAGENTA + f"Status: {log_data['status']}")
                print(Fore.RED + f"Size: {log_data['size']} bytes")
                print(Fore.WHITE + f"Referrer: {log_data['referrer']}")
                print(Fore.LIGHTWHITE_EX + f"User Agent: {log_data['user_agent']}")
                print(Fore.LIGHTWHITE_EX + f"Response Time: {log_data['response_time']} seconds")
                print('-' * 40)
                
                results.append(log_entry)
                ip_counter[log_data['ip']] += 1

            else:
                print("Log format hatası:", log_entry)

except FileNotFoundError:
    print(Fore.RED + f"'{log_filename}' dosyası bulunamadı!")
    exit()

print(Fore.LIGHTWHITE_EX + "\nErişim Sayıları:")
for ip, count in ip_counter.items():
    print(Fore.YELLOW + f"IP: {ip} - Erişim Sayısı: {count}")

search_term = input("\nAramak istediğiniz terimi girin: ").strip()

filtered_results = [entry for entry in results if search_term in entry]

if filtered_results:
    print(Fore.YELLOW + "\nArama Sonuçları:")
    for log_entry in filtered_results:
        print(log_entry)
else:
    print(Fore.RED + "Arama terimi ile eşleşen sonuç bulunamadı.")

print("\nKaydetmek istediğiniz dosyalar:")
for idx, filename in enumerate(existing_files, start=1):
    print(f"{idx}. {filename}")

file_choice = input("\nKaydetmek istediğiniz dosya numarasını girin (yeni dosya için 'yeni' yazın): ").strip()

if file_choice.lower() == 'yeni':
    new_filename = input("Yeni dosya adı girin (örneğin: output.txt): ").strip()
else:
    try:
        selected_index = int(file_choice) - 1
        selected_file = existing_files[selected_index]
    except (IndexError, ValueError):
        print(Fore.RED + "Geçersiz dosya numarası!")
        exit()

if file_choice.lower() == 'yeni':
    with open(new_filename, 'w') as output_file:
        for entry in filtered_results:
            output_file.write(entry)
    print(f"Sonuçlar '{new_filename}' dosyasına kaydedildi.")
else:
    with open(selected_file, 'a') as output_file:
        for entry in filtered_results:
            output_file.write(entry)
    print(f"Sonuçlar '{selected_file}' dosyasına kaydedildi.")
