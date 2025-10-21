# API Reference

This document provides a comprehensive reference for all classes, methods, and functions in the Udemy Downloader codebase.

## Core Classes

### Udemy Class

The main class for interacting with Udemy's API and processing course content.

```python
class Udemy:
    def __init__(self, bearer_token: str)
```

#### Constructor Parameters
- `bearer_token` (str): Bearer token for API authentication

#### Public Methods

##### Course Information Methods

```python
def extract_course_name(self, url: str) -> tuple[str, str]
```
**Purpose**: Extract portal name and course identifier from URL  
**Parameters**:
- `url` (str): Udemy course URL
**Returns**: Tuple of (portal_name, course_name_or_id)  
**Example**:
```python
portal, course = udemy.extract_course_name("https://www.udemy.com/course/python-bootcamp/")
# Returns: ("www", "python-bootcamp")
```

```python
def extract_portal_name(self, url: str) -> str
```
**Purpose**: Extract portal name from URL  
**Parameters**:
- `url` (str): Udemy URL
**Returns**: Portal name (e.g., "www", "business")

##### Private Methods (Internal API)

```python
def _extract_course_info(self, url: str) -> tuple[str, dict]
```
**Purpose**: Extract complete course information  
**Parameters**:
- `url` (str): Course URL
**Returns**: Tuple of (course_id, course_info_dict)  
**Side Effects**: Sets global `portal_name` variable  
**Raises**: `SystemExit` if course not found

```python
def _extract_course_curriculum(self, url: str, course_id: str, portal_name: str) -> dict
```
**Purpose**: Extract course curriculum with pagination  
**Parameters**:
- `url` (str): Course URL
- `course_id` (str): Udemy course ID
- `portal_name` (str): Portal identifier
**Returns**: Complete curriculum data dictionary

```python
def _parse_lecture(self, lecture: dict) -> dict
```
**Purpose**: Parse individual lecture data  
**Parameters**:
- `lecture` (dict): Raw lecture data from API
**Returns**: Processed lecture dictionary with media sources  
**Processing**:
- Extracts video sources (encrypted/unencrypted)
- Processes subtitles and captions
- Handles supplementary assets
- Determines content type

##### Content Extraction Methods

```python
def _extract_sources(self, sources: list, skip_hls: bool) -> list
```
**Purpose**: Extract video sources from various formats  
**Parameters**:
- `sources` (list): List of video source objects
- `skip_hls` (bool): Whether to skip HLS processing
**Returns**: List of processed video sources

```python
def _extract_media_sources(self, sources: list) -> list
```
**Purpose**: Extract DASH media sources for encrypted content  
**Parameters**:
- `sources` (list): List of media source objects
**Returns**: List of processed DASH sources

```python
def _extract_subtitles(self, tracks: list) -> list
```
**Purpose**: Extract subtitle information  
**Parameters**:
- `tracks` (list): List of subtitle track objects
**Returns**: List of subtitle dictionaries with download URLs

```python
def _extract_supplementary_assets(self, supp_assets: list, lecture_counter: int) -> list
```
**Purpose**: Process supplementary course assets  
**Parameters**:
- `supp_assets` (list): List of asset objects
- `lecture_counter` (int): Lecture number for filename prefix
**Returns**: List of processed asset dictionaries

##### Quiz Processing Methods

```python
def _get_quiz(self, quiz_id: str) -> dict
```
**Purpose**: Fetch raw quiz data from API  
**Parameters**:
- `quiz_id` (str): Quiz identifier
**Returns**: Raw quiz data from API

```python
def _get_quiz_with_info(self, quiz_id: str) -> dict
```
**Purpose**: Fetch and process quiz data with type detection  
**Parameters**:
- `quiz_id` (str): Quiz identifier
**Returns**: Processed quiz data with type classification  
**Quiz Types**:
- `normal-quiz`: Multiple choice questions
- `coding-problem`: Programming exercises

##### Stream Processing Methods

