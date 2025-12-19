from any_video_downloader import VideoDownloader
import json

def test_cars():
    url = "https://play.cuevana3cc.me/pelicula/cars-3/"
    dl = VideoDownloader()
    print(f"Testing extraction for: {url}")
    
    videos = dl.get_video_info(url)
    
    if not videos:
        print("No videos found.")
    else:
        print(f"Found {len(videos)} videos.")
        for i, vid in enumerate(videos):
            print(f"\n--- Video {i+1} ---")
            print(f"Title: {vid['title']}")
            print(f"URL: {vid['url']}")
            print(f"Formats: {len(vid['formats'])}")
            for fmt in vid['formats']:
                print(f"  Fmt: {fmt['ext']} - {fmt['quality']} - {fmt['filesize']}")

if __name__ == "__main__":
    test_cars()
