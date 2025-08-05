#!/usr/bin/env python3
"""
YouTube Video Downloader Script
Handles downloading YouTube videos using yt-dlp
"""

import os
import sys
import yt_dlp
import re
from pathlib import Path
from datetime import datetime
import json

def sanitize_filename(filename):
    """Remove or replace characters that are invalid in filenames"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def get_download_options(download_type, output_path):
    """Get yt-dlp options based on download type"""
    
    base_options = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'ignoreerrors': False,  # Changed to False to see actual errors
        'no_warnings': False,
        'extractaudio': False,
        'audioformat': 'mp3',
        'audioquality': '192',
        'verbose': True,  # Enable verbose logging
        # Add user agent to avoid blocking
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
    }
    
    if download_type == 'audio':
        base_options.update({
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        })
    elif download_type == 'best':
        base_options.update({
            'format': 'best[height<=1080]',
        })
    else:  # video (default)
        base_options.update({
            'format': 'best[ext=mp4][height<=720]/best[height<=720]/best',
        })
    
    return base_options

def is_valid_youtube_url(url):
    """Check if the URL is a valid YouTube URL"""
    youtube_patterns = [
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/',
        r'(https?://)?(www\.)?youtu\.be/',
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    return False

def download_youtube_video():
    """Main function to download YouTube video"""
    
    # Get environment variables
    video_url = os.getenv('VIDEO_URL')
    download_type = os.getenv('DOWNLOAD_TYPE', 'video')
    timestamp = os.getenv('TIMESTAMP', datetime.now().isoformat())
    
    if not video_url:
        print("Error: VIDEO_URL environment variable not set")
        sys.exit(1)
    
    # Basic URL validation
    if not is_valid_youtube_url(video_url):
        print(f"Error: Invalid YouTube URL: {video_url}")
        sys.exit(1)
    
    print(f"Starting download for: {video_url}")
    print(f"Download type: {download_type}")
    print(f"Timestamp: {timestamp}")
    
    # Create downloads directory
    downloads_dir = Path('downloads')
    downloads_dir.mkdir(exist_ok=True)
    
    # Setup yt-dlp options
    ydl_opts = get_download_options(download_type, str(downloads_dir))
    
    # Add progress hook
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            print(f"Downloading... {percent} at {speed}")
        elif d['status'] == 'finished':
            print(f"Download completed: {d['filename']}")
    
    ydl_opts['progress_hooks'] = [progress_hook]
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First, let's try to get basic info without downloading
            print("Attempting to extract video information...")
            print(f"Using yt-dlp version: {yt_dlp.version.__version__}")
            
            # Try with different extraction methods
            try:
                info = ydl.extract_info(video_url, download=False)
            except Exception as extract_error:
                print(f"First extraction attempt failed: {extract_error}")
                
                # Try with different options
                print("Trying with simplified options...")
                simple_ydl_opts = {
                    'quiet': False,
                    'no_warnings': False,
                    'verbose': True,
                }
                
                with yt_dlp.YoutubeDL(simple_ydl_opts) as simple_ydl:
                    info = simple_ydl.extract_info(video_url, download=False)
            
            # Check if info extraction was successful
            if info is None:
                raise Exception("Failed to extract video information. The video might be private, deleted, or the URL is invalid.")
            
            print("Video information extracted successfully!")
            
            # Safely get video information with defaults
            title = info.get('title', 'Unknown_Video')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            video_id = info.get('id', 'unknown_id')
            availability = info.get('availability', 'unknown')
            
            print(f"Title: {title}")
            print(f"Duration: {duration} seconds")
            print(f"Uploader: {uploader}")
            print(f"Video ID: {video_id}")
            print(f"Availability: {availability}")
            
            # Check if video is available
            if availability in ['private', 'premium_only', 'subscriber_only']:
                raise Exception(f"Video is {availability} and cannot be downloaded")
            
            # Download the video with the original options
            print("Starting download...")
            ydl.download([video_url])
            
            # Create metadata file
            metadata = {
                'url': video_url,
                'title': title,
                'duration': duration,
                'uploader': uploader,
                'video_id': video_id,
                'download_type': download_type,
                'timestamp': timestamp,
                'status': 'completed'
            }
            
            metadata_file = downloads_dir / f"metadata_{sanitize_filename(title)}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print("Download completed successfully!")
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = f"yt-dlp download error: {str(e)}"
        print(f"Error: {error_msg}")
        create_error_file(downloads_dir, video_url, download_type, timestamp, error_msg)
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"General error: {str(e)}"
        print(f"Error downloading video: {error_msg}")
        create_error_file(downloads_dir, video_url, download_type, timestamp, error_msg)
        sys.exit(1)

def create_error_file(downloads_dir, video_url, download_type, timestamp, error_msg):
    """Create an error metadata file"""
    error_metadata = {
        'url': video_url,
        'download_type': download_type,
        'timestamp': timestamp,
        'status': 'failed',
        'error': error_msg
    }
    
    error_file = downloads_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(error_file, 'w', encoding='utf-8') as f:
        json.dump(error_metadata, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    download_youtube_video()
