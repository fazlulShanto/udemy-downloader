"""
VTT to SRT subtitle converter.
"""

import html
import os
from webvtt import WebVTT
from pysrt.srtitem import SubRipItem
from pysrt.srttime import SubRipTime


def convert(directory: str, filename: str) -> None:
    """
    Convert VTT subtitle file to SRT format.
    
    Args:
        directory: Directory containing the VTT file
        filename: Filename without extension
    """
    index = 0
    vtt_filepath = os.path.join(directory, filename + ".vtt")
    srt_filepath = os.path.join(directory, filename + ".srt")
    
    with open(srt_filepath, mode='w', encoding='utf8', errors='ignore') as srt:
        for caption in WebVTT().read(vtt_filepath):
            index += 1
            start = SubRipTime(0, 0, caption.start_in_seconds)
            end = SubRipTime(0, 0, caption.end_in_seconds)
            srt.write(
                SubRipItem(index, start, end, html.unescape(caption.text)).__str__() + "\n"
            )