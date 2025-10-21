"""
Udemy Downloader - A Python library for downloading Udemy courses.
"""

__version__ = "0.1.0"
__author__ = "Puyodead1"

from .downloader import UdemyDownloader
from .auth import UdemyAuth
from .session import Session

__all__ = ["UdemyDownloader", "UdemyAuth", "Session"]