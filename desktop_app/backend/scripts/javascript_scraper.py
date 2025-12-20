"""
Web JavaScript Scraper
Refactored for API usage.
"""

import requests
from bs4 import BeautifulSoup
import os
import random
from urllib.parse import urljoin, urlparse
import time

class JavascriptScraper:
    def __init__(self, output_dir="js_files"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def download_javascript(self, url, progress_callback=None):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]
        
        downloaded_files = []
        
        try:
            if progress_callback:
                progress_callback({"status": "scanning", "message": f"Scanning {url}..."})

            headers = {'User-Agent': random.choice(user_agents)}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script', src=True)
            
            total = len(scripts)
            if progress_callback:
                progress_callback({"status": "found", "count": total, "message": f"Found {total} scripts."})

            for i, script in enumerate(scripts):
                js_url = urljoin(url, script['src'])
                
                try:
                    filename = os.path.basename(urlparse(js_url).path)
                    if not filename.endswith('.js'):
                        filename = f"script_{i}.js"
                    
                    # Sanitize
                    filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).rstrip()
                    filepath = os.path.join(self.output_dir, filename)

                    if progress_callback:
                        progress_callback({
                            "status": "downloading",
                            "current": i+1,
                            "total": total,
                            "filename": filename
                        })
                    
                    js_res = requests.get(js_url, headers={'User-Agent': random.choice(user_agents)}, timeout=10)
                    if js_res.status_code == 200:
                        with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                            f.write(js_res.text)
                        downloaded_files.append(filename)
                        time.sleep(0.1)

                except Exception as e:
                    print(f"Error downloading {js_url}: {e}")

            if progress_callback:
                progress_callback({"status": "completed", "count": len(downloaded_files), "files": downloaded_files})
            
            return downloaded_files

        except Exception as e:
            if progress_callback:
                progress_callback({"status": "error", "error": str(e)})
            raise e
