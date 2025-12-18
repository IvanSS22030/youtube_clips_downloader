"""
YouTube Clip Downloader

This script downloads YouTube clips using yt-dlp.
It extracts clip timing information from the URL and downloads
only the specified segment of the video.

Dependencies:
    - yt-dlp: For downloading YouTube videos
    - ffmpeg: For video processing

Author: IvanSS22030
Date: May 2025
"""

import yt_dlp
import os
import re
from urllib.parse import parse_qs, urlparse


def parse_clip_url(url):
    """
    Extract clip start and end times from YouTube clip URL.

    Args:
        url (str): YouTube clip URL

    Returns:
        tuple: (start_time, end_time) in seconds
    """
    try:
        # First try to get clip information using yt-dlp
        ydl_opts = {
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'chapters' in info:
                # For newer clip format, the clip is actually a chapter
                for chapter in info['chapters']:
                    if chapter.get('is_clip'):
                        return chapter['start_time'], chapter['end_time']

            # If we have specific clip information
            if info.get('clip_start_time') is not None and info.get('clip_end_time') is not None:
                return info['clip_start_time'], info['clip_end_time']

    except Exception:
        # Fallback to URL parsing for older clip format
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        if 'start' in query_params and 'end' in query_params:
            start_time = int(query_params.get('start', [0])[0])
            end_time = int(query_params.get('end', [0])[0])
            return start_time, end_time

    # If we can't find timing information, download the whole video
    return 0, None


def download_clip(url, output_dir="downloads"):
    """
    Download a YouTube clip.

    Args:
        url (str): YouTube clip URL
        output_dir (str): Directory to save the downloaded clip
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Extract clip timing
        start_time, end_time = parse_clip_url(
            url)        # Configure yt-dlp options
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Simplified format selection
            'outtmpl': os.path.join(output_dir, f'%(title)s - Clip_{timestamp}.%(ext)s'),
            'quiet': False,
            'progress': True,
            'force_overwrites': True  # This will force download even if file exists
        }

        # Only add download range if we have both start and end times
        if end_time is not None:
            ydl_opts.update({
                'download_ranges': lambda _info, _er: [[start_time, end_time]],
                'force_keyframes_at_cuts': True,
            })

        # Download the clip
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Downloading clip...")
            ydl.download([url])

        print(f"\nClip downloaded successfully to {output_dir}")

    except Exception as e:
        print(f"Error downloading clip: {str(e)}")


def main():
    """Main function to handle user input and start download."""
    print("YouTube Clip Downloader")
    print("----------------------")

    while True:
        url = input("\nEnter YouTube clip URL (or 'q' to quit): ").strip()

        if url.lower() == 'q':
            break

        if not url:
            print("Please enter a valid URL")
            continue

        if 'youtube.com' not in url and 'youtu.be' not in url:
            print("Please enter a valid YouTube URL")
            continue

        download_clip(url)

        choice = input("\nDownload another clip? (y/n): ").strip().lower()
        if choice != 'y':
            break

    print("\nThank you for using YouTube Clip Downloader!")


if __name__ == "__main__":
    main()
# https://youtube.com/clip/UgkxTgcUJln8Ir1oBOKYK-KBT2iuHWxEcs98?si=G6tvmvO4qwYBNT_h next link to download