```python
def _extract_m3u8(self, url: str) -> list
```
**Purpose**: Extract HLS stream information  
**Parameters**:
- `url` (str): M3U8 playlist URL
**Returns**: List of HLS stream dictionaries  
**Side Effects**: Downloads and caches M3U8 files

```python
def _extract_mpd(self, url: str) -> list
```
**Purpose**: Extract DASH stream information  
**Parameters**:
- `url` (str): MPD manifest URL
**Returns**: List of DASH stream dictionaries  
**Side Effects**: Downloads MPD files, uses yt-dlp for processing

##### Pagination and Data Retrieval

```python
def _handle_pagination(self, initial_url: str, initial_params: dict = None) -> dict
```
**Purpose**: Handle paginated API responses  
**Parameters**:
- `initial_url` (str): First page URL
- `initial_params` (dict, optional): Query parameters
**Returns**: Combined results from all pages

```python
def _get_courses(self, portal_name: str) -> list
```
**Purpose**: Get all user's enrolled courses  
**Parameters**:
- `portal_name` (str): Portal identifier
**Returns**: List of course objects

### Session Class

Manages HTTP sessions with custom SSL configuration.

```python
class Session:
    def __init__(self)
```

#### Methods

```python
def visit(self, portal_name: str) -> bool
```
**Purpose**: Make initial visit request for Cloudflare bypass  
**Parameters**:
- `portal_name` (str): Udemy portal name
**Returns**: Success status boolean

```python
def _get(self, url: str, params: dict = None) -> requests.Response
```
**Purpose**: Perform GET request with retry logic  
**Parameters**:
- `url` (str): Request URL
- `params` (dict, optional): Query parameters
**Returns**: HTTP response object  
**Features**: Automatic retry, cookie support, error handling

```python
def _post(self, url: str, data: dict, redirect: bool = True) -> requests.Response
```
**Purpose**: Perform POST request  
**Parameters**:
- `url` (str): Request URL
- `data` (dict): POST data
- `redirect` (bool): Allow redirects
**Returns**: HTTP response object

### UdemyAuth Class

Handles authentication and session management.

```python
class UdemyAuth:
    def __init__(self, username: str = "", password: str = "", cache_session: bool = False)
```

#### Constructor Parameters
- `username` (str): Username (currently unused)
- `password` (str): Password (currently unused)
- `cache_session` (bool): Whether to cache session

## Utility Functions

### String Processing

```python
def deEmojify(inputStr: str) -> str
```
**Purpose**: Remove emoji characters from strings  
**Parameters**:
- `inputStr` (str): Input string with potential emojis
**Returns**: String with emojis removed  
**Use Cases**: Filename sanitization, title cleaning

```python
def parse_chapter_filter(chapter_str: str) -> set
```
**Purpose**: Parse chapter filter string into set of numbers  
**Parameters**:
- `chapter_str` (str): Filter string (e.g., "1,3-5,7")
**Returns**: Set of chapter numbers to include  
**Formats Supported**:
- Individual: "1,3,5"
- Ranges: "1-5"
- Mixed: "1,3-5,7,9-11"

### Video Processing

```python
def mux_process(video_filepath: str, audio_filepath: str, video_title: str, 
                output_path: str, audio_key: str = None, video_key: str = None) -> int
```
**Purpose**: Mux video and audio streams with optional decryption  
**Parameters**:
- `video_filepath` (str): Path to video file
- `audio_filepath` (str): Path to audio file
- `video_title` (str): Title for metadata
- `output_path` (str): Output file path
- `audio_key` (str, optional): Audio decryption key
- `video_key` (str, optional): Video decryption key
**Returns**: FFmpeg return code (0 = success)  
**Features**: H.265 encoding, hardware acceleration, metadata embedding

