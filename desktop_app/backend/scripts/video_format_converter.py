"""
Video Format Converter
Refactored for API usage.
"""

import os
import subprocess
import sys
from pathlib import Path
import time
import re

class VideoFormatConverter:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir
        self.supported_formats = {'.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mp4'}

    def get_duration(self, input_path):
        """Get duration in seconds using ffprobe"""
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(input_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout)
        except:
            return 0

    def convert_to_mp4(self, input_path, output_path=None, quality_preset='high', progress_callback=None):
        # Determine paths
        input_path = Path(input_path)
        if output_path is None:
            if self.output_dir:
                 output_dir = Path(self.output_dir)
                 output_dir.mkdir(exist_ok=True)
                 output_path = output_dir / f"{input_path.stem}_converted.mp4"
            else:
                 output_path = input_path.parent / f"{input_path.stem}_converted.mp4"
        else:
            output_path = Path(output_path)
        
        # Presets (Simplifed)
        presets = {
            'high': {'crf': '18', 'preset': 'slow'},
            'medium': {'crf': '23', 'preset': 'medium'},
            'fast': {'crf': '23', 'preset': 'fast'},
            'ultrafast': {'crf': '25', 'preset': 'ultrafast'}
        }
        settings = presets.get(quality_preset, presets['high'])

        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-c:v', 'libx264', '-crf', settings['crf'], '-preset', settings['preset'],
            '-c:a', 'aac', '-b:a', '192k',
            '-movflags', '+faststart', '-y',
            str(output_path)
        ]

        total_duration = self.get_duration(input_path)
        
        try:
            if progress_callback:
                progress_callback({"status": "starting", "message": f"Converting {input_path.name}..."})

            # Run FFmpeg and parse output for progress
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)
            
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                
                if line and "time=" in line:
                    # Parse time=00:00:05.12
                    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d+)', line)
                    if time_match and total_duration > 0:
                        h, m, s = map(float, time_match.groups())
                        current_seconds = h*3600 + m*60 + s
                        percent = (current_seconds / total_duration) * 100
                        if progress_callback:
                            progress_callback({
                                "status": "converting", 
                                "percent": percent,
                                "message": f"Converting... {percent:.1f}%"
                            })

            if process.returncode == 0:
                if progress_callback:
                     progress_callback({"status": "completed", "percent": 100, "output": str(output_path)})
                return True
            else:
                if progress_callback:
                    progress_callback({"status": "error", "error": "FFmpeg process failed"})
                return False

        except Exception as e:
            if progress_callback:
                progress_callback({"status": "error", "error": str(e)})
            raise e
