"""
Content extractors for different types of Udemy content.
"""

import os
import re
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

import m3u8
import yt_dlp
from pathvalidate import sanitize_filename

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Handles extraction of various content types from Udemy."""
    
    def __init__(self, session):
        self.session = session

    def extract_supplementary_assets(self, supp_assets: List[Dict], lecture_counter: int) -> List[Dict]:
        """Extract supplementary assets from lecture data."""
        _temp = []
        for entry in supp_assets:
            title = sanitize_filename(entry.get("title"))
            filename = entry.get("filename")
            download_urls = entry.get("download_urls")
            external_url = entry.get("external_url")
            asset_type = entry.get("asset_type").lower()
            id = entry.get("id")
            
            if asset_type == "file":
                if download_urls and isinstance(download_urls, dict):
                    extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
                    download_url = download_urls.get("File", [])[0].get("file")
                    _temp.append({
                        "type": "file",
                        "title": title,
                        "filename": f"{lecture_counter:03d} {filename}",
                        "extension": extension,
                        "download_url": download_url,
                        "id": id,
                    })
            elif asset_type == "sourcecode":
                if download_urls and isinstance(download_urls, dict):
                    extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
                    download_url = download_urls.get("SourceCode", [])[0].get("file")
                    _temp.append({
                        "type": "source_code",
                        "title": title,
                        "filename": f"{lecture_counter:03d} {filename}",
                        "extension": extension,
                        "download_url": download_url,
                        "id": id,
                    })
            elif asset_type == "externallink":
                _temp.append({
                    "type": "external_link",
                    "title": title,
                    "filename": f"{lecture_counter:03d} {filename}",
                    "extension": "txt",
                    "download_url": external_url,
                    "id": id,
                })
        return _temp

    def extract_article(self, asset: Dict, id: int) -> List[Dict]:
        """Extract article content."""
        return [{
            "type": "article",
            "body": asset.get("body"),
            "extension": "html",
            "id": id,
        }]

    def extract_file_asset(self, asset: Dict, lecture_counter: int, asset_type: str) -> List[Dict]:
        """Extract file-based assets (PPT, File, E-book, Audio)."""
        _temp = []
        download_urls = asset.get("download_urls")
        filename = asset.get("filename")
        id = asset.get("id")
        
        if download_urls and isinstance(download_urls, dict):
            extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
            
            # Map asset types to their download URL keys
            url_key_map = {
                "presentation": "Presentation",
                "file": "File", 
                "ebook": "E-Book",
                "audio": "Audio"
            }
            
            url_key = url_key_map.get(asset_type, "File")
            download_url = download_urls.get(url_key, [])[0].get("file")
            
            _temp.append({
                "type": asset_type,
                "filename": f"{lecture_counter:03d} {filename}",
                "extension": extension,
                "download_url": download_url,
                "id": id,
            })
        return _temp

    def extract_sources(self, sources: List[Dict], skip_hls: bool) -> List[Dict]:
        """Extract video sources from lecture data."""
        _temp = []
        if sources and isinstance(sources, list):
            for source in sources:
                label = source.get("label")
                download_url = source.get("file")
                if not download_url or label.lower() == "audio":
                    continue
                    
                height = label if label else None
                width = self._get_width_from_height(height)
                
                if source.get("type") == "application/x-mpegURL" or "m3u8" in download_url:
                    if not skip_hls:
                        out = self.extract_m3u8(download_url)
                        if out:
                            _temp.extend(out)
                else:
                    _type = source.get("type")
                    _temp.append({
                        "type": "video",
                        "height": height,
                        "width": width,
                        "extension": _type.replace("video/", ""),
                        "download_url": download_url,
                    })
        return _temp

    def extract_media_sources(self, sources: List[Dict]) -> List[Dict]:
        """Extract media sources (DASH) from lecture data."""
        _temp = []
        if sources and isinstance(sources, list):
            for source in sources:
                _type = source.get("type")
                src = source.get("src")

                if _type == "application/dash+xml":
                    out = self.extract_mpd(src)
                    if out:
                        _temp.extend(out)
        return _temp

    def extract_subtitles(self, tracks: List[Dict]) -> List[Dict]:
        """Extract subtitle tracks from lecture data."""
        _temp = []
        if tracks and isinstance(tracks, list):
            for track in tracks:
                if not isinstance(track, dict) or track.get("_class") != "caption":
                    continue
                    
                download_url = track.get("url")
                if not download_url or not isinstance(download_url, str):
                    continue
                    
                lang = (
                    track.get("language") or 
                    track.get("srclang") or 
                    track.get("label") or 
                    track["locale_id"].split("_")[0]
                )
                ext = "vtt" if "vtt" in download_url.rsplit(".", 1)[-1] else "srt"
                _temp.append({
                    "type": "subtitle",
                    "language": lang,
                    "extension": ext,
                    "download_url": download_url,
                })
        return _temp

    def extract_m3u8(self, url: str) -> List[Dict]:
        """Extract m3u8 streams."""
        asset_id_re = re.compile(r"assets/(?P<id>\d+)/")
        _temp = []

        temp_path = Path(Path.cwd(), "temp")
        temp_path.mkdir(parents=True, exist_ok=True)

        try:
            asset_id = asset_id_re.search(url).group("id")
            m3u8_path = Path(temp_path, f"index_{asset_id}.m3u8")

            r = self.session._get(url)
            r.raise_for_status()
            raw_data = r.text

            with open(m3u8_path, "w") as f:
                f.write(raw_data)

            m3u8_object = m3u8.loads(raw_data)
            playlists = m3u8_object.playlists
            seen = set()
            
            for pl in playlists:
                resolution = pl.stream_info.resolution
                codecs = pl.stream_info.codecs

                if not resolution or not codecs:
                    continue
                    
                width, height = resolution
                if height in seen:
                    continue

                playlist_path = Path(temp_path, f"index_{asset_id}_{width}x{height}.m3u8")
                with open(playlist_path, "w") as f:
                    r = self.session._get(pl.uri)
                    r.raise_for_status()
                    f.write(r.text)

                seen.add(height)
                _temp.append({
                    "type": "hls",
                    "height": height,
                    "width": width,
                    "extension": "mp4",
                    "download_url": playlist_path.as_uri(),
                })
        except Exception as error:
            logger.error(f"Error fetching hls streams: {error}")
        return _temp

    def extract_mpd(self, url: str) -> List[Dict]:
        """Extract MPD streams."""
        asset_id_re = re.compile(r"assets/(?P<id>\d+)/")
        _temp = {}

        temp_path = Path(Path.cwd(), "temp")
        temp_path.mkdir(parents=True, exist_ok=True)

        try:
            asset_id = asset_id_re.search(url).group("id")
            mpd_path = Path(temp_path, f"index_{asset_id}.mpd")

            with open(mpd_path, "wb") as f:
                r = self.session._get(url)
                r.raise_for_status()
                f.write(r.content)

            ytdl = yt_dlp.YoutubeDL({
                "quiet": True,
                "no_warnings": True,
                "allow_unplayable_formats": True,
                "enable_file_urls": True,
            })
            
            results = ytdl.extract_info(mpd_path.as_uri(), download=False, force_generic_extractor=True)
            formats = results.get("formats", [])
            
            best_audio = next((f for f in formats if f["acodec"] != "none" and f["vcodec"] == "none"), None)
            if not best_audio:
                raise ValueError("No suitable audio format found in MPD")
                
            audio_format_id = best_audio.get("format_id")
            video_formats = [f for f in formats if f["vcodec"] != "none" and f["acodec"] == "none"]

            for format in video_formats:
                video_format_id = format.get("format_id")
                extension = format.get("ext")
                height = format.get("height")
                width = format.get("width")
                tbr = format.get("tbr", 0)

                if height not in _temp:
                    _temp[height] = []

                _temp[height].append({
                    "type": "dash",
                    "height": str(height),
                    "width": str(width),
                    "format_id": f"{video_format_id},{audio_format_id}",
                    "extension": extension,
                    "download_url": mpd_path.as_uri(),
                    "tbr": round(tbr),
                })

            # Keep only highest bitrate for each resolution
            _temp2 = []
            for height, formats in _temp.items():
                if formats:
                    formats.sort(key=lambda x: x["tbr"], reverse=True)
                    _temp2.append(formats[0])

            _temp = _temp2
        except Exception:
            logger.exception("Error fetching MPD streams")

        return _temp

    def _get_width_from_height(self, height: str) -> str:
        """Get width from height for common resolutions."""
        height_width_map = {
            "2160": "3840",
            "1440": "2560", 
            "1080": "1920",
            "720": "1280",
            "480": "854",
            "360": "640",
            "240": "426"
        }
        return height_width_map.get(height, "256")