"""
Test script for Any Video Downloader
Tests the video detection and analysis functionality
"""

from any_video_downloader import VideoDownloader


def test_tokyvideo():
    """Test with the TokyVideo URL"""
    url = "https://www.tokyvideo.com/es/video/narnia-el-leon-la-bruja-y-el-ropero-2005-espanol-latino-c-nando-urhopelis"

    print("Testing Any Video Downloader")
    print("=" * 50)
    print(f"Testing URL: {url}")
    print()

    downloader = VideoDownloader()

    try:
        videos = downloader.get_video_info(url)

        if videos:
            print("✓ Successfully detected videos!")
            downloader.display_video_info(videos)

            print("\nVideo analysis complete!")
            print("You can now run the main script to download videos interactively.")
        else:
            print("✗ No videos detected from this URL")
            print("This might be due to:")
            print("- The website uses a video format not supported by yt-dlp")
            print("- The video requires special authentication")
            print("- The video is embedded from another platform")

    except Exception as e:
        print(f"✗ Error analyzing URL: {str(e)}")


if __name__ == "__main__":
    test_tokyvideo()