```python
def handle_segments(url: str, format_id: str, lecture_id: str, video_title: str, 
                   output_path: str, chapter_dir: str) -> None
```
**Purpose**: Download and process DASH segments for encrypted content  
**Parameters**:
- `url` (str): MPD manifest URL or file path
- `format_id` (str): yt-dlp format identifier
- `lecture_id` (str): Unique lecture identifier
- `video_title` (str): Lecture title for metadata
- `output_path` (str): Final output file path
- `chapter_dir` (str): Chapter directory for temporary files
**Side Effects**: Downloads segments, extracts keys, muxes streams, cleans up

### Download Functions

```python
def download_aria(url: str, file_dir: str, filename: str) -> int
```
**Purpose**: Download files using aria2c  
**Parameters**:
- `url` (str): Download URL
- `file_dir` (str): Target directory
- `filename` (str): Target filename
**Returns**: aria2c return code  
**Features**: High-speed concurrent downloads, resume capability

```python
def download(url: str, path: str, filename: str) -> int
```
**Purpose**: Download files with resume capability using requests  
**Parameters**:
- `url` (str): Download URL
- `path` (str): Target file path
- `filename` (str): Filename for progress display
**Returns**: Total file size downloaded  
**Features**: Resume support, progress bar, chunked downloading

### Content Processing

```python
def process_lecture(lecture: dict, lecture_path: str, chapter_dir: str) -> None
```
**Purpose**: Process individual lecture based on content type  
**Parameters**:
- `lecture` (dict): Processed lecture data
- `lecture_path` (str): Target file path
- `chapter_dir` (str): Chapter directory path
**Processing**: Quality selection, format detection, encoding options

```python
def process_caption(caption: dict, lecture_title: str, lecture_dir: str, tries: int = 0) -> None
```
**Purpose**: Download and process subtitle files  
**Parameters**:
- `caption` (dict): Caption data with URL and language
- `lecture_title` (str): Lecture title for filename
- `lecture_dir` (str): Directory for caption files
- `tries` (int): Current retry attempt
**Features**: VTT to SRT conversion, retry logic, multiple languages

```python
def process_quiz(udemy: Udemy, lecture: dict, chapter_dir: str) -> None
```
**Purpose**: Process quiz content and generate HTML  
**Parameters**:
- `udemy` (Udemy): Udemy client for API access
- `lecture` (dict): Lecture data with quiz ID
- `chapter_dir` (str): Chapter directory for output
**Processing**: Determines quiz type, renders appropriate template

### System Validation

```python
def check_for_aria() -> bool
```
**Purpose**: Verify aria2c availability  
**Returns**: True if aria2c is available and working

```python
def check_for_ffmpeg() -> bool
```
**Purpose**: Verify FFmpeg availability  
**Returns**: True if FFmpeg is available and working

```python
def check_for_shaka() -> bool
```
**Purpose**: Verify Shaka Packager availability  
**Returns**: True if Shaka Packager is available and working

### Time Utilities

```python
def durationtoseconds(period: str) -> float
```
**Purpose**: Convert ISO 8601 duration to seconds  
**Parameters**:
- `period` (str): ISO 8601 duration (e.g., "PT1H30M45.5S")
**Returns**: Duration in seconds, or None if invalid  
**Format**: PT[nD][nH][nM][n.nS]

### DRM Utilities

```python
def extract_kid(mp4_file: str) -> str
```
**Purpose**: Extract Key ID from MP4 PSSH header  
**Parameters**:
- `mp4_file` (str): Path to MP4 file
**Returns**: Hexadecimal Key ID or None  
**Dependencies**: mp4parse, widevine_pssh_data_pb2

### Subtitle Conversion

```python
def convert(directory: str, filename: str) -> None
```
**Purpose**: Convert WebVTT to SubRip format  
**Parameters**:
- `directory` (str): Directory containing VTT file
- `filename` (str): Base filename without extension
**Processing**: Reads VTT, converts timing, handles HTML entities

## Main Application Functions

### Entry Points

```python
def pre_run() -> None
```
**Purpose**: Initialize application before main execution  
**Responsibilities**:
- Parse command-line arguments
- Set up logging system
- Create directories
- Load configuration files
- Set global variables

