"""
Configuration and constants for the Udemy downloader.
"""

import os
from pathlib import Path

# Directory paths
HOME_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(HOME_DIR, "out_dir")
MAIN_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
SAVED_DIR = os.path.join(HOME_DIR, "saved")

# Default settings
DEFAULT_CONCURRENT_DOWNLOADS = 10
DEFAULT_CAPTION_LOCALE = "en"
DEFAULT_H265_CRF = 28
DEFAULT_H265_PRESET = "medium"
MAX_CONCURRENT_DOWNLOADS = 30
DEFAULT_RETRY_COUNT = 3

# File paths
KEY_FILE_PATH = os.path.join(HOME_DIR, "keyfile.json")
LOG_DIR_PATH = os.path.join(HOME_DIR, "logs")
LOG_FILE_PATH = os.path.join(LOG_DIR_PATH, "udemy-downloader.log")

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Template paths
TEMPLATES_DIR = os.path.join(MAIN_SCRIPT_PATH, "templates")
QUIZ_TEMPLATE = os.path.join(TEMPLATES_DIR, "quiz_template.html")
CODING_ASSIGNMENT_TEMPLATE = os.path.join(TEMPLATES_DIR, "coding_assignment_template.html")
ARTICLE_TEMPLATE = os.path.join(TEMPLATES_DIR, "article_template.html")