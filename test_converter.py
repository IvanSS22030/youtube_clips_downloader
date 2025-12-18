"""
Test script for video format converter
"""

from video_format_converter import VideoFormatConverter
import os

def test_converter():
    """Test the video converter with the provided example file"""
    
    # Initialize converter
    converter = VideoFormatConverter(output_dir="downloads")
    
    # Check FFmpeg availability
    if not converter.check_ffmpeg():
        print("Cannot test without FFmpeg")
        return
    
    # Test file path
    test_file = r"C:\Users\IvanJ\Downloads\Spider-man.into.the.spider-verse.2018.2160p.x265.hdr.5.1-dual-lat-cinecalidad.to.mkv"
    
    print(f"Testing with file: {test_file}")
    
    # Check if file exists
    if os.path.exists(test_file):
        print("[OK] Test file found")
        
        # Get video info
        info = converter.get_video_info(test_file)
        if info:
            converter.display_video_info(test_file, info)
            
            print(f"\n{'-'*50}")
            print("This file can be converted using:")
            print("1. Run the main script: python video_format_converter.py")
            print("2. Choose option 1 (Convert single file)")
            print(f"3. Enter path: {test_file}")
            print("4. Choose quality preset (recommended: 1 for high quality)")
            print(f"\nEstimated output size: ~{converter.format_size(info.get('size', 0) * 0.8)}")
        else:
            print("[ERROR] Could not get video information")
    else:
        print(f"[ERROR] Test file not found at: {test_file}")
        print("Make sure the file path is correct and the file exists")

if __name__ == "__main__":
    test_converter()