# Utility Functions

This document covers all utility functions, helper modules, and supporting components used throughout the application.

## Core Utilities (utils.py)

### DRM Key Extraction

#### extract_kid()
```python
def extract_kid(mp4_file):
    """
    Extract Key ID (KID) from MP4 file's PSSH header for DRM decryption.
    
    Args:
        mp4_file (str): Path to MP4 file containing PSSH header
        
    Returns:
        str: Hexadecimal Key ID in lowercase, or None if not found
        
    Process:
        1. Parse MP4 file structure using mp4parse
        2. Locate 'moov' box containing metadata
        3. Find PSSH box with Widevine system ID
        4. Extract and decode Widevine PSSH data
        5. Return content_id as hexadecimal string
        
    Raises:
        Exception: If file doesn't exist
        
    Dependencies:
        - mp4parse: For MP4 box structure parsing
        - widevine_pssh_data_pb2: For protobuf PSSH data parsing
        - codecs: For hex decoding
        - base64: For encoding operations
        
    Usage:
        Used in handle_segments() to extract decryption keys
        for encrypted video and audio streams.
    """
```

## TLS Configuration (tls.py)

### Custom SSL Adapter

#### SSLCiphers Class
```python
class SSLCiphers(HTTPAdapter):
    """
    Custom HTTP Adapter for modifying TLS cipher suites and fingerprints.
    
    Purpose:
        - Customize SSL/TLS handshake behavior
        - Modify cipher list for compatibility
        - Bypass certain security restrictions
        
    Features:
        - Custom cipher list configuration
        - Disabled hostname verification for flexibility
        - Pool manager customization
        - Proxy support with custom SSL context
    """
    
    def __init__(self, cipher_list=None, *args, **kwargs):
        """
        Initialize SSL adapter with custom cipher configuration.
        
        Args:
            cipher_list (str, optional): Custom cipher list string
            
        Default Behavior:
            - Creates default SSL context
            - Disables hostname checking
            - Uses Python's default ciphers if none specified
            
        Side Effects:
            - Modifies SSL context for all requests using this adapter
        """
    
    def init_poolmanager(self, *args, **kwargs):
        """
        Initialize connection pool manager with custom SSL context.
        
        Override:
            Injects custom SSL context into connection pool
            
        Returns:
            Pool manager with custom SSL configuration
        """
    
    def proxy_manager_for(self, *args, **kwargs):
        """
        Create proxy manager with custom SSL context.
        
        Override:
            Ensures proxy connections use custom SSL settings
            
        Returns:
            Proxy manager with custom SSL configuration
        """
```

## Subtitle Conversion (vtt_to_srt.py)

### VTT to SRT Converter

#### convert()
```python
def convert(directory, filename):
    """
    Convert WebVTT subtitle files to SubRip (SRT) format.
    
    Args:
        directory (str): Directory containing the VTT file
        filename (str): Base filename without extension
        
    Process:
        1. Read VTT file using webvtt library
        2. Parse timing and text data
        3. Convert to SRT format with proper indexing
        4. Handle HTML entities in subtitle text
        5. Write SRT file with UTF-8 encoding
        
    File Handling:
        - Input: {filename}.vtt
        - Output: {filename}.srt
        - Encoding: UTF-8 with error ignoring
        
    Features:
        - Automatic timing conversion
        - HTML entity decoding (e.g., &amp; → &)
        - Sequential subtitle indexing
        - Proper SRT formatting
        
    Dependencies:
        - webvtt: For VTT file parsing
        - pysrt: For SRT time format handling
        - html: For entity decoding
        
    Error Handling:
        - Ignores encoding errors during file operations
        - Continues processing even with malformed entries
    """
```

## MP4 Parsing (mp4parse.py)

### MP4 Box Structure Parser

This module provides comprehensive MP4/F4V file parsing capabilities for DRM analysis.

