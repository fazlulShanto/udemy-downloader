#!/usr/bin/env python3
"""
Example using browser cookies for authentication.
"""

from udemy_downloader import UdemyDownloader

def main():
    # Initialize downloader with browser cookies
    downloader = UdemyDownloader(browser="chrome")  # or "firefox", "edge", etc.
    
    course_url = "https://www.udemy.com/course/your-course-name/"
    
    try:
        # Download with specific options
        downloader.download_course(
            course_url,
            skip_lectures=False,
            download_captions=True,
            download_quizzes=True,
            caption_locale="all",  # Download all available caption languages
            use_h265=True,  # Use H.265 encoding
            concurrent_downloads=5,  # Limit concurrent downloads
        )
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()