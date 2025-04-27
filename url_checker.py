import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from urllib.parse import urljoin, urlparse
import threading
import webbrowser
import json
from datetime import datetime
import os
import contextlib

class URLCheckerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("URL Checker — /HFerrahoglu")
        self.geometry("1000x700")
        
        self.checker = URLChecker()
        self.checker.gui = self
        self.running = False
        self.table_rows = []
        
        self.setup_gui()

    def setup_gui(self):
        header_frame = ctk.CTkFrame(self, fg_color="#1a2526")
        header_frame.pack(pady=(10, 0), padx=10, fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="URL Checker",
            font=("Arial", 24, "bold"),
            text_color="white"
        ).pack(pady=10)
        
        control_frame = ctk.CTkFrame(self, fg_color="#2b3b3c")
        control_frame.pack(pady=(5, 10), padx=10, fill="x")
        
        ctk.CTkLabel(control_frame, text="Base URL:", text_color="white", font=("Arial", 12)).pack(side="left", padx=5)
        self.url_entry = ctk.CTkEntry(control_frame, width=300, placeholder_text="https://example.com", font=("Arial", 12))
        self.url_entry.pack(side="left", padx=5)
        
        self.start_btn = ctk.CTkButton(control_frame, text="Start Scraping", command=self.start_scraping, font=("Arial", 12))
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(control_frame, text="Stop Scraping", command=self.stop_scraping, state="disabled", font=("Arial", 12))
        self.stop_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(control_frame, text="Export Results", command=self.export_results, state="disabled", font=("Arial", 12))
        self.export_btn.pack(side="left", padx=5)
        
        self.loader = ctk.CTkProgressBar(control_frame, width=30, height=30, mode="indeterminate", corner_radius=15)
        self.loader.pack(side="left", padx=5)
        self.loader.set(0)
        self.loader.stop()
        self.loader.pack_forget()
        
        self.search_entry = ctk.CTkEntry(control_frame, placeholder_text="Search URLs...", width=200, font=("Arial", 12))
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_urls)
        
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.table = ctk.CTkScrollableFrame(results_frame)
        self.table.pack(fill="both", expand=True)
        
        headers = ["#", "Status", "Title", "URL", "Code", "XPath"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.table, text=header, font=("Arial", 12, "bold"), text_color="white").grid(row=0, column=i, padx=2, pady=2, sticky="w")
        
        self.log_text = ctk.CTkTextbox(self, height=150, text_color="white")
        self.log_text.pack(pady=10, padx=10, fill="x")
        
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor="w", text_color="white")
        self.status_bar.pack(fill="x", padx=10, pady=5)

    def log(self, message):
        self.log_text.insert("end", f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see("end")
        
    def start_scraping(self):
        if not self.running and self.url_entry.get():
            self.running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.export_btn.configure(state="disabled")
            self.status_bar.configure(text="Scraping in progress...")
            
            self.loader.pack(side="left", padx=5)
            self.loader.start()
            
            self.clear_table()
            self.checker.results = []
            
            thread = threading.Thread(target=self.checker.run, args=(self.url_entry.get(),))
            thread.start()
            
    def stop_scraping(self):
        if self.running:
            self.running = False
            if self.checker.driver:
                self.checker.driver.quit()
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.status_bar.configure(text="Scraping stopped")
            
            self.loader.stop()
            self.loader.pack_forget()
            
    def export_results(self):
        if self.checker.results:
            base_url_safe = self.checker.base_url.replace("http://", "").replace("https://", "").replace("/", "_")
            filename = f"{base_url_safe}_detailed_results.json"
            with open(filename, 'w') as f:
                json.dump(self.checker.results, f, indent=4)
            self.log(f"Results exported to {filename}")
            
    def clear_table(self):
        for row in self.table_rows:
            for widget in row:
                widget.destroy()
        self.table_rows = []
            
    def filter_urls(self, event):
        search_term = self.search_entry.get().lower()
        filtered_results = [r for r in self.checker.results if search_term in r['url'].lower() or 
                           search_term in r['status'].lower()]
        
        self.clear_table()
        for idx, result in enumerate(filtered_results, 1):
            self.append_result(idx, result)
            
    def append_result(self, idx, result):
        status_color = {"VALID": "#00FF00", "INVALID": "#FF0000", "UNDETECTABLE": "#FFFF00"}.get(result['status'], "#FFFFFF")
        
        row_widgets = []
        row_widgets.append(ctk.CTkLabel(self.table, text=str(idx), text_color="white"))
        row_widgets[-1].grid(row=idx, column=0, padx=2, pady=2, sticky="w")
        
        row_widgets.append(ctk.CTkLabel(self.table, text=result['status'], text_color=status_color))
        row_widgets[-1].grid(row=idx, column=1, padx=2, pady=2, sticky="w")
        
        row_widgets.append(ctk.CTkLabel(self.table, text=result['title'], text_color="white"))
        row_widgets[-1].grid(row=idx, column=2, padx=2, pady=2, sticky="w")
        
        url_btn = ctk.CTkButton(self.table, text=result['url'], command=lambda u=result['url']: webbrowser.open(u),
                              fg_color="transparent", text_color="#1E90FF", hover_color="#555555")
        url_btn.grid(row=idx, column=3, padx=2, pady=2, sticky="w")
        row_widgets.append(url_btn)
        
        row_widgets.append(ctk.CTkLabel(self.table, text=str(result['code']), text_color="white"))
        row_widgets[-1].grid(row=idx, column=4, padx=2, pady=2, sticky="w")
        
        row_widgets.append(ctk.CTkLabel(self.table, text=result['xpath'], text_color="white"))
        row_widgets[-1].grid(row=idx, column=5, padx=2, pady=2, sticky="w")
        
        self.table_rows.append(row_widgets)
        
        self.table.update()

class URLChecker:
    def __init__(self):
        self.stats = {'valid': 0, 'invalid': 0, 'undetectable': 0, 'total': 0}
        self.results = []
        self.driver = None
        self.base_url = None
        self.gui = None

    def format_timestamp(self):
        return datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    def get_path_from_url(self, url):
        parsed = urlparse(url)
        return parsed.path if parsed.path else '/'

    def get_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
        }

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(log_path=os.devnull)
        with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
            return webdriver.Chrome(service=service, options=chrome_options)

    def get_xpath(self, element):
        components = []
        child = element
        try:
            root = self.driver.find_element(By.TAG_NAME, "html")
            while child != root:
                siblings = child.find_elements(By.XPATH, f"preceding-sibling::{child.tag_name}")
                components.insert(0, f"{child.tag_name}[{len(siblings) + 1}]")
                child = child.find_element(By.XPATH, '..')
            return '//' + '/'.join(components)
        except:
            return "N/A"

    def get_css_selector(self, element):
        try:
            return self.driver.execute_script("""
                function generateSelector(el) {
                    if (el.id) return '#' + el.id;
                    if (el.className) return '.' + el.className.replace(/ /g, '.');
                    
                    let path = [];
                    while (el.nodeType === Node.ELEMENT_NODE) {
                        let selector = el.nodeName.toLowerCase();
                        if (el.className) {
                            selector += '.' + el.className.replace(/ /g, '.');
                        }
                        path.unshift(selector);
                        el = el.parentNode;
                    }
                    return path.join(' > ');
                }
                return generateSelector(arguments[0]);
            """, element)
        except:
            return "N/A"

    def check_url(self, url, title, xpath, css_selector):
        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                allow_redirects=True,
                timeout=10,
                verify=True
            )
            status_code = response.status_code
            timestamp = self.format_timestamp()
            path = self.get_path_from_url(url)

            if 200 <= status_code < 400:
                self.stats['valid'] += 1
                return {
                    'timestamp': timestamp,
                    'status': 'VALID',
                    'path': path,
                    'code': status_code,
                    'url': url,
                    'title': title,
                    'xpath': xpath,
                    'css_selector': css_selector
                }
            else:
                self.stats['invalid'] += 1
                return {
                    'timestamp': timestamp,
                    'status': 'INVALID',
                    'path': path,
                    'code': status_code,
                    'url': url,
                    'title': title,
                    'xpath': xpath,
                    'css_selector': css_selector
                }
        except requests.RequestException:
            self.stats['undetectable'] += 1
            timestamp = self.format_timestamp()
            return {
                'timestamp': timestamp,
                'status': 'UNDETECTABLE',
                'path': self.get_path_from_url(url),
                'code': 'N/A',
                'url': url,
                'title': title,
                'xpath': xpath,
                'css_selector': css_selector
            }

    def collect_urls(self, base_url):
        urls_info = []
        self.base_url = base_url
        
        self.gui.log(f"Collecting URLs from {base_url}")
        self.driver = self.setup_driver()
        try:
            self.driver.get(base_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
            
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                if not self.gui.running:
                    break
                try:
                    href = link.get_attribute('href')
                    if href and (href.startswith('http://') or href.startswith('https://')):
                        title = link.text.strip() or link.get_attribute('title') or 'No Title'
                        xpath = self.get_xpath(link)
                        css_selector = self.get_css_selector(link)
                        urls_info.append((href, title, xpath, css_selector))
                except Exception as e:
                    self.gui.log(f"Error processing link: {str(e)}")
                    continue
        except Exception as e:
            self.gui.log(f"Error during URL collection: {str(e)}")
        finally:
            self.driver.quit()
            self.driver = None
        
        return urls_info

    def run(self, base_url):
        self.results = []
        self.stats = {'valid': 0, 'invalid': 0, 'undetectable': 0, 'total': 0}
        
        urls_info = self.collect_urls(base_url)
        self.stats['total'] = len(urls_info)
        
        for idx, (url, title, xpath, css_selector) in enumerate(urls_info, 1):
            if not self.gui.running:
                break
            result = self.check_url(url, title, xpath, css_selector)
            self.results.append(result)
            self.gui.after(0, self.gui.append_result, idx, result)
            self.gui.after(0, self.gui.status_bar.configure, 
                         {"text": f"Checking - Valid: {self.stats['valid']} | Invalid: {self.stats['invalid']} | Undetectable: {self.stats['undetectable']}"})
            
        if self.gui.running:
            self.gui.log("Scraping completed")
            self.gui.after(0, self.gui.status_bar.configure, 
                         {"text": f"Completed - Valid: {self.stats['valid']} | Invalid: {self.stats['invalid']} | Undetectable: {self.stats['undetectable']}"})
            self.gui.after(0, self.gui.start_btn.configure, {"state": "normal"})
            self.gui.after(0, self.gui.stop_btn.configure, {"state": "disabled"})
            self.gui.after(0, self.gui.export_btn.configure, {"state": "normal"})
            self.gui.after(0, self.gui.loader.stop)
            self.gui.after(0, self.gui.loader.pack_forget)
        else:
            self.gui.log("Scraping stopped by user")
            self.gui.after(0, self.gui.status_bar.configure, {"text": "Scraping stopped"})
            self.gui.after(0, self.gui.loader.stop)
            self.gui.after(0, self.gui.loader.pack_forget)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = URLCheckerGUI()
    app.mainloop()