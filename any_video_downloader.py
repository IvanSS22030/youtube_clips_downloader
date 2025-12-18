"""
Any Video Downloader

This script detects videos from various websites, shows their quality and file sizes,
and allows you to choose which ones to download.

Dependencies:
    - yt-dlp: For downloading videos from various platforms
    - requests: For web requests
    - beautifulsoup4: For HTML parsing

Author: IvanSS22030
Date: May 2025
"""

import yt_dlp
import os
import requests
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
import time

try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class VideoDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def format_size(self, size_bytes):
        """Convert bytes to human readable format"""
        if size_bytes is None:
            return "Unknown"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def get_video_info(self, url):
        """Extract video information from URL"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Analyzing URL: {url}")
                info = ydl.extract_info(url, download=False)

                if info is None:
                    # Fallback to Selenium if available
                    if SELENIUM_AVAILABLE:
                         print("Standard detection failed. Attempting fallback with Selenium...")
                         return self._get_video_info_selenium(url)
                    return None

                # Handle playlists
                if 'entries' in info:
                    videos = []
                    for entry in info['entries']:
                        if entry:
                            videos.append(self._process_video_entry(entry))
                    return videos
                else:
                    return [self._process_video_entry(info)]

        except Exception as e:
            print(f"Error extracting video info: {str(e)}")
            # Fallback to Selenium if available
            if SELENIUM_AVAILABLE:
                print("Attempting fallback with Selenium...")
                return self._get_video_info_selenium(url)
            return None

    def _get_video_info_selenium(self, url):
        """Fallback method using Selenium to detect video frames"""
        if not SELENIUM_AVAILABLE:
            return None

        # Retry loop to handle session poisoning/redirects
        max_retries = 3
        for attempt in range(max_retries):
            print(f"Starting browser automation for: {url} (Attempt {attempt+1}/{max_retries})")
            
            # Configure options
            if UC_AVAILABLE:
                options = uc.ChromeOptions()
            else:
                options = Options()
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                options.add_experimental_option('excludeSwitches', ['enable-logging'])

            # Enable Performance Logging to sniff network for m3u8/mp4
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            
            # Block popups/ads
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.popups": 2,
                "profile.managed_default_content_settings.ads": 2,
                "profile.default_content_setting_values.popups": 2,
                "profile.content_settings.exceptions.automatic_downloads.*.setting": 2,
            }
            options.add_experimental_option("prefs", prefs)

            driver = None
            try:
                if UC_AVAILABLE:
                    print("Using undetected-chromedriver for better bypass...")
                    driver = uc.Chrome(options=options)
                else:
                    driver = webdriver.Chrome(options=options)
                
                # Enable Network domain for CDP
                driver.execute_cdp_cmd('Network.enable', {})
                # Block known Redirect/Ad domains
                driver.execute_cdp_cmd('Network.setBlockedURLs', {
                    "urls": [
                        "*go.msdirectsa.com*", 
                        "*koviral.xyz*", 
                        "*doubleclick.net*", 
                        "*adservice.google.com*",
                        "*histats.com*",
                        "*popads.net*",
                        "*msdirectsa.com*", 
                        "*.xyz",
                        "*clickid*"
                    ]
                })

                driver.get(url)
                
                # Smart wait for any interactive elements or iframes
                # If using UC, give it a moment for Cloudflare/Redirects to settle
                if UC_AVAILABLE:
                    time.sleep(5)
                    
                wait = WebDriverWait(driver, 15)
                
                # Anti-Redirect / Malware check
                # Wait a bit to see if a redirect happens
                time.sleep(5)
                if "cuevana" not in driver.current_url:
                    print(f"Malware redirect detected ({driver.current_url}). Terminating poisoned session...")
                    driver.quit()
                    driver = None
                    time.sleep(2)
                    continue # Try again with new driver

                # Strategy 1: Look for "Latino" / "Español" buttons common on streaming sites
                try:
                    print("Scanning for video source buttons...")
                    # Generic text search for common player buttons
                    buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Latino') or contains(text(), 'Español') or contains(text(), 'Subtitulado') or contains(text(), 'Source')]")
                    
                    visible_buttons = [b for b in buttons if b.is_displayed()]
                    print(f"Found {len(visible_buttons)} visible interaction candidates.")
                    
                    # Click the first visible one
                    for btn in visible_buttons:
                        print(f"Attempting interaction with: '{btn.text[:30]}...'")
                        
                        # Scroll to it
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(1)
                        
                        # Anti-overlay click strategy: Click, wait, if no iframe, click again
                        try:
                            btn.click()
                        except:
                             driver.execute_script("arguments[0].click();", btn)
                        
                        print("Clicked first time. Waiting...")
                        time.sleep(3)
                        
                        # Check if iframe appeared
                        if not driver.find_elements(By.TAG_NAME, "iframe"):
                            print("No iframe yet. Clicking again (handling potential overlay)...")
                            try:
                                btn.click()
                            except:
                                driver.execute_script("arguments[0].click();", btn)
                            time.sleep(3)
                        
                        # If we found iframes, we can stop clicking other buttons
                        if driver.find_elements(By.TAG_NAME, "iframe"):
                            print("Iframe detected after interaction.")
                            break

                except Exception as e:
                    print(f"Button interaction skipped: {e}")

                # Strategy 2: Wait for iframes to populate
                try:
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
                except:
                    print("No iframes detected immediately.")
                    # Save screenshot for debug
                    timestamp = datetime.now().strftime('%H%M%S')
                    screenshot_path = f"debug_failed_detection_{timestamp}.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"saved debug screenshot to {screenshot_path}")

                # Extract all iframe SRCs
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                video_urls = []
                
                for frame in iframes:
                    src = frame.get_attribute("src")
                    print(f"DEBUG: Found iframe src: {src}") 
                    if src and src.startswith("http"):
                        # Filter out common ad/tracker frames if possible, but for now just gather
                        video_urls.append(src)

                if not video_urls:
                    print("No video iframes found by Selenium. Retrying session...")
                    driver.quit()
                    driver = None
                    continue

                print(f"Selenium found {len(video_urls)} potential video frames.")
                
                # Deep Extraction: Navigate to the found streams to get the real video link
                final_video_urls = []
                
                for v_url in video_urls:
                    print(f"Deep scraping stream: {v_url}")
                    try:
                        # Navigate to the embed URL
                        driver.get(v_url)
                        time.sleep(3)
                        
                        # Look for video tag
                        try:
                            video_tags = driver.find_elements(By.TAG_NAME, "video")
                            for v in video_tags:
                                src = v.get_attribute("src")
                                if src:
                                    print(f"Found direct video source: {src}")
                                    final_video_urls.append(src)
                                    
                            # Also check for 'sources' in script tags if video tag missing
                            # (omitted for brevity, video tag is usually present on these players)
                        except:
                            pass
                            
                        # Also keep the original embed URL as a backup
                        final_video_urls.append(v_url)
                        
                    except Exception as e:
                        print(f"Deep scrape failed for {v_url}: {e}")
                        final_video_urls.append(v_url)

                # NETWORK SNIFFING: Scan performance logs for m3u8/mp4 requests
                print("Sniffing network traffic for media files...")
                try:
                    logs = driver.get_log("performance")
                    for entry in logs:
                        try:
                            message = json.loads(entry["message"])["message"]
                            if "Network.responseReceived" in message["method"]:
                                params = message.get("params", {})
                                resp = params.get("response", {})
                                url = resp.get("url", "")
                                
                                if ".m3u8" in url or ".mp4" in url:
                                    print(f"Intercepted media URL: {url}")
                                    # Prioritize these over the wrapper URLs
                                    final_video_urls.insert(0, url)
                        except Exception as inner_e:
                            # Ignore individual malformed log entries
                            continue
                except Exception as e:
                    print(f"Log sniffing failed: {e}")

                # Deduplicate
                final_video_urls = list(set(final_video_urls))

                # Feed found URLs back into yt-dlp to get actual metadata
                all_videos = []
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                }

                for v_url in final_video_urls:
                    try:
                        print(f"Analyzing extracted stream: {v_url}")
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(v_url, download=False)
                            if info:
                                if 'entries' in info:
                                    for entry in info['entries']:
                                        all_videos.append(self._process_video_entry(entry))
                                else:
                                    all_videos.append(self._process_video_entry(info))
                    except Exception as e:
                        # Only define manual entry if it's the original embed link.
                        # If it was a direct link (mp4) and failed, it might be expired/protected.
                        print(f"Stream not supported natively: {v_url}")
                        manual_entry = {
                            'title': f"Detected Video Stream ({v_url[:30]}...)",
                            'duration': 0,
                            'uploader': 'Unknown',
                            'upload_date': datetime.now().strftime('%Y%m%d'),
                            'view_count': 0,
                            'url': v_url,
                            'formats': [{
                                'format_id': 'manual',
                                'ext': 'mp4', # Assume mp4 for direct links
                                'quality': 'Manual/Direct',
                                'filesize': 0,
                                'vcodec': 'unknown',
                                'acodec': 'unknown',
                                'fps': 0,
                                'resolution': 'Unknown',
                                'format_note': 'Direct Link',
                                'protocol': 'https'
                            }]
                        }
                        all_videos.append(manual_entry)
                
                if not all_videos:
                    print("No supported videos found from the extracted frames.")
                    return None
                
                return all_videos

            except Exception as e:
                print(f"Selenium fallback failed on attempt {attempt+1}: {str(e)}")
            finally:
                if driver:
                    driver.quit()

        return None

    def _process_video_entry(self, info):
        """Process individual video entry"""
        video_data = {
            'title': info.get('title', 'Unknown Title'),
            'duration': info.get('duration', 0),
            'uploader': info.get('uploader', 'Unknown'),
            'upload_date': info.get('upload_date', ''),
            'view_count': info.get('view_count', 0),
            'url': info.get('webpage_url', info.get('url', '')),
            'formats': []
        }

        # Process available formats
        if 'formats' in info and info['formats']:
            for fmt in info['formats']:
                # Skip metadata-only formats
                if fmt.get('vcodec') != 'none' or fmt.get('acodec') != 'none':
                    format_info = {
                        'format_id': fmt.get('format_id', ''),
                        'ext': fmt.get('ext', 'unknown'),
                        'quality': self._get_quality_description(fmt),
                        'filesize': fmt.get('filesize') or fmt.get('filesize_approx'),
                        'vcodec': fmt.get('vcodec', 'none'),
                        'acodec': fmt.get('acodec', 'none'),
                        'fps': fmt.get('fps'),
                        'resolution': f"{fmt.get('width', '?')}x{fmt.get('height', '?')}" if fmt.get('width') else None,
                        'format_note': fmt.get('format_note', ''),
                        'protocol': fmt.get('protocol', 'unknown')
                    }
                    video_data['formats'].append(format_info)

        # Sort formats by quality (best first)
        video_data['formats'].sort(key=lambda x: (
            x['filesize'] or 0,
            int(x['resolution'].split('x')[
                1]) if x['resolution'] and 'x' in x['resolution'] and x['resolution'].split('x')[1].isdigit() else 0
        ), reverse=True)

        return video_data

    def _get_quality_description(self, fmt):
        """Generate quality description for format"""
        quality_parts = []

        # Resolution
        if fmt.get('height'):
            quality_parts.append(f"{fmt['height']}p")
        elif fmt.get('width'):
            quality_parts.append(f"{fmt['width']}w")

        # FPS
        if fmt.get('fps'):
            quality_parts.append(f"{fmt['fps']}fps")

        # Video codec
        if fmt.get('vcodec') and fmt['vcodec'] != 'none':
            vcodec = fmt['vcodec'].split('.')[0]  # Remove profile info
            quality_parts.append(vcodec)

        # Audio codec
        if fmt.get('acodec') and fmt['acodec'] != 'none':
            acodec = fmt['acodec'].split('.')[0]  # Remove profile info
            if fmt.get('vcodec') == 'none':  # Audio only
                quality_parts.append(f"audio-{acodec}")
            else:
                quality_parts.append(acodec)

        # Format note
        if fmt.get('format_note'):
            quality_parts.append(fmt['format_note'])

        return ' | '.join(quality_parts) if quality_parts else 'Unknown Quality'

    def display_video_info(self, videos):
        """Display video information in a formatted way"""
        if not videos:
            print("No videos found!")
            return

        print("\n" + "="*80)
        print("DETECTED VIDEOS")
        print("="*80)

        for i, video in enumerate(videos, 1):
            print(f"\n[{i}] {video['title']}")
            print(f"    Uploader: {video['uploader']}")
            print(f"    Duration: {self._format_duration(video['duration'])}")
            print(
                f"    Views: {video['view_count']:,}" if video['view_count'] else "    Views: Unknown")
            print(f"    URL: {video['url']}")

            if video['formats']:
                print(f"    Available formats ({len(video['formats'])}):")
                # Show top 10 formats
                for j, fmt in enumerate(video['formats'][:10], 1):
                    size_str = self.format_size(fmt['filesize'])
                    print(
                        f"      [{j}] {fmt['ext'].upper()} - {fmt['quality']} - {size_str}")

                if len(video['formats']) > 10:
                    print(
                        f"      ... and {len(video['formats']) - 10} more formats")
            else:
                print("    No downloadable formats found")

    def _format_duration(self, seconds):
        """Format duration from seconds to readable format"""
        if seconds is None:
            return "Unknown"
        if not seconds:
            return "Unknown"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def download_video(self, video, format_choice=None):
        """Download selected video with chosen format"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            ydl_opts = {
                'outtmpl': os.path.join(self.output_dir, f'%(title)s_{timestamp}.%(ext)s'),
                'quiet': False,
                'progress': True,
            }

            # If specific format chosen
            if format_choice and format_choice <= len(video['formats']):
                chosen_format = video['formats'][format_choice - 1]
                ydl_opts['format'] = chosen_format['format_id']
                print(
                    f"Downloading in format: {chosen_format['quality']} ({chosen_format['ext'].upper()})")
            else:
                # Default to best quality
                ydl_opts['format'] = 'best'
                print("Downloading in best available quality")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading: {video['title']}")
                ydl.download([video['url']])
                print(f"✓ Download completed: {video['title']}")

        except Exception as e:
            print(f"✗ Error downloading {video['title']}: {str(e)}")

    def interactive_download(self, videos):
        """Interactive download process"""
        if not videos:
            return

        while True:
            print("\n" + "-"*50)
            print("DOWNLOAD OPTIONS")
            print("-"*50)
            print("Enter video number to download (1-{})".format(len(videos)))
            print("Enter 'all' to download all videos")
            print("Enter 'q' to quit")

            choice = input("\nYour choice: ").strip().lower()

            if choice == 'q':
                break
            elif choice == 'all':
                for video in videos:
                    self.download_video(video)
                break
            else:
                try:
                    video_num = int(choice)
                    if 1 <= video_num <= len(videos):
                        selected_video = videos[video_num - 1]

                        # Show format options
                        if len(selected_video['formats']) > 1:
                            print(
                                f"\nAvailable formats for '{selected_video['title']}':")
                            for j, fmt in enumerate(selected_video['formats'], 1):
                                    size_str = self.format_size(fmt['filesize'])
                                    if fmt['filesize'] is None:
                                        size_str = "Calculated during download"
                                    print(
                                        f"  [{j}] {fmt['ext'].upper()} - {fmt['quality']} - {size_str}")

                            format_choice = input(
                                f"\nChoose format (1-{len(selected_video['formats'])}) or press Enter for best: ").strip()

                            if format_choice:
                                try:
                                    format_num = int(format_choice)
                                    self.download_video(
                                        selected_video, format_num)
                                except ValueError:
                                    self.download_video(selected_video)
                            else:
                                self.download_video(selected_video)
                        else:
                            self.download_video(selected_video)
                    else:
                        print("Invalid video number!")
                except ValueError:
                    print("Invalid input! Please enter a number, 'all', or 'q'")


def main():
    """Main function"""
    print("Any Video Downloader")
    print("===================")
    print("Supports YouTube, Vimeo, Dailymotion, and many other platforms!")

    downloader = VideoDownloader()

    while True:
        url = input("\nEnter video URL (or 'q' to quit): ").strip()

        if url.lower() == 'q':
            break

        if not url:
            print("Please enter a valid URL")
            continue

        # Validate URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                print("Please enter a valid URL with http:// or https://")
                continue
        except Exception:
            print("Invalid URL format")
            continue

        print("\nAnalyzing website for videos...")
        videos = downloader.get_video_info(url)

        if videos:
            downloader.display_video_info(videos)
            downloader.interactive_download(videos)
        else:
            print("No videos found or unable to extract video information from this URL.")
            print(
                "Make sure the URL contains video content and is from a supported platform.")

        continue_choice = input(
            "\nAnalyze another URL? (y/n): ").strip().lower()
        if continue_choice != 'y':
            break

    print("\nThank you for using Any Video Downloader!")


if __name__ == "__main__":
    main()
