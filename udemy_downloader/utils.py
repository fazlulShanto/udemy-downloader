"""
Utility functions for the Udemy downloader.
"""

import base64
import codecs
import os
import subprocess
import logging
from pathlib import Path
from typing import IO, Union

import mp4parse
import widevine_pssh_data_pb2
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


def extract_kid(mp4_file: str) -> Union[str, None]:
    """
    Extract KID (Key ID) from MP4 file with PSSH header.
    
    Args:
        mp4_file: Path to MP4 file with a PSSH header
        
    Returns:
        String containing the KID or None if not found
    """
    if not os.path.exists(mp4_file):
        raise Exception("File does not exist")
        
    try:
        boxes = mp4parse.F4VParser.parse(filename=mp4_file)
        for box in boxes:
            if box.header.box_type == "moov":
                pssh_box = next(x for x in box.pssh if x.system_id == "edef8ba979d64acea3c827dcd51d21ed")
                hex_data = codecs.decode(pssh_box.payload, "hex")

                pssh = widevine_pssh_data_pb2.WidevinePsshData()
                pssh.ParseFromString(hex_data)
                content_id = base64.b16encode(pssh.content_id)
                return content_id.decode("utf-8").lower()
    except Exception as e:
        logger.error(f"Error extracting KID: {e}")
        
    return None


def log_subprocess_output(prefix: str, pipe: IO[bytes]) -> None:
    """
    Log subprocess output line by line.
    
    Args:
        prefix: Prefix for log messages
        pipe: Subprocess pipe to read from
    """
    if pipe:
        for line in iter(lambda: pipe.read(1), ""):
            logger.debug("[%s]: %r", prefix, line.decode("utf8").strip())
        pipe.flush()


def download_file(url: str, path: str, filename: str) -> int:
    """
    Download file with resume capability.
    
    Args:
        url: URL to download from
        path: Path to save file
        filename: Filename for progress display
        
    Returns:
        File size in bytes
    """
    file_size = int(requests.head(url).headers["Content-Length"])
    if os.path.exists(path):
        first_byte = os.path.getsize(path)
    else:
        first_byte = 0
        
    if first_byte >= file_size:
        return file_size
        
    header = {"Range": f"bytes={first_byte}-{file_size}"}
    pbar = tqdm(total=file_size, initial=first_byte, unit="B", unit_scale=True, desc=filename)
    
    res = requests.get(url, headers=header, stream=True)
    res.raise_for_status()
    
    with open(path, "ab") as f:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return file_size


def download_aria(url: str, file_dir: str, filename: str) -> int:
    """
    Download file using aria2c.
    
    Args:
        url: URL to download from
        file_dir: Directory to save file
        filename: Filename to save as
        
    Returns:
        Return code from aria2c
    """
    args = [
        "aria2c",
        url,
        "-o", filename,
        "-d", file_dir,
        "-j16", "-s20", "-x16", "-c",
        "--auto-file-renaming=false",
        "--summary-interval=0",
        "--disable-ipv6",
        "--follow-torrent=false",
    ]
    
    process = subprocess.Popen(args)
    log_subprocess_output("ARIA2-STDOUT", process.stdout)
    log_subprocess_output("ARIA2-STDERR", process.stderr)
    ret_code = process.wait()
    
    if ret_code != 0:
        raise Exception("Return code from the downloader was non-0 (error)")
    return ret_code





def check_dependency(command: str, name: str) -> bool:
    """
    Check if a command-line dependency is available.
    
    Args:
        command: Command to check
        name: Human-readable name for logging
        
    Returns:
        True if dependency is available, False otherwise
    """
    try:
        subprocess.Popen([command, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()
        return True
    except FileNotFoundError:
        logger.error(f"{name} is missing from your system or path!")
        return False
    except Exception:
        logger.exception(f"Unexpected exception while checking for {name}")
        return True  # Assume it's available if we can't check properly


def sanitize_path(path: str) -> str:
    """
    Sanitize a file path for cross-platform compatibility.
    
    Args:
        path: Path to sanitize
        
    Returns:
        Sanitized path
    """
    from pathvalidate import sanitize_filename
    return sanitize_filename(path)


def duration_to_seconds(period: str) -> float:
    """
    Convert ISO 8601 duration to seconds.
    
    Args:
        period: ISO 8601 duration string (e.g., "PT1H30M45S")
        
    Returns:
        Duration in seconds
    """
    if period[:2] == "PT":
        period = period[2:]
        day = int(period.split("D")[0] if "D" in period else 0)
        hour = int(period.split("H")[0].split("D")[-1] if "H" in period else 0)
        minute = int(period.split("M")[0].split("H")[-1] if "M" in period else 0)
        second = period.split("S")[0].split("M")[-1]
        
        total_time = float(
            str((day * 24 * 60 * 60) + (hour * 60 * 60) + (minute * 60) + (int(second.split(".")[0])))
            + "."
            + str(int(second.split(".")[-1]))
        )
        return total_time
    else:
        logger.error("Duration Format Error")
        return 0.0


def remove_emojis(text: str) -> str:
    """
    Remove emojis from text.
    
    Args:
        text: Text to process
        
    Returns:
        Text with emojis removed
    """
    import demoji
    return demoji.replace(text, "")