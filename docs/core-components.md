# Core Components

This document details the core classes and components that form the backbone of the Udemy Downloader application.

## Udemy Class

The main class responsible for interacting with Udemy's API and processing course content.

### Constructor
```python
class Udemy:
    def __init__(self, bearer_token):
        """
        Initialize Udemy client with authentication.
        
        Args:
            bearer_token (str): Bearer token for API authentication
            
        Side Effects:
            - Creates session with authentication headers
            - Sets up cookie jar for browser cookie support
            - Initializes UdemyAuth instance
        """
```

### Core Methods

#### Course Information Extraction
```python
def _extract_course_info(self, url):
    """
    Extract course information from Udemy URL.
    
    Args:
        url (str): Udemy course URL
        
    Returns:
        tuple: (course_id, course_info_dict)
        
    Side Effects:
        - Fetches user's enrolled courses
        - Searches archived courses if not found
        - Sets global portal_name variable
        
    Raises:
        SystemExit: If course not found or user not enrolled
    """

def _extract_course_curriculum(self, url, course_id, portal_name):
    """
    Extract complete course curriculum with pagination support.
    
    Args:
        url (str): Course URL
        course_id (str): Udemy course ID
        portal_name (str): Portal name (e.g., 'www', 'business')
        
    Returns:
        dict: Complete curriculum data with all lectures and chapters
        
    Side Effects:
        - Makes multiple API calls for pagination
        - Logs progress for large courses
    """
```

#### Content Parsing
```python
def _parse_lecture(self, lecture):
    """
    Parse individual lecture data and extract media sources.
    
    Args:
        lecture (dict): Raw lecture data from API
        
    Returns:
        dict: Processed lecture with sources, subtitles, and assets
        
    Processing:
        - Extracts video sources (encrypted/unencrypted)
        - Processes subtitles and captions
        - Handles supplementary assets
        - Determines content type (video/article/quiz)
        
    Side Effects:
        - Removes raw data to save memory
        - Downloads and caches M3U8/MPD files for streaming
    """
```

#### Media Source Extraction
```python
def _extract_sources(self, sources, skip_hls):
    """
    Extract video sources from various formats.
    
    Args:
        sources (list): List of video source objects
        skip_hls (bool): Whether to skip HLS stream processing
        
    Returns:
        list: Processed video sources with quality information
        
    Processing:
        - Handles direct MP4 downloads
        - Processes HLS (m3u8) streams
        - Extracts quality and resolution information
    """

def _extract_media_sources(self, sources):
    """
    Extract DASH media sources for encrypted content.
    
    Args:
        sources (list): List of media source objects
        
    Returns:
        list: Processed DASH sources with format information
        
    Processing:
        - Downloads MPD manifests
        - Uses yt-dlp to extract format information
        - Combines video and audio streams
        - Selects highest bitrate for each resolution
    """
```

#### Asset Processing
```python
def _extract_supplementary_assets(self, supp_assets, lecture_counter):
    """
    Process supplementary course assets.
    
    Args:
        supp_assets (list): List of supplementary asset objects
        lecture_counter (int): Current lecture number for filename prefix
        
    Returns:
        list: Processed assets with download information
        
    Asset Types:
        - Files (PDFs, documents)
        - Source code archives
        - External links
        
    Side Effects:
        - Sanitizes filenames
        - Adds lecture counter prefix
    """

def _extract_article(self, asset, id):
    """
    Extract article content for HTML rendering.
    
    Args:
        asset (dict): Article asset data
        id (int): Lecture ID
        
    Returns:
        list: Article data for template rendering
    """
```

#### Quiz Processing
```python
def _get_quiz_with_info(self, quiz_id):
    """
    Fetch and process quiz data.
    
    Args:
        quiz_id (str): Quiz identifier
        
    Returns:
        dict: Processed quiz data with type classification
        
    Quiz Types:
        - Normal quiz: Multiple choice questions
        - Coding assignment: Programming exercises
        
    Processing:
        - Fetches quiz questions and answers
        - Extracts coding assignment components
        - Processes instructions, tests, and solutions
    """
```

## Session Class

Manages HTTP sessions with custom SSL configuration and request handling.

```python
class Session:
    def __init__(self):
        """
        Initialize HTTP session with custom SSL ciphers.
        
        Side Effects:
            - Creates requests.Session with custom headers
            - Configures SSL cipher list for compatibility
            - Sets up connection pooling
        """

    def visit(self, portal_name):
        """
        Make initial visit request to bypass Cloudflare protection.
        
        Args:
            portal_name (str): Udemy portal name
            
        Returns:
            bool: Success status of visit request
            
        Side Effects:
            - Sets necessary cookies for subsequent requests
            - Handles Cloudflare bot detection
        """

    def _get(self, url, params=None):
        """
        Perform GET request with retry logic.
        
        Args:
            url (str): Request URL
            params (dict): Query parameters
            
        Returns:
            requests.Response: HTTP response object
            
        Features:
            - Automatic retry on failure (up to 10 attempts)
            - Handles 502/503 errors gracefully
            - Uses cookie jar for authentication
            - Exponential backoff on errors
        """
```