#### F4VParser Class
```python
class F4VParser:
    """
    Parser for MP4/F4V files with focus on box structure analysis.
    
    Capabilities:
        - Parse complete MP4 box hierarchy
        - Extract DRM-related metadata
        - Handle various box types (moov, moof, pssh, etc.)
        - Support for both file and byte stream input
    """
    
    @classmethod
    def parse(cls, filename=None, bytes_input=None, file_input=None, 
              offset_bytes=0, headers_only=False):
        """
        Parse MP4 file or bytes into box structures.
        
        Args:
            filename (str, optional): Path to MP4 file
            bytes_input (bytes, optional): MP4 data as bytes
            file_input (file, optional): File object to read from
            offset_bytes (int): Starting offset for parsing
            headers_only (bool): Parse headers only (for truncated files)
            
        Returns:
            Generator yielding parsed box objects
            
        Supported Box Types:
            - abst: Bootstrap Info Box
            - afra: Fragment Random Access Box
            - mdat: Media Data Box
            - moof: Movie Fragment Box
            - moov: Movie Box (contains PSSH)
            - mfhd: Movie Fragment Header
            - pssh: Protection System Specific Header
            
        Usage Patterns:
            # Parse from file
            boxes = F4VParser.parse(filename="video.mp4")
            
            # Parse from bytes
            boxes = F4VParser.parse(bytes_input=mp4_data)
            
            # Headers only (for damaged files)
            headers = F4VParser.parse(filename="video.mp4", headers_only=True)
        """
```

#### Box Type Classes

##### ProtectionSystemSpecificHeader
```python
class ProtectionSystemSpecificHeader(MixinDictRepr):
    """
    Represents PSSH box containing DRM information.
    
    Attributes:
        type (str): Always "pssh"
        header (BoxHeader): Box header information
        system_id (str): DRM system identifier (Widevine, PlayReady, etc.)
        payload (str): Encrypted payload data
        
    Widevine System ID:
        "edef8ba979d64acea3c827dcd51d21ed"
        
    Usage:
        Used by extract_kid() to locate Widevine DRM data
        in encrypted MP4 files.
    """
```

##### MovieBox
```python
class MovieBox(MixinDictRepr):
    """
    Represents moov box containing movie metadata.
    
    Attributes:
        type (str): Always "moov"
        header (BoxHeader): Box header information
        pssh (list): List of PSSH boxes found in movie
        
    Child Boxes:
        - Multiple PSSH boxes for different DRM systems
        - Track information
        - Metadata
        
    Parsing:
        Recursively parses child boxes and collects
        all PSSH boxes into a list for DRM processing.
    """
```

#### Utility Methods

##### Box Header Parsing
```python
@staticmethod
def _read_box_header(bs):
    """
    Read MP4 box header from bitstream.
    
    Args:
        bs (bitstring.ConstBitStream): Bitstream positioned at box start
        
    Returns:
        BoxHeader: Named tuple with size, type, and header_size
        
    Header Format:
        - 32-bit size field
        - 32-bit type field (ASCII)
        - Optional 64-bit extended size (if size == 1)
        
    Special Cases:
        - Size == 1: Extended 64-bit size follows
        - Size == 0: Box extends to end of file
        - Non-ASCII types: Kept as bytes
    """
```

## Download Functions

### High-Speed Downloads

#### download_aria()
```python
def download_aria(url, file_dir, filename):
    """
    Download files using aria2c for high-speed concurrent downloads.
    
    Args:
        url (str): Download URL
        file_dir (str): Target directory
        filename (str): Target filename
        
    Returns:
        int: aria2c return code (0 = success)
        
    Configuration:
        - 16 connections per server (-j16)
        - 20 segments per file (-s20)
        - 16 concurrent downloads (-x16)
        - Resume capability (-c)
        - IPv6 disabled for compatibility
        - Auto file renaming disabled
        - Summary interval disabled for cleaner output
        
    Command Generated:
        aria2c {url} -o {filename} -d {file_dir} -j16 -s20 -x16 -c 
               --auto-file-renaming=false --summary-interval=0 
               --disable-ipv6 --follow-torrent=false
               
    Error Handling:
        - Logs stdout/stderr for debugging
        - Raises exception on non-zero return code
        - Subprocess output captured for analysis
        
    Use Cases:
        - Large file downloads
        - Supplementary asset downloads
        - Resume interrupted downloads
    """
```

