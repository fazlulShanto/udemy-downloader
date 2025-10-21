"""
Command-line interface for the Udemy downloader.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Set

from coloredlogs import ColoredFormatter
from dotenv import load_dotenv

from .config import (
    DOWNLOAD_DIR, LOG_DIR_PATH, LOG_FILE_PATH, LOG_FORMAT, LOG_DATE_FORMAT,
    DEFAULT_CONCURRENT_DOWNLOADS, DEFAULT_CAPTION_LOCALE, DEFAULT_H265_CRF,
    DEFAULT_H265_PRESET, MAX_CONCURRENT_DOWNLOADS, KEY_FILE_PATH, SAVED_DIR
)
from .constants import LOG_LEVEL
from .downloader import UdemyDownloader
from .utils import check_dependency, remove_emojis

logger: Optional[logging.Logger] = None


def parse_chapter_filter(chapter_str: str) -> Set[int]:
    """
    Parse chapter filter string into set of chapter numbers.
    
    Args:
        chapter_str: String like "1,3-5,7,9-11"
        
    Returns:
        Set of chapter numbers
    """
    chapters = set()
    for part in chapter_str.split(","):
        if "-" in part:
            try:
                start, end = part.split("-")
                start = int(start.strip())
                end = int(end.strip())
                chapters.update(range(start, end + 1))
            except ValueError:
                logger.error("Invalid range in --chapter argument: %s", part)
        else:
            try:
                chapters.add(int(part.strip()))
            except ValueError:
                logger.error("Invalid chapter number in --chapter argument: %s", part)
    return chapters


def setup_logging(log_level: int) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        
    Returns:
        Configured logger
    """
    # Ensure logs directory exists
    Path(LOG_DIR_PATH).mkdir(parents=True, exist_ok=True)

    # Setup logger
    logger = logging.getLogger(__name__)
    logging.root.setLevel(log_level)

    # Create formatters
    console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Create handlers
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setFormatter(file_formatter)

    # Configure logger
    logger = logging.getLogger("udemy-downloader")
    logger.setLevel(log_level)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


def check_dependencies() -> bool:
    """
    Check for required external dependencies.
    
    Returns:
        True if all dependencies are available
    """
    dependencies = [
        ("aria2c", "Aria2c"),
        ("ffmpeg", "FFMPEG"),
        ("shaka-packager", "Shaka Packager")
    ]
    
    all_available = True
    for cmd, name in dependencies:
        if not check_dependency(cmd, name):
            all_available = False
    
    return all_available


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(description="Udemy Downloader")
    
    # Required arguments
    parser.add_argument(
        "-c", "--course-url",
        dest="course_url",
        type=str,
        help="The URL of the course to download",
        required=True,
    )
    
    # Authentication
    parser.add_argument(
        "-b", "--bearer",
        dest="bearer_token",
        type=str,
        help="The Bearer token to use",
    )
    parser.add_argument(
        "--browser",
        dest="browser",
        help="The browser to extract cookies from",
        choices=["chrome", "firefox", "opera", "edge", "brave", "chromium", "vivaldi", "safari", "file"],
    )
    
    # Quality and download options
    parser.add_argument(
        "-q", "--quality",
        dest="quality",
        type=int,
        help="Download specific video quality. If not specified, best quality will be downloaded",
    )
    parser.add_argument(
        "-cd", "--concurrent-downloads",
        dest="concurrent_downloads",
        type=int,
        help=f"Maximum concurrent downloads for segments (1-{MAX_CONCURRENT_DOWNLOADS})",
    )
    
    # Content options
    parser.add_argument(
        "--skip-lectures",
        dest="skip_lectures",
        action="store_true",
        help="Skip downloading lectures",
    )
    parser.add_argument(
        "--download-assets",
        dest="download_assets",
        action="store_true",
        help="Download lecture assets",
    )
    parser.add_argument(
        "--download-captions",
        dest="download_captions",
        action="store_true",
        help="Download captions",
    )
    parser.add_argument(
        "--download-quizzes",
        dest="download_quizzes",
        action="store_true",
        help="Download quizzes",
    )
    
    # Caption options
    parser.add_argument(
        "-l", "--lang",
        dest="lang",
        type=str,
        help="Caption language to download, 'all' for all languages (Default: 'en')",
    )
    parser.add_argument(
        "--keep-vtt",
        dest="keep_vtt",
        action="store_true",
        help="Keep VTT files after converting to SRT",
    )
    
    # Video processing options
    parser.add_argument(
        "--skip-hls",
        dest="skip_hls",
        action="store_true",
        help="Skip HLS streams (faster fetching)",
    )
    parser.add_argument(
        "--use-h265",
        dest="use_h265",
        action="store_true",
        help="Encode videos with H.265 codec",
    )
    parser.add_argument(
        "--h265-crf",
        dest="h265_crf",
        type=int,
        default=DEFAULT_H265_CRF,
        help=f"CRF value for H.265 encoding (default: {DEFAULT_H265_CRF})",
    )
    parser.add_argument(
        "--h265-preset",
        dest="h265_preset",
        type=str,
        default=DEFAULT_H265_PRESET,
        help=f"Preset for H.265 encoding (default: {DEFAULT_H265_PRESET})",
    )
    parser.add_argument(
        "--use-nvenc",
        dest="use_nvenc",
        action="store_true",
        help="Use NVIDIA hardware encoding for H.265",
    )
    
    # File management
    parser.add_argument(
        "--save-to-file",
        dest="save_to_file",
        action="store_true",
        help="Save course content to file for later loading",
    )
    parser.add_argument(
        "--load-from-file",
        dest="load_from_file",
        action="store_true",
        help="Load course content from previously saved file",
    )
    parser.add_argument(
        "-o", "--out",
        dest="out",
        type=str,
        help="Output directory path",
    )
    
    # Course options
    parser.add_argument(
        "--id-as-course-name",
        dest="id_as_course_name",
        action="store_true",
        help="Use course ID as directory name",
    )
    parser.add_argument(
        "-sc", "--subscription-course",
        dest="is_subscription_course",
        action="store_true",
        help="Mark as subscription course",
    )
    parser.add_argument(
        "--continue-lecture-numbers",
        "-n",
        dest="use_continuous_lecture_numbers",
        action="store_true",
        help="Use continuous lecture numbering",
    )
    parser.add_argument(
        "--chapter",
        dest="chapter_filter_raw",
        type=str,
        help="Download specific chapters (e.g., '1,3-5,7,9-11')",
    )
    
    # Utility options
    parser.add_argument(
        "--info",
        dest="info",
        action="store_true",
        help="Print course information only, don't download",
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        type=str,
        help="Logging level (DEBUG, INFO, ERROR, WARNING, CRITICAL)",
    )
    
    return parser


