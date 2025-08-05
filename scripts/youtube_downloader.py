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
        'ignoreerrors': True,
        'no_warnings': False,
        'extractaudio': False,
        'audioformat': 'mp3',
        'audioquality': '192',
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

def download_youtube_video():
    """Main function to download YouTube video"""
    
    # Get environment variables
    video_url = os.getenv('VIDEO_URL')
    download_type = os.getenv('DOWNLOAD_TYPE', 'video')
    timestamp = os.getenv('TIMESTAMP', datetime.now().isoformat())
    
    if not video_url:
        print("Error: VIDEO_URL environment variable not set")
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
            # Extract info first
            print("Extracting video information...")
            info = ydl.extract_info(video_url, download=False)
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            print(f"Title: {title}")
            print(f"Duration: {duration} seconds")
            print(f"Uploader: {uploader}")
            
            # Download the video
            print("Starting download...")
            ydl.download([video_url])
            
            # Create metadata file
            metadata = {
                'url': video_url,
                'title': title,
                'duration': duration,
                'uploader': uploader,
                'download_type': download_type,
                'timestamp': timestamp,
                'status': 'completed'
            }
            
            metadata_file = downloads_dir / f"metadata_{sanitize_filename(title)}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print("Download completed successfully!")
            
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        
        # Create error metadata file
        error_metadata = {
            'url': video_url,
            'download_type': download_type,
            'timestamp': timestamp,
            'status': 'failed',
            'error': str(e)
        }
        
        error_file = downloads_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_metadata, f, indent=2, ensure_ascii=False)
        
        sys.exit(1)

if __name__ == "__main__":
    download_youtube_video()