#### download()
```python
def download(url, path, filename):
    """
    Download files with resume capability using requests.
    
    Args:
        url (str): Download URL
        path (str): Target file path
        filename (str): Filename for progress display
        
    Returns:
        int: Total file size downloaded
        
    Features:
        - Resume partial downloads
        - Progress bar with tqdm
        - Chunked downloading (1KB chunks)
        - Range request support
        - File size validation
        
    Resume Logic:
        1. Check if file exists and get current size
        2. Compare with remote file size
        3. Use Range header to resume from current position
        4. Append new data to existing file
        
    Progress Display:
        - Shows download speed
        - Displays percentage complete
        - Updates in real-time
        - Human-readable file sizes
        
    Error Handling:
        - HTTP error responses
        - Network connectivity issues
        - File system errors
        - Incomplete downloads
    """
```

## String Processing

### Text Sanitization

#### deEmojify()
```python
def deEmojify(inputStr):
    """
    Remove emoji characters from strings for filesystem compatibility.
    
    Args:
        inputStr (str): Input string potentially containing emojis
        
    Returns:
        str: String with all emoji characters removed
        
    Implementation:
        Uses demoji library to identify and remove emoji characters
        
    Use Cases:
        - Sanitizing course titles for directory names
        - Cleaning lecture titles for filenames
        - Preparing text for filesystem operations
        
    Dependencies:
        - demoji: Emoji detection and removal library
        
    Examples:
        "Python 🐍 Course" → "Python  Course"
        "Web Dev 💻🚀" → "Web Dev "
    """
```

### Chapter Filtering

#### parse_chapter_filter()
```python
def parse_chapter_filter(chapter_str):
    """
    Parse chapter filter string into set of chapter numbers.
    
    Args:
        chapter_str (str): Filter specification string
        
    Returns:
        set: Set of integer chapter numbers to include
        
    Supported Formats:
        - Individual chapters: "1,3,5"
        - Ranges: "1-5" (inclusive)
        - Mixed: "1,3-5,7,9-11"
        - Whitespace tolerant: "1, 3 - 5, 7"
        
    Parsing Logic:
        1. Split by commas to get individual parts
        2. For each part, check if it contains a dash
        3. If dash present, parse as range (start-end)
        4. If no dash, parse as single number
        5. Add all numbers to result set
        
    Error Handling:
        - Invalid ranges logged and skipped
        - Non-numeric values logged and skipped
        - Malformed input gracefully handled
        - Empty input returns empty set
        
    Examples:
        "1,3,5" → {1, 3, 5}
        "1-3" → {1, 2, 3}
        "1,3-5,7" → {1, 3, 4, 5, 7}
        "invalid" → {} (with error log)
    """
```

## Time and Duration Utilities

### Duration Conversion

#### durationtoseconds()
```python
def durationtoseconds(period):
    """
    Convert ISO 8601 duration format to seconds.
    
    Args:
        period (str): ISO 8601 duration string (e.g., "PT1H30M45.5S")
        
    Returns:
        float: Duration in seconds, or None if invalid format
        
    Supported Format:
        PT[nD][nH][nM][n.nS]
        - PT: Duration prefix (required)
        - nD: Days (optional)
        - nH: Hours (optional)
        - nM: Minutes (optional)
        - n.nS: Seconds with decimal (optional)
        
    Parsing Logic:
        1. Verify PT prefix
        2. Extract days, hours, minutes, seconds
        3. Handle decimal seconds
        4. Calculate total seconds
        
    Examples:
        "PT1H30M" → 5400.0 (1.5 hours)
        "PT45.5S" → 45.5 (45.5 seconds)
        "PT1D2H3M4.5S" → 93784.5 (1 day, 2:03:04.5)
        
    Error Handling:
        - Invalid format returns None
        - Logs error for debugging
        - Graceful handling of missing components
        
    Use Cases:
        - Converting video duration metadata
        - Calculating total course length
        - Progress tracking calculations
    """
```

## Subprocess Management

### Process Output Logging