def main():
    """Main CLI entry point."""
    global logger
    
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = LOG_LEVEL
    if args.log_level:
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "CRITICAL": logging.CRITICAL,
        }
        log_level = level_map.get(args.log_level.upper(), logging.INFO)
    
    logger = setup_logging(log_level)
    
    # Check dependencies
    if not args.skip_lectures and not check_dependencies():
        sys.exit(1)
    
    # Setup download directory
    download_dir = DOWNLOAD_DIR
    if args.out:
        download_dir = os.path.abspath(args.out)
    
    logger.info(f"Output directory set to {download_dir}")
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    Path(SAVED_DIR).mkdir(parents=True, exist_ok=True)
    
    # Load decryption keys if available
    keys = {}
    if os.path.exists(KEY_FILE_PATH):
        with open(KEY_FILE_PATH, encoding="utf8", mode="r") as keyfile:
            keys = json.loads(keyfile.read())
    else:
        logger.warning("Keyfile not found! You won't be able to decrypt encrypted videos!")
    
    # Process chapter filter
    chapter_filter = None
    if args.chapter_filter_raw:
        chapter_filter = parse_chapter_filter(args.chapter_filter_raw)
        logger.info("Chapter filter applied: %s", sorted(chapter_filter))
    
    # Setup authentication
    bearer_token = args.bearer_token or os.getenv("UDEMY_BEARER")
    if not bearer_token and not args.browser:
        logger.error("No bearer token or browser specified for authentication")
        sys.exit(1)
    
    # Initialize downloader
    try:
        downloader = UdemyDownloader(bearer_token=bearer_token, browser=args.browser)
    except Exception as e:
        logger.error(f"Failed to initialize downloader: {e}")
        sys.exit(1)
    
    # Process concurrent downloads setting
    concurrent_downloads = args.concurrent_downloads or DEFAULT_CONCURRENT_DOWNLOADS
    if concurrent_downloads <= 0:
        concurrent_downloads = DEFAULT_CONCURRENT_DOWNLOADS
    elif concurrent_downloads > MAX_CONCURRENT_DOWNLOADS:
        concurrent_downloads = MAX_CONCURRENT_DOWNLOADS
    
    # Prepare download options
    options = {
        "quality": args.quality,
        "concurrent_downloads": concurrent_downloads,
        "skip_lectures": args.skip_lectures,
        "download_assets": args.download_assets,
        "download_captions": args.download_captions,
        "download_quizzes": args.download_quizzes,
        "caption_locale": args.lang or DEFAULT_CAPTION_LOCALE,
        "keep_vtt": args.keep_vtt,
        "skip_hls": args.skip_hls,
        "use_h265": args.use_h265,
        "h265_crf": args.h265_crf,
        "h265_preset": args.h265_preset,
        "use_nvenc": args.use_nvenc,
        "id_as_course_name": args.id_as_course_name,
        "is_subscription_course": args.is_subscription_course,
        "use_continuous_lecture_numbers": args.use_continuous_lecture_numbers,
        "chapter_filter": chapter_filter,
        "download_dir": download_dir,
        "keys": keys,
    }
    
    try:
        if args.info:
            # Just get course info
            course_info = downloader.get_course_info(args.course_url)
            print_course_info(course_info)
        elif args.load_from_file:
            # Load from file and process
            logger.info("Loading course data from file...")
            course_data = downloader.load_course_data()
            if args.info:
                print_course_info(course_data)
            else:
                downloader.download_course(args.course_url, **options)
        else:
            # Normal download process
            if args.save_to_file:
                course_info = downloader.get_course_info(args.course_url)
                downloader.save_course_data(course_info)
                logger.info("Course data saved to file")
            
            downloader.download_course(args.course_url, **options)
            
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        sys.exit(1)


def print_course_info(course_data: dict) -> None:
    """Print course information."""
    title = course_data.get("title", "Unknown")
    chapter_count = course_data.get("total_chapters", 0)
    lecture_count = course_data.get("total_lectures", 0)
    
    logger.info(f"Course: {title}")
    logger.info(f"Total Chapters: {chapter_count}")
    logger.info(f"Total Lectures: {lecture_count}")


if __name__ == "__main__":
    main()