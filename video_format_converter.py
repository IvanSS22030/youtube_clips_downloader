"""
Video Format Converter

This script converts video files from various formats (MKV, AVI, MOV, etc.) to MP4 format
without losing quality. It uses FFmpeg for high-quality video conversion with optimal settings
for preserving video and audio quality.

Dependencies:
    - ffmpeg: For video conversion (usually comes with yt-dlp)

Author: IvanSS22030
Date: August 2025
"""

import os
import subprocess
import sys
from pathlib import Path, WindowsPath
import time
from datetime import datetime
import shutil
import tempfile


class VideoFormatConverter:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir
        self.supported_formats = {'.mkv', '.avi', '.mov',
                                  '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mp4'}

    def check_ffmpeg(self):
        """Check if FFmpeg is available on the system"""
        try:
            result = subprocess.run(['ffmpeg', '-version'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print("[OK] FFmpeg is available")
                return True
        except FileNotFoundError:
            print(
                "[ERROR] FFmpeg not found. Please install FFmpeg or ensure it's in your PATH.")
            print("  You can download it from: https://ffmpeg.org/download.html")
            return False
        return False

    def sanitize_path(self, file_path):
        """Sanitize file path for Windows compatibility"""
        try:
            # Convert to Path object and resolve any relative paths
            path = Path(file_path).resolve()

            # Handle Windows-specific path issues
            if sys.platform == "win32":
                # Convert to Windows path format
                path = WindowsPath(str(path))

                # Check if path contains problematic characters
                problematic_chars = ['<', '>', ':', '"', '|', '?', '*']
                if any(char in str(path) for char in problematic_chars):
                    print(
                        f"[WARNING] Path contains problematic characters: {path}")
                    print("  Consider renaming the file to remove special characters")

            return path
        except Exception as e:
            print(f"[ERROR] Error sanitizing path: {str(e)}")
            return None

    def validate_file(self, file_path):
        """Validate that the file can be accessed and is not corrupted"""
        try:
            path = self.sanitize_path(file_path)
            if not path:
                return False, "Invalid file path"

            if not path.exists():
                return False, f"File does not exist: {path}"

            if not path.is_file():
                return False, f"Path is not a file: {path}"

            # Check file size
            try:
                file_size = path.stat().st_size
                if file_size == 0:
                    return False, "File is empty (0 bytes)"
                if file_size < 1024:  # Less than 1KB
                    return False, f"File seems too small: {file_size} bytes"
            except OSError as e:
                return False, f"Cannot access file size: {str(e)}"

            # Check if file is readable
            try:
                with open(path, 'rb') as f:
                    # Read first 1KB to check if file is accessible
                    f.read(1024)
            except PermissionError:
                return False, "Permission denied - file may be in use by another application"
            except OSError as e:
                return False, f"Cannot read file: {str(e)}"

            # Check file extension
            if path.suffix.lower() not in self.supported_formats:
                return False, f"Unsupported format: {path.suffix}. Supported: {', '.join(self.supported_formats)}"

            return True, "File validation passed"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def get_video_info(self, input_path):
        """Get video file information using ffprobe with better error handling"""
        try:
            # Use a temporary file path if the original path has issues
            temp_input = None
            if sys.platform == "win32":
                # Create a temporary copy with a simple name for problematic files
                try:
                    temp_dir = tempfile.gettempdir()
                    temp_name = f"temp_video_{int(time.time())}{Path(input_path).suffix}"
                    temp_input = Path(temp_dir) / temp_name
                    shutil.copy2(input_path, temp_input)
                    probe_path = str(temp_input)
                except Exception as e:
                    print(
                        f"[WARNING] Could not create temp file, using original: {str(e)}")
                    probe_path = str(input_path)
            else:
                probe_path = str(input_path)

            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', probe_path
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30)

            # Clean up temp file if it was created
            if temp_input and temp_input.exists():
                try:
                    temp_input.unlink()
                except:
                    pass

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)

                # Extract video info
                video_streams = [s for s in data.get(
                    'streams', []) if s.get('codec_type') == 'video']
                audio_streams = [s for s in data.get(
                    'streams', []) if s.get('codec_type') == 'audio']

                info = {
                    'duration': float(data.get('format', {}).get('duration', 0)),
                    'size': int(data.get('format', {}).get('size', 0)),
                    'bitrate': int(data.get('format', {}).get('bit_rate', 0)),
                    'video_streams': len(video_streams),
                    'audio_streams': len(audio_streams)
                }

                if video_streams:
                    v = video_streams[0]
                    info.update({
                        'width': int(v.get('width', 0)),
                        'height': int(v.get('height', 0)),
                        'video_codec': v.get('codec_name', 'unknown'),
                        'video_bitrate': v.get('bit_rate', 'unknown'),
                        'fps': eval(v.get('r_frame_rate', '0/1')) if v.get('r_frame_rate') else 0
                    })

                if audio_streams:
                    a = audio_streams[0]
                    info.update({
                        'audio_codec': a.get('codec_name', 'unknown'),
                        'audio_bitrate': a.get('bit_rate', 'unknown'),
                        'sample_rate': a.get('sample_rate', 'unknown')
                    })

                return info
            else:
                print(f"[WARNING] ffprobe failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print("[ERROR] ffprobe timed out - file may be corrupted or too large")
            return None
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None

    def format_size(self, size_bytes):
        """Convert bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def format_duration(self, seconds):
        """Format duration from seconds to readable format"""
        if not seconds:
            return "Unknown"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def display_video_info(self, input_path, info):
        """Display video information"""
        print(f"\n{'='*60}")
        print(f"VIDEO INFORMATION")
        print(f"{'='*60}")
        print(f"File: {Path(input_path).name}")
        print(f"Duration: {self.format_duration(info.get('duration', 0))}")
        print(f"Size: {self.format_size(info.get('size', 0))}")
        print(
            f"Resolution: {info.get('width', '?')}x{info.get('height', '?')}")
        print(f"FPS: {info.get('fps', 'unknown')}")
        print(f"Video Codec: {info.get('video_codec', 'unknown')}")
        print(f"Audio Codec: {info.get('audio_codec', 'unknown')}")
        print(f"Video Streams: {info.get('video_streams', 0)}")
        print(f"Audio Streams: {info.get('audio_streams', 0)}")

    def convert_to_mp4(self, input_path, output_path=None, quality_preset='high'):
        """
        Convert video file to MP4 format with high quality settings

        Args:
            input_path (str): Path to input video file
            output_path (str): Path for output MP4 file (optional)
            quality_preset (str): Quality preset ('high', 'medium', 'fast')
        """
        # Validate input file first
        is_valid, message = self.validate_file(input_path)
        if not is_valid:
            print(f"[ERROR] File validation failed: {message}")
            return False

        input_path = self.sanitize_path(input_path)
        if not input_path:
            print("[ERROR] Could not sanitize input path")
            return False

        # Determine output path
        if output_path is None:
            if self.output_dir:
                output_dir = Path(self.output_dir)
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"{input_path.stem}_converted.mp4"
            else:
                output_path = input_path.parent / \
                    f"{input_path.stem}_converted.mp4"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\nConverting: {input_path.name}")
        print(f"Output: {output_path}")

        # Get video info
        info = self.get_video_info(input_path)
        if info:
            self.display_video_info(input_path, info)

        # Quality presets
        presets = {
            'high': {
                'video_codec': 'libx264',
                'crf': '18',  # Very high quality
                'preset': 'slow',  # Better compression
                'audio_codec': 'aac',
                'audio_bitrate': '320k'
            },
            'medium': {
                'video_codec': 'libx264',
                'crf': '23',  # Good quality
                'preset': 'medium',
                'audio_codec': 'aac',
                'audio_bitrate': '192k'
            },
            'fast': {
                'video_codec': 'libx264',
                'crf': '23',
                'preset': 'fast',
                'audio_codec': 'aac',
                'audio_bitrate': '128k'
            },
            'ultrafast': {
                'video_codec': 'libx264',
                'crf': '25',  # Still good quality
                'preset': 'ultrafast',  # Much faster encoding
                'audio_codec': 'aac',
                'audio_bitrate': '128k'
            }
        }

        settings = presets.get(quality_preset, presets['high'])

        # Build FFmpeg command with better error handling
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', settings['video_codec'],  # Video codec
            # Constant Rate Factor (lower = higher quality)
            '-crf', settings['crf'],
            # Encoding speed vs compression efficiency
            '-preset', settings['preset'],
            '-c:a', settings['audio_codec'],  # Audio codec
            '-b:a', settings['audio_bitrate'],  # Audio bitrate
            '-movflags', '+faststart',  # Optimize for web streaming
            '-y',  # Overwrite output file if it exists
            str(output_path)
        ]

        print(f"\n{'='*60}")
        print(f"CONVERSION STARTED")
        print(f"{'='*60}")
        print(f"Quality preset: {quality_preset}")
        print(
            f"Video codec: {settings['video_codec']} (CRF: {settings['crf']})")
        print(
            f"Audio codec: {settings['audio_codec']} ({settings['audio_bitrate']})")

        try:
            start_time = time.time()

            # Run conversion with better error handling
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True,
                                       universal_newlines=True)

            # Monitor progress
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Look for time progress in FFmpeg output
                    if "time=" in output and "bitrate=" in output:
                        print(f"\rProgress: {output.strip()}",
                              end='', flush=True)

            # Wait for process to complete
            return_code = process.wait()
            elapsed_time = time.time() - start_time

            if return_code == 0:
                print(f"\n\n[SUCCESS] Conversion completed successfully!")
                print(f"Time taken: {self.format_duration(elapsed_time)}")

                # Show output file info
                if output_path.exists():
                    output_size = output_path.stat().st_size
                    print(f"Output file: {output_path.name}")
                    print(f"Output size: {self.format_size(output_size)}")

                    if info and info.get('size', 0) > 0:
                        ratio = (output_size / info['size']) * 100
                        print(f"Size ratio: {ratio:.1f}% of original")

                return True
            else:
                print(
                    f"\n[ERROR] Conversion failed with return code: {return_code}")
                stderr_output = process.stderr.read()
                if stderr_output:
                    print(f"Error details: {stderr_output}")
                return False

        except Exception as e:
            print(f"\n[ERROR] Error during conversion: {str(e)}")
            return False

    def batch_convert(self, input_dir, pattern="*"):
        """Convert multiple files in a directory"""
        input_dir = Path(input_dir)
        if not input_dir.exists():
            print(f"[ERROR] Directory does not exist: {input_dir}")
            return

        # Find all supported video files
        video_files = []
        for ext in self.supported_formats:
            video_files.extend(input_dir.glob(f"{pattern}{ext}"))

        if not video_files:
            print(f"No supported video files found in {input_dir}")
            return

        print(f"Found {len(video_files)} video file(s) to convert:")
        for i, file in enumerate(video_files, 1):
            print(f"  [{i}] {file.name}")

        choice = input(
            f"\nConvert all {len(video_files)} files? (y/n): ").strip().lower()
        if choice != 'y':
            return

        successful = 0
        failed = 0

        for file in video_files:
            print(f"\n{'-'*60}")
            print(
                f"Processing {file.name} ({video_files.index(file) + 1}/{len(video_files)})")

            if self.convert_to_mp4(file):
                successful += 1
            else:
                failed += 1

        print(f"\n{'='*60}")
        print(f"BATCH CONVERSION COMPLETE")
        print(f"{'='*60}")
        print(f"Successfully converted: {successful}")
        print(f"Failed: {failed}")


def main():
    """Main function"""
    print("Video Format Converter")
    print("=====================")
    print("Convert video files to MP4 format with high quality")

    converter = VideoFormatConverter()

    # Check if FFmpeg is available
    if not converter.check_ffmpeg():
        return

    while True:
        print(f"\n{'-'*50}")
        print("CONVERSION OPTIONS")
        print(f"{'-'*50}")
        print("1. Convert single file")
        print("2. Batch convert directory")
        print("3. Quit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == '3':
            break
        elif choice == '1':
            # Single file conversion
            file_path = input(
                "\nEnter path to video file: ").strip().strip('"')

            if not file_path:
                print("Please enter a valid file path")
                continue

            # Quality selection
            print("\nQuality presets:")
            print("1. High (CRF 18, slow preset) - Best quality, ~4-8 hours for 4K")
            print("2. Medium (CRF 23, medium preset) - Balanced, ~2-4 hours for 4K")
            print("3. Fast (CRF 23, fast preset) - Quick conversion, ~1-3 hours for 4K")
            print(
                "4. Ultra Fast (CRF 25, ultrafast preset) - Very quick, ~30-60 mins for 4K")

            quality_choice = input(
                "Choose quality preset (1-4) [default: 1]: ").strip()
            quality_map = {'1': 'high', '2': 'medium',
                           '3': 'fast', '4': 'ultrafast'}
            quality = quality_map.get(quality_choice, 'high')

            # Custom output path
            output_path = input(
                "Enter output path (or press Enter for auto): ").strip().strip('"')
            if not output_path:
                output_path = None

            converter.convert_to_mp4(file_path, output_path, quality)

        elif choice == '2':
            # Batch conversion
            dir_path = input("\nEnter directory path: ").strip().strip('"')
            if not dir_path:
                print("Please enter a valid directory path")
                continue

            converter.batch_convert(dir_path)
        else:
            print("Invalid choice! Please enter 1, 2, or 3")

    print("\nThank you for using Video Format Converter!")


if __name__ == "__main__":
    main()
