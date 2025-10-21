"""
Main Udemy downloader class.
"""

import os
import re
import json
import math
import logging
import sys
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

from requests.exceptions import ConnectionError as conn_error
from pathvalidate import sanitize_filename

from .auth import UdemyAuth
from .extractors import ContentExtractor
from .processors import LectureProcessor, QuizProcessor, AssetProcessor
from .constants import URLS, CURRICULUM_ITEMS_PARAMS
from .config import SAVED_DIR

logger = logging.getLogger(__name__)


class UdemyDownloader:
    """Main class for downloading Udemy courses."""
    
    def __init__(self, bearer_token: Optional[str] = None, browser: Optional[str] = None):
        """
        Initialize the Udemy downloader.
        
        Args:
            bearer_token: Bearer token for authentication
            browser: Browser to extract cookies from
        """
        self.bearer_token = bearer_token
        self.browser = browser
        self.auth = UdemyAuth()
        self.session = self.auth._session
        self.extractor = ContentExtractor(self.session)
        self.lecture_processor = LectureProcessor(self.session, self.extractor)
        self.quiz_processor = QuizProcessor(self.session)
        self.asset_processor = AssetProcessor()
        
        self.portal_name = None
        self.course_name = None
        self.cookies = None
        
        self._setup_authentication()

    def _setup_authentication(self):
        """Setup authentication using bearer token or browser cookies."""
        if self.bearer_token:
            self.auth.set_bearer_token(self.bearer_token)
        elif self.browser:
            self._setup_browser_cookies()
        else:
            logger.error("No bearer token or browser specified for authentication")
            raise ValueError("Authentication method required")

    def _setup_browser_cookies(self):
        """Setup browser cookies for authentication."""
        import browser_cookie3
        from http.cookiejar import MozillaCookieJar
        
        if self.browser == "chrome":
            self.cookies = browser_cookie3.chrome()
        elif self.browser == "firefox":
            self.cookies = browser_cookie3.firefox()
        elif self.browser == "opera":
            self.cookies = browser_cookie3.opera()
        elif self.browser == "edge":
            self.cookies = browser_cookie3.edge()
        elif self.browser == "brave":
            self.cookies = browser_cookie3.brave()
        elif self.browser == "chromium":
            self.cookies = browser_cookie3.chromium()
        elif self.browser == "vivaldi":
            self.cookies = browser_cookie3.vivaldi()
        elif self.browser == "file":
            self.cookies = MozillaCookieJar("cookies.txt")
            self.cookies.load()
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")

    def extract_course_name(self, url: str) -> tuple:
        """Extract portal name and course name from URL."""
        obj = re.search(
            r"(?i)(?://(?P<portal_name>.+?).udemy.com/(?:course(/draft)*/)?(?P<name_or_id>[a-zA-Z0-9_-]+))",
            url,
        )
        if obj:
            return obj.group("portal_name"), obj.group("name_or_id")
        raise ValueError("Invalid Udemy URL format")

    def extract_portal_name(self, url: str) -> str:
        """Extract portal name from URL."""
        obj = re.search(r"(?i)(?://(?P<portal_name>.+?).udemy.com)", url)
        if obj:
            return obj.group("portal_name")
        raise ValueError("Invalid Udemy URL format")

    def _handle_pagination(self, initial_url: str, initial_params: Optional[Dict] = None) -> Dict:
        """Handle paginated requests and return all results."""
        page = 1
        try:
            data = self.session._get(initial_url, initial_params, self.cookies).json()
        except conn_error as error:
            logger.fatal(f"Connection error: {error}")
            time.sleep(0.8)
            sys.exit(1)
        else:
            _next = data.get("next")
            _count = data.get("count")
            est_page_count = math.ceil(_count / 100) if _count else 1

            while _next:
                logger.info(f"> Downloading data page {page + 1}/{est_page_count}")
                try:
                    resp = self.session._get(_next, cookies=self.cookies)
                    if not resp.ok:
                        logger.error(f"Failed to fetch page {page + 1}, retrying...")
                        continue
                    resp = resp.json()
                except conn_error as error:
                    logger.fatal(f"Connection error: {error}")
                    time.sleep(0.8)
                    sys.exit(1)
                else:
                    _next = resp.get("next")
                    results = resp.get("results")
                    if results and isinstance(results, list):
                        data["results"].extend(results)
                        page += 1
            return data

    def _get_courses(self, portal_name: str) -> List[Dict]:
        """Get all courses the user has access to."""
        subscribed = self._get_subscribed_courses(portal_name)
        subscription = self._get_subscription_course_enrollments(portal_name)
        return subscribed + subscription

    def _get_subscribed_courses(self, portal_name: str) -> List[Dict]:
        """Fetch subscribed courses."""
        url = URLS.MY_COURSES.format(portal_name=portal_name)
        res = self._handle_pagination(url)
        return res["results"] if res and isinstance(res, dict) else []

    def _get_subscription_course_enrollments(self, portal_name: str) -> List[Dict]:
        """Fetch subscription course enrollments."""
        url = URLS.SUBSCRIPTION_COURSES.format(portal_name=portal_name)
        res = self._handle_pagination(url)
        return res["results"] if res and isinstance(res, dict) else []

    def _extract_course_info_json(self, url: str, course_id: str) -> Dict:
        """Extract course information from API."""
        url = URLS.COURSE.format(portal_name=self.portal_name, course_id=course_id)
        try:
            resp = self.session._get(url, cookies=self.cookies).json()
        except conn_error as error:
            logger.fatal(f"Connection error: {error}")
            time.sleep(0.8)
            sys.exit(1)
        else:
            return resp

    def _extract_course_curriculum(self, url: str, course_id: str, portal_name: str) -> Dict:
        """Extract course curriculum from API."""
        url = URLS.CURRICULUM_ITEMS.format(portal_name=portal_name, course_id=course_id)
        return self._handle_pagination(url, CURRICULUM_ITEMS_PARAMS)

    def _extract_course(self, response: List[Dict], course_name: str) -> Dict:
        """Find course in response by name or ID."""
        for entry in response:
            course_id = str(entry.get("id"))
            published_title = entry.get("published_title")
            if course_name in (published_title, course_id):
                return entry
        return {}

    def _extract_course_info(self, url: str) -> tuple:
        """Extract course information from URL."""
        self.portal_name, course_name = self.extract_course_name(url)
        
        # Get all courses
        results = self._get_courses(portal_name=self.portal_name)
        course = self._extract_course(response=results, course_name=course_name)
        
        if not course:
            # Try archived courses
            results = self._get_archived_courses(self.portal_name)
            course = self._extract_course(response=results, course_name=course_name)

        if course:
            return course.get("id"), course
            
        logger.fatal("Failed to find the course, are you enrolled?")
        sys.exit(1)

    def _get_archived_courses(self, portal_name: str) -> List[Dict]:
        """Get archived courses."""
        try:
            url = URLS.MY_COURSES.format(portal_name=portal_name)
            url = f"{url}&is_archived=true"
            webpage = self.session._get(url, cookies=self.cookies).json()
        except conn_error as error:
            logger.fatal(f"Connection error: {error}")
            time.sleep(0.8)
            sys.exit(1)
        except (ValueError, Exception) as error:
            logger.fatal(f"{error}")
            time.sleep(0.8)
            sys.exit(1)
        else:
            return webpage.get("results", [])

    def get_course_info(self, course_url: str) -> Dict:
        """
        Get course information without downloading.
        
        Args:
            course_url: URL of the course
            
        Returns:
            Dict containing course information
        """
        self.portal_name = self.extract_portal_name(course_url)
        visit_status = self.session.visit(self.portal_name)
        if not visit_status:
            logger.fatal("Visit request failed")
            sys.exit(1)

        logger.info("Fetching course information...")
        course_id, course_info = self._extract_course_info(course_url)
        
        logger.info("Fetching course curriculum...")
        course_json = self._extract_course_curriculum(course_url, course_id, self.portal_name)
        course_json["portal_name"] = self.portal_name
        
        return self._parse_course_data(course_json, course_info)

    def download_course(self, course_url: str, **options) -> None:
        """
        Download a complete course.
        
        Args:
            course_url: URL of the course to download
            **options: Download options (quality, captions, assets, etc.)
        """
        course_data = self.get_course_info(course_url)
        
        # Process download options
        self._apply_download_options(options)
        
        # Start download process
        self.lecture_processor.process_course(course_data, options)

    def _parse_course_data(self, course_json: Dict, course_info: Dict) -> Dict:
        """Parse raw course data into structured format."""
        # This would contain the logic from the original parse_new function
        # Simplified for brevity
        return {
            "course_id": course_info.get("id"),
            "title": course_info.get("title"),
            "course_title": course_info.get("published_title"),
            "portal_name": self.portal_name,
            "chapters": [],  # Would be populated with parsed data
            "total_chapters": 0,
            "total_lectures": 0
        }

    def _apply_download_options(self, options: Dict) -> None:
        """Apply download options to processors."""
        # Configure processors based on options
        pass

    def save_course_data(self, course_data: Dict, filename: str = "course_content.json") -> None:
        """Save course data to file."""
        Path(SAVED_DIR).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join(SAVED_DIR, filename)
        with open(filepath, "w", encoding="utf8") as f:
            json.dump(course_data, f, indent=2)
        logger.info(f"Course data saved to {filepath}")

    def load_course_data(self, filename: str = "course_content.json") -> Dict:
        """Load course data from file."""
        filepath = os.path.join(SAVED_DIR, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Course data file not found: {filepath}")
        
        with open(filepath, "r", encoding="utf8") as f:
            return json.load(f)