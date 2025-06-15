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