#### log_subprocess_output()
```python
def log_subprocess_output(prefix, pipe):
    """
    Log subprocess output for debugging and monitoring.
    
    Args:
        prefix (str): Log prefix to identify the subprocess
        pipe (IO[bytes]): Subprocess stdout or stderr pipe
        
    Process:
        1. Read output byte by byte to avoid blocking
        2. Decode bytes to UTF-8 strings
        3. Log each line with specified prefix
        4. Flush pipe when complete
        
    Usage Pattern:
        process = subprocess.Popen(command, stdout=PIPE, stderr=PIPE)
        log_subprocess_output("FFMPEG-STDOUT", process.stdout)
        log_subprocess_output("FFMPEG-STDERR", process.stderr)
        
    Benefits:
        - Real-time output monitoring
        - Debugging subprocess issues
        - Progress tracking for long operations
        - Error diagnosis and troubleshooting
        
    Thread Safety:
        - Safe for concurrent use with multiple processes
        - Non-blocking read operations
        - Proper resource cleanup
    """
```

## Constants and Configuration (constants.py)

### API Configuration

#### Authentication Constants
```python
CLIENT_SECRET = "f2lgDUDxjFiOlVHUpwQNFUfCQPyMO0tJQMaud53PF01UKueW8enYjeEYoyVeP0bb2XVEDkJ5GLJaVTfM5QgMVz6yyXyydZdA5QhzgvG9UmCPUYaCrIVf7VpmiilfbLJc"
CLIENT_ID = "TH96Ov3Ebo3OtgoSH5mOYzYolcowM3ycedWQDDce"
BASIC_AUTH = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")
```

#### HTTP Headers
```python
HEADERS = {
    "User-Agent": "okhttp/4.12.0 UdemyAndroid 9.51.2(594) (phone)",
    "Accept-Encoding": "gzip",
    "x-mobile-visit-enabled": "true",
    "x-udemy-client-secret": CLIENT_SECRET,
    "authorization": "Basic {}".format(BASIC_AUTH),
    "x-udemy-client-id": CLIENT_ID,
    "accept-language": "en_US",
    "x-version-name": "9.51.2",
    "x-client-name": "Udemy-Android",
}
```

### URL Templates

#### URLS Class
```python
class URLS:
    """
    Centralized URL template management for Udemy API endpoints.
    
    Template Variables:
        - {portal_name}: Udemy portal (www, business, etc.)
        - {course_id}: Numeric course identifier
        - {quiz_id}: Quiz/assessment identifier
        - {course_name}: Course name for search
        
    Endpoint Categories:
        - Course information and curriculum
        - User enrollment and subscriptions
        - Quiz and assessment data
        - Authentication and visits
    """
    
    CURRICULUM_ITEMS = "https://{portal_name}.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/"
    COURSE = "https://{portal_name}.udemy.com/api-2.0/courses/{course_id}/"
    MY_COURSES = "https://{portal_name}.udemy.com/api-2.0/users/me/subscribed-courses?fields[course]=id,url,title,published_title&ordering=-last_accessed,-access_time&page=1&page_size=10000"
    QUIZ = "https://{portal_name}.udemy.com/api-2.0/quizzes/{quiz_id}/assessments/?version=1&page_size=250&fields[assessment]=id,assessment_type,prompt,correct_response,section,question_plain,related_lectures"
    # ... additional URLs
```

### File Paths

#### Path Constants
```python
HOME_DIR = os.getcwd()
SAVED_DIR = os.path.join(os.getcwd(), "saved")
KEY_FILE_PATH = os.path.join(os.getcwd(), "keyfile.json")
COOKIE_FILE_PATH = os.path.join(os.getcwd(), "cookies.txt")
LOG_DIR_PATH = os.path.join(os.getcwd(), "logs")
LOG_FILE_PATH = os.path.join(os.getcwd(), "logs", f"{time.strftime('%Y-%m-%d-%I-%M-%S')}.log")
```

### Logging Configuration

#### Log Format Settings
```python
LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(funcName)s:%(lineno)d] %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%I:%M:%S"
LOG_LEVEL = logging.INFO
```

### API Parameters

#### Request Parameters
```python
CURRICULUM_ITEMS_PARAMS = {
    "fields[lecture]": "title,object_index,created,asset,supplementary_assets,description,download_url",
    "fields[quiz]": "title,object_index,type",
    "fields[practice]": "title,object_index",
    "fields[chapter]": "title,object_index",
    "fields[asset]": "title,filename,asset_type,status,is_external,media_license_token,course_is_drmed,media_sources,captions,slides,slide_urls,download_urls,external_url,stream_urls,@min,status,delayed_asset_message,processing_errors,body",
    "caching_intent": True,
    "page_size": "200",
}
```