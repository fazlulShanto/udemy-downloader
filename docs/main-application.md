# Main Application

This document covers the main application entry point, command-line interface, and the primary workflow orchestration.

## Entry Point

The application starts with two main functions:

### pre_run()
```python
def pre_run():
    """
    Initialize application before main execution.
    
    Responsibilities:
        - Parse command-line arguments
        - Set up logging system
        - Create necessary directories
        - Load configuration from files
        - Validate external dependencies
        
    Side Effects:
        - Sets global configuration variables
        - Creates logs/, saved/, out_dir/ directories
        - Loads decryption keys from keyfile.json
        - Configures colored logging for console and file output
        
    Global Variables Set:
        - All command-line argument values
        - Logger instance with appropriate handlers
        - Key dictionary from keyfile.json
    """
```

### main()
```python
def main():
    """
    Main application workflow orchestration.
    
    Process:
        1. Validate external tool dependencies
        2. Load environment configuration
        3. Initialize Udemy client with authentication
        4. Fetch course information and curriculum
        5. Process and download course content
        6. Handle caching and resume functionality
        
    Dependencies Checked:
        - aria2c: For high-speed downloads
        - ffmpeg: For video processing
        - shaka-packager: For DASH stream handling
        
    Exit Conditions:
        - Missing external tools (when not skipping lectures)
        - Authentication failure
        - Course not found or access denied
    """
```

## Command-Line Interface

### Argument Parser Configuration

The application uses `argparse` for comprehensive command-line interface:

```python
parser = argparse.ArgumentParser(description="Udemy Downloader")
```

#### Required Arguments
```python
parser.add_argument("-c", "--course-url", required=True,
                   help="The URL of the course to download")
```

#### Authentication Options
```python
parser.add_argument("-b", "--bearer", 
                   help="The Bearer token to use")
parser.add_argument("--browser", 
                   choices=["chrome", "firefox", "opera", "edge", "brave", 
                           "chromium", "vivaldi", "safari"],
                   help="The browser to extract cookies from")
```

#### Download Control
```python
parser.add_argument("-q", "--quality", type=int,
                   help="Download specific video quality")
parser.add_argument("--skip-lectures", action="store_true",
                   help="Skip lecture video downloads")
parser.add_argument("--download-assets", action="store_true",
                   help="Download supplementary assets")
parser.add_argument("--download-captions", action="store_true",
                   help="Download captions/subtitles")
parser.add_argument("--download-quizzes", action="store_true",
                   help="Download quiz content")
```

#### Language and Localization
```python
parser.add_argument("-l", "--lang", default="en",
                   help="Caption language (default: en, use 'all' for all languages)")
```

#### Performance Options
```python
parser.add_argument("-cd", "--concurrent-downloads", type=int,
                   help="Max concurrent downloads (1-30)")
parser.add_argument("--skip-hls", action="store_true",
                   help="Skip HLS stream processing for faster fetching")
```

#### Video Encoding
```python
parser.add_argument("--use-h265", action="store_true",
                   help="Encode videos with H.265 codec")
parser.add_argument("--h265-crf", type=int, default=28,
                   help="H.265 CRF value (default: 28)")
parser.add_argument("--h265-preset", default="medium",
                   help="H.265 encoding preset (default: medium)")
parser.add_argument("--use-nvenc", action="store_true",
                   help="Use NVIDIA hardware encoding")
```

#### File Management
```python
parser.add_argument("--out", "-o", 
                   help="Output directory path")
parser.add_argument("--keep-vtt", action="store_true",
                   help="Keep VTT files after SRT conversion")
parser.add_argument("--id-as-course-name", action="store_true",
                   help="Use course ID as folder name")
parser.add_argument("--continue-lecture-numbers", "-n", action="store_true",
                   help="Use continuous lecture numbering")
```

#### Chapter Filtering
```python
parser.add_argument("--chapter", 
                   help="Download specific chapters (e.g., '1,3-5,7,9-11')")
```

#### Caching and Resume
```python
parser.add_argument("--save-to-file", action="store_true",
                   help="Save course data to file for later use")
parser.add_argument("--load-from-file", action="store_true",
                   help="Load course data from previously saved file")
```

#### Information and Debugging
```python
parser.add_argument("--info", action="store_true",
                   help="Print course information only, no downloads")
parser.add_argument("--log-level", 
                   help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
parser.add_argument("-sc", "--subscription-course", action="store_true",
                   help="Mark as subscription course for detection issues")
```

## Workflow Functions

### Course Processing Pipeline

#### parse_new()
```python
def parse_new(udemy, udemy_object):
    """
    Process and download course content.
    
    Args:
        udemy (Udemy): Authenticated Udemy client instance
        udemy_object (dict): Processed course data structure
        
    Process:
        1. Create course directory structure
        2. Filter chapters based on user selection
        3. Process each chapter and its lectures
        4. Handle different content types (video, quiz, article)
        5. Download assets and subtitles as requested
        
    Content Type Handling:
        - Videos: Quality selection, DRM processing, encoding
        - Quizzes: Template rendering, data extraction
        - Articles: HTML generation with templates
        - Assets: File downloads, external link shortcuts
        
    Side Effects:
        - Creates directory structure
        - Downloads and processes files
        - Generates HTML templates
        - Updates progress logs
    """
```

