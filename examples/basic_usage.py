#!/usr/bin/env python3
"""
Basic usage example for the Udemy Downloader library.
"""

import os
from udemy_downloader import UdemyDownloader

def main():
    # Initialize the downloader with bearer token
    bearer_token = os.getenv("UDEMY_BEARER")  # Set this environment variable
    if not bearer_token:
        print("Please set UDEMY_BEARER environment variable")
        return
    
    downloader = UdemyDownloader(bearer_token=bearer_token)
    
    # Course URL
    course_url = "https://www.udemy.com/course/your-course-name/"
    
    try:
        # Get course information
        print("Fetching course information...")
        course_info = downloader.get_course_info(course_url)
        print(f"Course: {course_info.get('title')}")
        print(f"Chapters: {course_info.get('total_chapters')}")
        print(f"Lectures: {course_info.get('total_lectures')}")
        
        # Download the course
        print("Starting download...")
        downloader.download_course(
            course_url,
            quality=720,  # Download 720p quality
            download_captions=True,  # Download captions
            download_assets=True,  # Download supplementary assets
            caption_locale="en",  # English captions
        )
        
        print("Download completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()