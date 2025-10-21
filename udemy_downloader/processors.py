"""
Content processors for different types of Udemy content.
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

from pathvalidate import sanitize_filename
from .config import TEMPLATES_DIR
from .utils import download_aria

logger = logging.getLogger(__name__)


class LectureProcessor:
    """Processes lecture content."""
    
    def __init__(self, session, extractor):
        self.session = session
        self.extractor = extractor

    def parse_lecture(self, lecture: Dict) -> Dict:
        """Parse lecture data and extract content."""
        retVal = []
        index = lecture.get("index")
        lecture_data = lecture.get("data")
        asset = lecture_data.get("asset")
        supp_assets = lecture_data.get("supplementary_assets")

        if isinstance(asset, dict):
            asset_type = asset.get("asset_type", "").lower() or asset.get("assetType", "").lower()
            
            if asset_type == "article":
                retVal.extend(self.extractor.extract_article(asset, index))
            elif asset_type == "video":
                pass  # Video processing handled separately
            elif asset_type == "e-book":
                retVal.extend(self.extractor.extract_file_asset(asset, index, "ebook"))
            elif asset_type == "file":
                retVal.extend(self.extractor.extract_file_asset(asset, index, "file"))
            elif asset_type == "presentation":
                retVal.extend(self.extractor.extract_file_asset(asset, index, "presentation"))
            elif asset_type == "audio":
                retVal.extend(self.extractor.extract_file_asset(asset, index, "audio"))
            else:
                logger.warning(f"Unknown asset type: {asset_type}")

            if isinstance(supp_assets, list) and len(supp_assets) > 0:
                retVal.extend(self.extractor.extract_supplementary_assets(supp_assets, index))

        # Process video/media content
        if asset:
            stream_urls = asset.get("stream_urls")
            if stream_urls:
                # Not encrypted
                if stream_urls and isinstance(stream_urls, dict):
                    sources = stream_urls.get("Video")
                    tracks = asset.get("captions")
                    sources = self.extractor.extract_sources(sources, False)  # skip_hls parameter
                    subtitles = self.extractor.extract_subtitles(tracks)
                    
                    lecture.pop("data")
                    lecture.update({
                        "assets": retVal,
                        "assets_count": len(retVal),
                        "sources": sources,
                        "subtitles": subtitles,
                        "subtitle_count": len(subtitles),
                        "sources_count": len(sources),
                        "is_encrypted": False,
                        "asset_id": asset.get("id"),
                        "type": asset.get("asset_type"),
                    })
                else:
                    lecture.pop("data")
                    lecture.update({
                        "html_content": asset.get("body"),
                        "extension": "html",
                        "assets": retVal,
                        "assets_count": len(retVal),
                        "subtitle_count": 0,
                        "sources_count": 0,
                        "is_encrypted": False,
                        "asset_id": asset.get("id"),
                        "type": asset.get("asset_type"),
                    })
            else:
                # Encrypted
                media_sources = asset.get("media_sources")
                if media_sources and isinstance(media_sources, list):
                    sources = self.extractor.extract_media_sources(media_sources)
                    tracks = asset.get("captions")
                    subtitles = self.extractor.extract_subtitles(tracks)
                    
                    lecture.pop("data")
                    lecture.update({
                        "assets": retVal,
                        "assets_count": len(retVal),
                        "video_sources": sources,
                        "subtitles": subtitles,
                        "subtitle_count": len(subtitles),
                        "sources_count": len(sources),
                        "is_encrypted": True,
                        "asset_id": asset.get("id"),
                        "type": asset.get("asset_type"),
                    })
                else:
                    lecture.pop("data")
                    lecture.update({
                        "html_content": asset.get("body"),
                        "extension": "html",
                        "assets": retVal,
                        "assets_count": len(retVal),
                        "subtitle_count": 0,
                        "sources_count": 0,
                        "is_encrypted": False,
                        "asset_id": asset.get("id"),
                        "type": asset.get("asset_type"),
                    })
        else:
            lecture.update({
                "assets": retVal,
                "assets_count": len(retVal),
                "asset_id": lecture_data.get("id"),
                "type": lecture_data.get("type"),
            })

        return lecture

    def process_course(self, course_data: Dict, options: Dict) -> None:
        """Process entire course for download."""
        # Implementation would handle the main download logic
        pass


class QuizProcessor:
    """Processes quiz content."""
    
    def __init__(self, session):
        self.session = session

    def get_quiz(self, quiz_id: str, portal_name: str) -> Dict:
        """Get quiz data from API."""
        from .constants import URLS
        url = URLS.QUIZ.format(portal_name=portal_name, quiz_id=quiz_id)
        try:
            resp = self.session._get(url).json()
        except Exception as error:
            logger.error(f"Error fetching quiz: {error}")
            return {}
        return resp.get("results", {})

    def get_quiz_with_info(self, quiz_id: str, portal_name: str) -> Dict:
        """Get quiz with processed information."""
        resp = {"_class": None, "_type": None, "contents": None}
        quiz_json = self.get_quiz(quiz_id, portal_name)
        
        if not quiz_json:
            return resp
            
        is_only_one = len(quiz_json) == 1 and quiz_json[0]["_class"] == "assessment"
        is_coding_assignment = quiz_json[0]["assessment_type"] == "coding-problem"

        resp["_class"] = quiz_json[0]["_class"]

        if is_only_one and is_coding_assignment:
            assignment = quiz_json[0]
            prompt = assignment["prompt"]

            resp["_type"] = assignment["assessment_type"]
            resp["contents"] = {
                "instructions": self._get_elem_value_or_none(prompt, "instructions"),
                "tests": self._get_elem_value_or_none(prompt, "test_files"),
                "solutions": self._get_elem_value_or_none(prompt, "solution_files"),
            }

            resp["hasInstructions"] = resp["contents"]["instructions"] != "(None)"
            resp["hasTests"] = not isinstance(resp["contents"]["tests"], str)
            resp["hasSolutions"] = not isinstance(resp["contents"]["solutions"], str)
        else:
            resp["_type"] = "normal-quiz"
            resp["contents"] = quiz_json

        return resp

    def _get_elem_value_or_none(self, elem: Dict, key: str) -> str:
        """Get element value or return '(None)'."""
        return elem[key] if elem and key in elem else "(None)"

    def process_normal_quiz(self, quiz: Dict, lecture: Dict, chapter_dir: str) -> None:
        """Process normal quiz and save to HTML."""
        lecture_title = lecture.get("lecture_title")
        lecture_index = lecture.get("lecture_index")
        lecture_file_name = sanitize_filename(lecture_title + ".html")
        lecture_path = os.path.join(chapter_dir, lecture_file_name)

        logger.info(f"Processing quiz {lecture_index}")
        template_path = os.path.join(TEMPLATES_DIR, "quiz_template.html")
        
        try:
            with open(template_path, "r") as f:
                html = f.read()
                quiz_data = {
                    "quiz_id": lecture["data"].get("id"),
                    "quiz_description": lecture["data"].get("description"),
                    "quiz_title": lecture["data"].get("title"),
                    "pass_percent": lecture.get("data").get("pass_percent"),
                    "questions": quiz["contents"],
                }
                html = html.replace("__data_placeholder__", json.dumps(quiz_data))
                
                with open(lecture_path, "w") as f:
                    f.write(html)
        except Exception as e:
            logger.error(f"Error processing quiz: {e}")

    def process_coding_assignment(self, quiz: Dict, lecture: Dict, chapter_dir: str) -> None:
        """Process coding assignment and save to HTML."""
        lecture_title = lecture.get("lecture_title")
        lecture_index = lecture.get("lecture_index")
        lecture_file_name = sanitize_filename(lecture_title + ".html")
        lecture_path = os.path.join(chapter_dir, lecture_file_name)

        logger.info(f"Processing quiz {lecture_index} (coding assignment)")
        template_path = os.path.join(TEMPLATES_DIR, "coding_assignment_template.html")
        
        try:
            with open(template_path, "r") as f:
                html = f.read()
                quiz_data = {
                    "title": lecture_title,
                    "hasInstructions": quiz["hasInstructions"],
                    "hasTests": quiz["hasTests"],
                    "hasSolutions": quiz["hasSolutions"],
                    "instructions": quiz["contents"]["instructions"],
                    "tests": quiz["contents"]["tests"],
                    "solutions": quiz["contents"]["solutions"],
                }
                html = html.replace("__data_placeholder__", json.dumps(quiz_data))
                
                with open(lecture_path, "w") as f:
                    f.write(html)
        except Exception as e:
            logger.error(f"Error processing coding assignment: {e}")


class AssetProcessor:
    """Processes various asset types."""
    
    def process_caption(self, caption: Dict, lecture_title: str, lecture_dir: str, 
                       keep_vtt: bool = False, tries: int = 0) -> None:
        """Process and download caption files."""
        filename = f"{sanitize_filename(lecture_title)}_{caption.get('language')}.{caption.get('extension')}"
        filename_no_ext = f"{sanitize_filename(lecture_title)}_{caption.get('language')}"
        filepath = os.path.join(lecture_dir, filename)

        if os.path.isfile(filepath):
            logger.info(f"Caption '{filename}' already downloaded.")
            return

        logger.info(f"Downloading caption: '{filename}'")
        try:
            ret_code = download_aria(caption.get("download_url"), lecture_dir, filename)
            logger.debug(f"Download return code: {ret_code}")
        except Exception as e:
            if tries >= 3:
                logger.error(f"Error downloading caption: {e}. Exceeded retries, skipping.")
                return
            else:
                logger.error(f"Error downloading caption: {e}. Will retry {3-tries} more times.")
                self.process_caption(caption, lecture_title, lecture_dir, keep_vtt, tries + 1)
                return

        if caption.get("extension") == "vtt":
            try:
                logger.info("Converting caption to SRT format...")
                from .vtt_to_srt import convert
                convert(lecture_dir, filename_no_ext)
                logger.info("Caption conversion complete.")
                if not keep_vtt:
                    os.remove(filepath)
            except Exception:
                logger.exception("Error converting caption")

    def process_asset(self, asset: Dict, chapter_dir: str, lecture_title: str) -> None:
        """Process different types of assets."""
        asset_type = asset.get("type")
        filename = asset.get("filename")
        download_url = asset.get("download_url")

        if asset_type == "article":
            self._process_article_asset(asset, chapter_dir, lecture_title)
        elif asset_type == "external_link":
            self._process_external_link_asset(asset, chapter_dir, filename, download_url)
        elif asset_type in ["audio", "e-book", "file", "presentation", "ebook", "source_code"]:
            self._process_downloadable_asset(download_url, chapter_dir, filename)
        else:
            logger.warning(f"Unknown asset type: {asset_type}")

    def _process_article_asset(self, asset: Dict, chapter_dir: str, lecture_title: str) -> None:
        """Process article assets."""
        body = asset.get("body")
        lecture_path = os.path.join(chapter_dir, f"{sanitize_filename(lecture_title)}.html")
        
        try:
            template_path = os.path.join(TEMPLATES_DIR, "article_template.html")
            with open(template_path, "r") as f:
                content = f.read()
                content = content.replace("__title_placeholder__", lecture_title[4:])
                content = content.replace("__data_placeholder__", body)
                
                with open(lecture_path, "w", encoding="utf8") as f:
                    f.write(content)
        except Exception as e:
            logger.error(f"Failed to write article file: {e}")

    def _process_external_link_asset(self, asset: Dict, chapter_dir: str, 
                                   filename: str, download_url: str) -> None:
        """Process external link assets."""
        # Create shortcut file
        file_path = os.path.join(chapter_dir, f"{filename}.url")
        with open(file_path, "w") as f:
            f.write("[InternetShortcut]\n")
            f.write(f"URL={download_url}")

        # Append to external links file
        savedirs, name = os.path.split(os.path.join(chapter_dir, filename))
        links_filename = os.path.join(savedirs, "external-links.txt")
        
        existing_links = []
        if os.path.isfile(links_filename):
            with open(links_filename, "r", encoding="utf-8", errors="ignore") as f:
                existing_links = [line.strip().lower() for line in f if line.strip()]

        if name.lower() not in existing_links:
            with open(links_filename, "a", encoding="utf-8", errors="ignore") as f:
                f.write(f"\n{name}\n{download_url}\n")

    def _process_downloadable_asset(self, download_url: str, chapter_dir: str, filename: str) -> None:
        """Process downloadable assets."""
        try:
            ret_code = download_aria(download_url, chapter_dir, filename)
            logger.debug(f"Download return code: {ret_code}")
        except Exception:
            logger.exception("Error downloading asset")