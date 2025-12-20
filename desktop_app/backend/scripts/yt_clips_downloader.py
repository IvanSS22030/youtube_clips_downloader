"""
YouTube Clip Downloader
Refactored for API usage.
"""

import yt_dlp
import os
import re
from urllib.parse import parse_qs, urlparse
from datetime import datetime

class YTClipsDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def parse_clip_url(self, url):
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'chapters' in info:
                    for chapter in info['chapters']:
                        if chapter.get('is_clip'):
                            return chapter['start_time'], chapter['end_time']
                if info.get('clip_start_time') is not None and info.get('clip_end_time') is not None:
                    return info['clip_start_time'], info['clip_end_time']
        except Exception:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            if 'start' in query_params and 'end' in query_params:
                return int(query_params.get('start', [0])[0]), int(query_params.get('end', [0])[0])
        return 0, None

    def download_clip(self, url, progress_callback=None):
        try:
            if progress_callback:
                progress_callback({"status": "analyzing", "message": "Analyzing clip range..."})

            start_time, end_time = self.parse_clip_url(url)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Progress Hook for yt-dlp
            def ydl_progress_hook(d):
                if d['status'] == 'downloading':
                    if progress_callback and d.get('total_bytes'):
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        progress_callback({
                            "status": "downloading",
                            "percent": percent,
                            "speed": d.get('speed', 0),
                            "eta": d.get('eta', 0)
                        })

            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': os.path.join(self.output_dir, f'%(title)s - Clip_{timestamp}.%(ext)s'),
                'quiet': True,
                'progress_hooks': [ydl_progress_hook],
                'force_overwrites': True
            }

            if end_time is not None:
                ydl_opts.update({
                    'download_ranges': lambda _info, _er: [[start_time, end_time]],
                    'force_keyframes_at_cuts': True,
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if progress_callback:
                progress_callback({"status": "completed", "percent": 100})
            
            return True

        except Exception as e:
            if progress_callback:
                progress_callback({"status": "error", "error": str(e)})
            raise e
