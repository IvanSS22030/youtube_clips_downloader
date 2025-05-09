# Web Content Downloader Suite

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A collection of Python scripts for downloading various types of content from websites.

## 🚀 Features

- **YouTube Clips**: Download clip segments from YouTube videos
- **Image Scraping**: Extract all images from websites, including background images
- **CSS Files**: Download and organize stylesheet files

## 🛠️ Tools Included

### 1. YouTube Clip Downloader (`yt_clips_downloader.py`)

- Automatic clip timing extraction
- High-quality video download (best available format)
- Proper audio-video merging
- Progress display during download

### 2. Image Scraper (`image_scraper.py`)

- Downloads regular `<img>` tag images
- Extracts CSS background images
- Maintains original file extensions
- Rate limiting to respect server load
- Handles relative and absolute URLs

### 3. CSS Scraper (`style_scraper.py`)

- Downloads linked stylesheets
- Extracts `@import` rules
- Uses rotating user agents
- Rate limiting between requests

## 📋 Requirements

- Python 3.8 or higher
- FFmpeg (for YouTube clip downloads)
- Python packages:
  - beautifulsoup4 >= 4.12.0
  - requests >= 2.31.0
  - yt-dlp >= 2025.4.30

## 📥 Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/IvanSS22030/web-content-downloader.git
   cd web-content-downloader
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install FFmpeg:

   **Windows:**

   1. Download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)
   2. Extract the zip file
   3. Add the `bin` folder to your system PATH
   4. Restart your terminal

   **Linux:**

   ```bash
   sudo apt update && sudo apt install ffmpeg
   ```

   **macOS:**

   ```bash
   brew install ffmpeg
   ```

## 🎯 Usage

### YouTube Clip Downloader

```bash
python yt_clips_downloader.py
```

Then enter the YouTube clip URL when prompted.

### Image Scraper

```bash
python image_scraper.py
```

Edit the `target_url` in the script to your desired website.

### CSS Scraper

```bash
python style_scraper.py
```

Edit the `url` in the script to your desired website.

## 📂 Output Structure

- YouTube clips → `downloads/`
- Images → `images/`
- CSS files → `css_files/`

## ⚠️ Usage Guidelines

These scripts are intended for personal use and educational purposes. Please:

- Respect website terms of service
- Follow robots.txt guidelines
- Use appropriate rate limiting
- Only download content you have permission to access

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

Created by IvanSS22030
