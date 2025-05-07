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
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Extract clip start and end times
    start_time = int(query_params.get('start', [0])[0])
    end_time = int(query_params.get('end', [0])[0])

    return start_time, end_time


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
        start_time, end_time = parse_clip_url(url)

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': os.path.join(output_dir, '%(title)s - Clip.%(ext)s'),
            'download_ranges': lambda info: [[start_time, end_time]],
            'force_keyframes_at_cuts': True,
            'postprocessors': [{
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'mp4',
            }],
            'quiet': False,
            'progress': True,
        }

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
