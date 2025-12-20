"""
Any Video Downloader (Refactored for Native yt-dlp)

This script wraps yt-dlp to provide reliable video downloading with
correct audio/video merging and progress reporting.

Dependencies:
    - yt-dlp
    - ffmpeg (required for merging high-quality streams)
"""

import yt_dlp
import os
from datetime import datetime
import time

class VideoDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def get_video_info(self, url):
        """Extract video information from URL"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False, # We need full info to get formats
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Analyzing URL: {url}")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return None

                # Handle playlists vs single video
                if 'entries' in info:
                    # It's a playlist or search result
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
                if fmt.get('acodec') == 'none' and fmt.get('vcodec') == 'none':
                    continue
                
                # Create a simplified format object
                format_info = {
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'resolution': fmt.get('resolution') or f"{fmt.get('width', '?')}x{fmt.get('height', '?')}",
                    'filesize': fmt.get('filesize', 0),
                    'fps': fmt.get('fps', 0),
                    'quality': self._get_quality_description(fmt),
                    # Store technical details for sorting
                    'vcodec': fmt.get('vcodec', 'none'),
                    'acodec': fmt.get('acodec', 'none'),
                }
                video_data['formats'].append(format_info)

        # Sort formats by resolution/quality (best first)
        video_data['formats'].sort(key=lambda x: (
            x.get('filesize') or 0,
            int(x['resolution'].split('x')[1]) if 'x' in x['resolution'] and x['resolution'].split('x')[1].isdigit() else 0
        ), reverse=True)

        return video_data

    def _get_quality_description(self, fmt):
        """Generate quality description for format"""
        parts = []
        if fmt.get('height'): parts.append(f"{fmt['height']}p")
        if fmt.get('fps'): parts.append(f"{fmt['fps']}fps")
        if fmt.get('vcodec') and fmt['vcodec'] != 'none': parts.append(fmt['vcodec'].split('.')[0])
        
        desc = ' | '.join(parts)
        if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
             return desc + " (Audio Only)"
        return desc or 'Unknown'

    def download_video(self, video_data, format_idx, progress_callback=None):
        """Download selected video with specific format or best available"""
        try:
            url = video_data['url']
            title = video_data['title']
            
            # Determine format
            # If format_idx is valid, use that specific format ID
            # BUT: yt-dlp downloading a specific format ID usually means "just that stream"
            # If we want 1080p (video only) to work, we need to instruct yt-dlp to merge best audio.
            # Strategy: 
            # 1. Look at selected format. 
            # 2. If it's video-only (vcodec!=none, acodec=none), tell yt-dlp: selected_id+bestaudio
            # 3. Else use selected_id
            
            selected_format = None
            format_str = "bestvideo+bestaudio/best" # Default fall-back

            if 0 <= format_idx < len(video_data['formats']):
                selected_format = video_data['formats'][format_idx]
                f_id = selected_format['format_id']
                vcodec = selected_format.get('vcodec', 'none')
                acodec = selected_format.get('acodec', 'none')
                
                if vcodec != 'none' and acodec == 'none':
                    # Video only selected -> explicit merge
                    format_str = f"{f_id}+bestaudio/best"
                else:
                    # Audio only or Combined
                    format_str = f_id

            print(f"Downloading '{title}' with format: {format_str}")
            
            # Timestamp for uniqueness
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Define Hooks
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if progress_callback:
                        # Calculate progress
                        # d['downloaded_bytes']
                        # d['total_bytes'] or d['total_bytes_estimate']
                        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                        downloaded = d.get('downloaded_bytes', 0)
                        
                        percent = 0
                        if total > 0:
                            percent = (downloaded / total) * 100
                            
                        # Speed / ETA
                        speed = d.get('speed') or 0
                        speed_mb = speed / 1024 / 1024
                        eta = d.get('eta') or 0
                        
                        eta_str = time.strftime("%M:%S", time.gmtime(eta)) if eta < 3600 else time.strftime("%H:%M:%S", time.gmtime(eta))
                        
                        progress_callback({
                            "status": "downloading",
                            "percent": percent,
                            "speed_mb": speed_mb,
                            "eta": eta_str,
                            "filename": d.get('filename', 'downloading...')
                        })
                
                elif d['status'] == 'finished':
                     print(f"[Done] Download finished: {d['filename']}")
                     if progress_callback:
                         progress_callback({
                             "status": "merging",
                             "percent": 100,
                             "message": "Merging formats..."
                         })

            ydl_opts = {
                'format': format_str,
                'outtmpl': os.path.join(self.output_dir, f'%(title)s_{timestamp}.%(ext)s'),
                'progress_hooks': [progress_hook],
                'quiet': False,
                'no_warnings': True,
                # 'merge_output_format': 'mp4', # Optional: force mp4 container
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            print(f"[Success] '{title}' processed successfully.")

        except Exception as e:
            print(f"[Error] Download failed: {str(e)}")
            if progress_callback:
                progress_callback({"status": "error", "error": str(e)})

if __name__ == "__main__":
    # Test
    dl = VideoDownloader()
    pass