```python
def main() -> None
```
**Purpose**: Main application workflow orchestration  
**Process**:
- Validate dependencies
- Load environment configuration
- Initialize Udemy client
- Fetch course information
- Process and download content

### Workflow Functions

```python
def parse_new(udemy: Udemy, udemy_object: dict) -> None
```
**Purpose**: Process and download course content  
**Parameters**:
- `udemy` (Udemy): Authenticated client
- `udemy_object` (dict): Course data structure
**Processing**: Creates directories, filters chapters, processes lectures

```python
def _print_course_info(udemy: Udemy, udemy_object: dict) -> None
```
**Purpose**: Display course information without downloading  
**Parameters**:
- `udemy` (Udemy): Udemy client
- `udemy_object` (dict): Course data
**Information**: Course metadata, chapter structure, lecture details

## Constants and Configuration

### API Constants

```python
CLIENT_SECRET: str
CLIENT_ID: str
BASIC_AUTH: str
HEADERS: dict
```

### URL Templates

```python
class URLS:
    CURRICULUM_ITEMS: str
    COURSE: str
    MY_COURSES: str
    QUIZ: str
    VISIT: str
    # ... additional URLs
```

### File Paths

```python
HOME_DIR: str
SAVED_DIR: str
KEY_FILE_PATH: str
LOG_FILE_PATH: str
# ... additional paths
```

### Request Parameters

```python
CURRICULUM_ITEMS_PARAMS: dict
COURSE_URL_PARAMS: dict
```

## Global Variables

### Configuration State

```python
# Content selection
dl_assets: bool
dl_captions: bool
dl_quizzes: bool
skip_lectures: bool

# Quality and performance
quality: int
concurrent_downloads: int
skip_hls: bool

# Video encoding
use_h265: bool
h265_crf: int
h265_preset: str
use_nvenc: bool

# Authentication
bearer_token: str
browser: str
keys: dict

# File management
course_name: str
portal_name: str
chapter_filter: set
```

## Error Handling

### Exception Types

- `ConnectionError`: Network connectivity issues
- `FileNotFoundError`: Missing external tools or files
- `ValueError`: Invalid data or parameters
- `SystemExit`: Critical errors requiring termination

### Error Patterns

```python
# Connection error handling
try:
    resp = session._get(url).json()
except conn_error as error:
    logger.fatal(f"Connection error: {error}")
    time.sleep(0.8)
    sys.exit(1)

# Retry logic
for i in range(10):
    req = session.get(url)
    if req.ok:
        return req
    logger.error(f"Retry attempt {i}")
    time.sleep(0.8)

# Graceful degradation
try:
    result = risky_operation()
except Exception:
    logger.exception("Operation failed")
    return None  # Continue with next item
```

## Return Value Conventions

### Success Indicators
- `0`: Successful subprocess execution
- `True`: Successful boolean operations
- Non-empty collections: Successful data retrieval

### Error Indicators
- `None`: Failed operations with graceful handling
- Empty collections: No data found
- Non-zero integers: Failed subprocess execution

### Data Structures

#### Lecture Dictionary
```python
{
    "id": str,
    "lecture_title": str,
    "lecture_index": int,
    "is_encrypted": bool,
    "sources": list,           # For unencrypted content
    "video_sources": list,     # For encrypted content
    "subtitles": list,
    "assets": list,
    "type": str
}
```

#### Source Dictionary
```python
{
    "type": str,              # "video", "hls", "dash"
    "height": str,            # "720", "1080", etc.
    "width": str,
    "extension": str,         # "mp4", "m4v", etc.
    "download_url": str,
    "format_id": str          # For DASH streams
}
```

#### Asset Dictionary
```python
{
    "type": str,              # "file", "source_code", "external_link"
    "title": str,
    "filename": str,
    "extension": str,
    "download_url": str,
    "id": str
}
```