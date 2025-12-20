"""
Web Image Scraper

This script downloads all images from a specified website URL.
It handles both regular image tags and background images in CSS.
Refactored for API usage.
"""

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import time

class ImageScraper:
    def __init__(self, output_dir="images"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def is_valid_image_url(self, url):
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        return any(url.lower().endswith(ext) for ext in image_extensions)

    def download_images(self, url, progress_callback=None):
        """
        Download all images from a specified URL.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        downloaded_files = []
        
        try:
            if progress_callback:
                progress_callback({"status": "scanning", "message": f"Scanning {url}..."})

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            img_tags = soup.find_all('img')
            bg_elements = soup.find_all(lambda tag: tag.get('style') and 'background-image' in tag.get('style'))

            found_urls = set()
            
            # 1. Collect all URLs first
            for img in img_tags:
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(url, src)
                    if self.is_valid_image_url(full_url):
                        found_urls.add(full_url)

            for element in bg_elements:
                style = element.get('style')
                if 'url(' in style:
                    try:
                        bg_url = style.split('url(')[1].split(')')[0].strip("'").strip('"')
                        full_url = urljoin(url, bg_url)
                        if self.is_valid_image_url(full_url):
                            found_urls.add(full_url)
                    except:
                        pass
            
            total_images = len(found_urls)
            if progress_callback:
                progress_callback({"status": "found", "count": total_images, "message": f"Found {total_images} images."})

            # 2. Download loop
            count = 0
            for i, img_url in enumerate(found_urls):
                try:
                    filename = f"image_{count}_{os.path.basename(urlparse(img_url).path)}"
                    # Sanitize filename
                    filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).rstrip()
                    
                    if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                         filename += '.jpg'

                    filepath = os.path.join(self.output_dir, filename)

                    if progress_callback:
                        progress_callback({
                            "status": "downloading", 
                            "current": i+1, 
                            "total": total_images, 
                            "filename": filename
                        })

                    img_response = requests.get(img_url, headers=headers, timeout=10)
                    if img_response.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        
                        downloaded_files.append(filename)
                        count += 1
                        time.sleep(0.1) # Gentle delay

                except Exception as e:
                    print(f"Failed to download {img_url}: {e}")

            if progress_callback:
                progress_callback({"status": "completed", "count": count, "files": downloaded_files})
            
            return downloaded_files

        except Exception as e:
            if progress_callback:
                progress_callback({"status": "error", "error": str(e)})
            raise e