#### _print_course_info()
```python
def _print_course_info(udemy, udemy_object):
    """
    Display detailed course information without downloading.
    
    Args:
        udemy (Udemy): Udemy client instance
        udemy_object (dict): Course data structure
        
    Information Displayed:
        - Course title and metadata
        - Chapter count and structure
        - Lecture details per chapter
        - Available video qualities
        - DRM status for each lecture
        - Asset counts and types
        - Available subtitle languages
        
    Features:
        - Chapter filtering support
        - Quality information extraction
        - Content type identification
        - Warning for large courses (>100 lectures)
    """
```

### Content Processing Functions

#### process_lecture()
```python
def process_lecture(lecture, lecture_path, chapter_dir):
    """
    Process individual lecture based on content type and encryption status.
    
    Args:
        lecture (dict): Processed lecture data
        lecture_path (str): Target file path for lecture
        chapter_dir (str): Chapter directory path
        
    Processing Logic:
        - Encrypted content: Use handle_segments() for DASH processing
        - Unencrypted content: Direct download or HLS processing
        - Quality selection based on user preference
        - Skip if file already exists
        
    Video Processing:
        - Quality selection (best available or user-specified)
        - Format detection (HLS, direct download)
        - Optional H.265 encoding
        - Progress logging and error handling
        
    Side Effects:
        - Downloads video files
        - Creates temporary files during processing
        - Logs download progress and errors
    """
```

#### process_quiz()
```python
def process_quiz(udemy, lecture, chapter_dir):
    """
    Process quiz content and generate HTML files.
    
    Args:
        udemy (Udemy): Udemy client for API access
        lecture (dict): Lecture data containing quiz ID
        chapter_dir (str): Chapter directory for output
        
    Quiz Types:
        - Normal Quiz: Multiple choice questions with explanations
        - Coding Assignment: Programming exercises with tests and solutions
        
    Processing:
        - Fetches quiz data from API
        - Determines quiz type (normal vs coding)
        - Renders appropriate HTML template
        - Saves interactive HTML file
        
    Template Data:
        - Quiz metadata (title, description, pass percentage)
        - Question and answer data
        - Explanations and feedback
        - Interactive JavaScript functionality
    """
```

#### process_caption()
```python
def process_caption(caption, lecture_title, lecture_dir, tries=0):
    """
    Download and process subtitle files.
    
    Args:
        caption (dict): Caption data with download URL and language
        lecture_title (str): Lecture title for filename
        lecture_dir (str): Directory for caption files
        tries (int): Current retry attempt (for error handling)
        
    Processing:
        - Downloads VTT or SRT caption files
        - Converts VTT to SRT format if needed
        - Handles multiple languages
        - Implements retry logic for failed downloads
        
    Filename Format:
        - Pattern: "{lecture_title}_{language}.{extension}"
        - Sanitized for filesystem compatibility
        - Language code included for identification
        
    Features:
        - Automatic VTT to SRT conversion
        - Optional VTT file retention
        - Retry mechanism (up to 3 attempts)
        - Progress logging
    """
```

## Dependency Validation

### External Tool Checking
```python
def check_for_aria():
    """
    Verify aria2c availability and functionality.
    
    Returns:
        bool: True if aria2c is available and working
        
    Test Method:
        - Executes 'aria2c -v' command
        - Captures output to verify installation
        - Handles FileNotFoundError for missing installation
    """

def check_for_ffmpeg():
    """
    Verify FFmpeg availability and functionality.
    
    Returns:
        bool: True if FFmpeg is available and working
        
    Test Method:
        - Executes 'ffmpeg' command (expects help output)
        - Verifies installation and PATH configuration
        - Required for video processing and muxing
    """

def check_for_shaka():
    """
    Verify Shaka Packager availability and functionality.
    
    Returns:
        bool: True if Shaka Packager is available and working
        
    Test Method:
        - Executes 'shaka-packager -version' command
        - Required for DASH stream processing
        - Critical for encrypted content handling
    """
```

## Configuration Loading

### Environment Variables
```python
load_dotenv()  # Load from .env file
bearer_token = bearer_token or os.getenv("UDEMY_BEARER")
```

### Keyfile Loading
```python
if os.path.exists(KEY_FILE_PATH):
    with open(KEY_FILE_PATH, encoding="utf8", mode="r") as keyfile:
        keys = json.loads(keyfile.read())
else:
    logger.warning("Keyfile not found! Won't be able to decrypt encrypted videos!")
```

### Directory Creation
```python
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(SAVED_DIR).mkdir(parents=True, exist_ok=True)
Path(LOG_DIR_PATH).mkdir(parents=True, exist_ok=True)
```

## Logging Configuration

### Multi-Handler Setup
```python
# Console logging with colors
console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(console_formatter)

# File logging without colors
file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setFormatter(file_formatter)

# Combine handlers
logger = logging.getLogger("udemy-downloader")
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)
logger.addHandler(file_handler)
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages (default)
- **WARNING**: Warning messages for non-critical issues
- **ERROR**: Error messages for recoverable problems
- **CRITICAL**: Critical errors that may cause termination

## Error Handling Strategy

### Graceful Degradation
- Missing external tools: Exit with clear error message
- Authentication failure: Provide troubleshooting guidance
- Network issues: Retry with exponential backoff
- File system errors: Log and continue with next item

### User Feedback
- Progress indicators for long operations
- Clear error messages with suggested solutions
- Warnings for potentially problematic operations
- Success confirmations for completed tasks

### Recovery Mechanisms
- Resume interrupted downloads
- Skip corrupted or inaccessible content
- Retry failed operations with backoff
- Cache intermediate results for efficiency