## UdemyAuth Class

Handles authentication and session management.

```python
class UdemyAuth:
    def __init__(self, username="", password="", cache_session=False):
        """
        Initialize authentication handler.
        
        Args:
            username (str): Username (currently unused)
            password (str): Password (currently unused)
            cache_session (bool): Whether to cache session
            
        Side Effects:
            - Creates Session instance
            - Prepares for future authentication methods
        """
```

## Utility Functions

### Content Processing
```python
def deEmojify(inputStr):
    """
    Remove emoji characters from strings.
    
    Args:
        inputStr (str): Input string with potential emojis
        
    Returns:
        str: String with emojis removed
        
    Use Case:
        - Sanitizing filenames
        - Cleaning course titles
    """

def parse_chapter_filter(chapter_str):
    """
    Parse chapter filter string into set of chapter numbers.
    
    Args:
        chapter_str (str): Filter string (e.g., "1,3-5,7,9-11")
        
    Returns:
        set: Set of chapter numbers to download
        
    Supported Formats:
        - Single numbers: "1,3,5"
        - Ranges: "1-5"
        - Mixed: "1,3-5,7,9-11"
        
    Error Handling:
        - Logs invalid ranges
        - Skips malformed entries
    """
```

### Video Processing
```python
def mux_process(video_filepath, audio_filepath, video_title, output_path, 
                audio_key=None, video_key=None):
    """
    Mux video and audio streams with optional decryption.
    
    Args:
        video_filepath (str): Path to video file
        audio_filepath (str): Path to audio file
        video_title (str): Title for metadata
        output_path (str): Output file path
        audio_key (str, optional): Audio decryption key
        video_key (str, optional): Video decryption key
        
    Returns:
        int: FFmpeg return code
        
    Features:
        - H.265 encoding support
        - Hardware acceleration (NVENC)
        - Custom CRF and preset settings
        - Metadata embedding
        - Cross-platform command generation
        
    Side Effects:
        - Creates temporary files during processing
        - Logs FFmpeg output for debugging
        
    Raises:
        Exception: If muxing fails (non-zero return code)
    """
```

### Download Management
```python
def handle_segments(url, format_id, lecture_id, video_title, output_path, chapter_dir):
    """
    Download and process DASH segments for encrypted content.
    
    Args:
        url (str): MPD manifest URL or file path
        format_id (str): yt-dlp format identifier
        lecture_id (str): Unique lecture identifier
        video_title (str): Lecture title for metadata
        output_path (str): Final output file path
        chapter_dir (str): Chapter directory for temporary files
        
    Process:
        1. Downloads encrypted video and audio segments
        2. Extracts decryption keys (KID)
        3. Looks up decryption keys from keyfile
        4. Muxes streams with decryption
        5. Cleans up temporary files
        
    Side Effects:
        - Changes working directory temporarily
        - Creates encrypted segment files
        - Removes temporary files after processing
        
    Error Handling:
        - Validates return codes at each step
        - Logs detailed error information
        - Gracefully handles missing keys
    """
```

## Global State Management

The application uses several global variables for configuration:

```python
# Download configuration
dl_assets = False          # Download supplementary assets
dl_captions = False        # Download subtitles
dl_quizzes = False         # Download quizzes
skip_lectures = False      # Skip video downloads
caption_locale = "en"      # Subtitle language
quality = None             # Video quality preference

# Processing options
keep_vtt = False           # Keep VTT files after SRT conversion
skip_hls = False           # Skip HLS stream processing
concurrent_downloads = 10   # Max concurrent segment downloads
use_h265 = False           # Use H.265 encoding
use_nvenc = False          # Use NVIDIA hardware encoding

# Authentication
bearer_token = None        # API bearer token
browser = None             # Browser for cookie extraction
cj = None                  # Cookie jar instance

# Course information
portal_name = None         # Udemy portal (www, business, etc.)
course_name = None         # Course identifier
keys = {}                  # Decryption key dictionary

# File management
id_as_course_name = False  # Use course ID as folder name
use_continuous_lecture_numbers = False  # Sequential numbering
chapter_filter = None      # Chapter filter set
```

## Error Handling Patterns

### Connection Errors
```python
try:
    resp = self.session._get(url).json()
except conn_error as error:
    logger.fatal(f"Connection error: {error}")
    time.sleep(0.8)
    sys.exit(1)
```

### Retry Logic
```python
for i in range(10):
    req = self._session.get(url, cookies=cj, params=params)
    if req.ok or req.status_code in [502, 503]:
        return req
    if not req.ok:
        logger.error(f"Failed request {url}")
        logger.error(f"{req.status_code} {req.reason}, retrying (attempt {i})...")
        time.sleep(0.8)
```

### Graceful Degradation
```python
try:
    video_kid = extract_kid(video_filepath_enc)
    logger.info("KID for video file is: " + video_kid)
except Exception:
    logger.exception(f"Error extracting video kid")
    return  # Skip this lecture instead of crashing
```