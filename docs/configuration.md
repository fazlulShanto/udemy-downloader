# Configuration

This document covers all configuration options, environment variables, and settings files used by the Udemy Downloader.

## Configuration Files

### Environment Configuration (.env)

The `.env` file stores environment variables for the application.

#### Setup
```bash
# Copy sample file
cp .env.sample .env

# Edit with your values
nano .env
```

#### Available Variables
```bash
# Required: Udemy Bearer Token
UDEMY_BEARER=your_bearer_token_here

# Optional: Default course URL (used by Docker Compose)
COURSE_URL=https://www.udemy.com/course/your-course-name/
```

#### Usage in Application
```python
from dotenv import load_dotenv
import os

load_dotenv()
bearer_token = os.getenv("UDEMY_BEARER")
course_url = os.getenv("COURSE_URL")
```

### Decryption Keys (keyfile.json)

Stores decryption keys for DRM-protected content.

#### Setup
```bash
# Copy sample file
cp keyfile.example.json keyfile.json

# Edit with your keys
nano keyfile.json
```

#### File Format
```json
{
    "key_id_1": "decryption_key_1",
    "key_id_2": "decryption_key_2",
    "example_kid": "example_key_value"
}
```

#### Key Format Details
- **Key ID (KID)**: 32-character hexadecimal string (lowercase)
- **Decryption Key**: 32-character hexadecimal string
- **Source**: Must be obtained through legal means

#### Loading in Application
```python
import json
import os

if os.path.exists(KEY_FILE_PATH):
    with open(KEY_FILE_PATH, encoding="utf8", mode="r") as keyfile:
        keys = json.loads(keyfile.read())
else:
    logger.warning("Keyfile not found! Won't be able to decrypt encrypted videos!")
```

### Browser Cookies (cookies.txt)

Optional Netscape-format cookie file for authentication.

#### Format
```
# Netscape HTTP Cookie File
.udemy.com	TRUE	/	FALSE	1234567890	cookie_name	cookie_value
```

#### Usage
```bash
python main.py -c <course_url> --browser file
```

## Command-Line Configuration

### Global Options

#### Authentication
```bash
# Bearer token authentication
python main.py -c <url> -b <bearer_token>

# Browser cookie extraction
python main.py -c <url> --browser chrome

# Cookie file authentication
python main.py -c <url> --browser file
```

#### Output Control
```bash
# Custom output directory
python main.py -c <url> -o /path/to/output

# Use course ID as folder name (shorter paths)
python main.py -c <url> --id-as-course-name

# Continuous lecture numbering
python main.py -c <url> --continue-lecture-numbers
```

### Content Selection

#### What to Download
```bash
# Download everything (default behavior)
python main.py -c <url>

# Skip video lectures (metadata only)
python main.py -c <url> --skip-lectures

# Download supplementary assets
python main.py -c <url> --download-assets

# Download captions/subtitles
python main.py -c <url> --download-captions

# Download quizzes
python main.py -c <url> --download-quizzes

# Combination example
python main.py -c <url> --download-assets --download-captions --download-quizzes
```

#### Chapter Filtering
```bash
# Download specific chapters
python main.py -c <url> --chapter "1,3,5"

# Download chapter ranges
python main.py -c <url> --chapter "1-5"

# Mixed chapter selection
python main.py -c <url> --chapter "1,3-5,7,9-11"
```

### Quality and Performance

#### Video Quality
```bash
# Download best quality (default)
python main.py -c <url>

# Download specific quality
python main.py -c <url> -q 720
python main.py -c <url> -q 1080

# Skip HLS processing (faster, may miss 1080p)
python main.py -c <url> --skip-hls
```

#### Download Performance
```bash
# Set concurrent downloads (1-30)
python main.py -c <url> --concurrent-downloads 20
python main.py -c <url> -cd 15

# Default is 10 concurrent downloads
```

### Language and Localization

#### Subtitle Languages
```bash
# Download English subtitles (default)
python main.py -c <url> --download-captions

# Download specific language
python main.py -c <url> --download-captions -l es  # Spanish
python main.py -c <url> --download-captions -l fr  # French
python main.py -c <url> --download-captions -l de  # German

# Download all available languages
python main.py -c <url> --download-captions -l all

# Keep VTT files (don't convert to SRT)
python main.py -c <url> --download-captions --keep-vtt
```

### Video Encoding Options

#### H.265 Encoding
```bash
# Enable H.265 encoding
python main.py -c <url> --use-h265

# Custom CRF value (quality control)
python main.py -c <url> --use-h265 --h265-crf 20  # Higher quality
python main.py -c <url> --use-h265 --h265-crf 35  # Lower quality

# Custom encoding preset (speed vs quality)
python main.py -c <url> --use-h265 --h265-preset faster
python main.py -c <url> --use-h265 --h265-preset slower

# Hardware acceleration (NVIDIA GPUs)
python main.py -c <url> --use-h265 --use-nvenc
```

### Caching and Resume

#### Data Caching
```bash
# Save course data for later use
python main.py -c <url> --save-to-file

# Load previously saved course data
python main.py -c <url> --load-from-file

# Combination for efficiency
python main.py -c <url> --save-to-file --info  # Save data, show info only
python main.py -c <url> --load-from-file        # Use saved data for download
```

### Information and Debugging

#### Information Display
```bash
# Show course information only (no downloads)
python main.py -c <url> --info

# Combine with chapter filtering
python main.py -c <url> --info --chapter "1-3"
```

#### Logging Control
```bash
# Set logging level
python main.py -c <url> --log-level DEBUG
python main.py -c <url> --log-level INFO     # Default
python main.py -c <url> --log-level WARNING
python main.py -c <url> --log-level ERROR
python main.py -c <url> --log-level CRITICAL
```

## Application Constants

### File Paths (constants.py)

#### Directory Structure
```python
HOME_DIR = os.getcwd()                    # Application root directory
SAVED_DIR = os.path.join(os.getcwd(), "saved")           # Cached data
DOWNLOAD_DIR = os.path.join(os.getcwd(), "out_dir")      # Default output
LOG_DIR_PATH = os.path.join(os.getcwd(), "logs")         # Log files
```

#### Configuration Files
```python
KEY_FILE_PATH = os.path.join(os.getcwd(), "keyfile.json")
COOKIE_FILE_PATH = os.path.join(os.getcwd(), "cookies.txt")
LOG_FILE_PATH = os.path.join(os.getcwd(), "logs", f"{time.strftime('%Y-%m-%d-%I-%M-%S')}.log")
```

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

### API Endpoints

#### URL Templates
```python
class URLS:
    CURRICULUM_ITEMS = "https://{portal_name}.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/"
    COURSE = "https://{portal_name}.udemy.com/api-2.0/courses/{course_id}/"
    MY_COURSES = "https://{portal_name}.udemy.com/api-2.0/users/me/subscribed-courses?fields[course]=id,url,title,published_title&ordering=-last_accessed,-access_time&page=1&page_size=10000"
    SUBSCRIPTION_COURSES = "https://{portal_name}.udemy.com/api-2.0/users/me/subscription-course-enrollments?..."
    QUIZ = "https://{portal_name}.udemy.com/api-2.0/quizzes/{quiz_id}/assessments/?version=1&page_size=250&..."
    VISIT = "https://{portal_name}.udemy.com/api-2.0/visits/current/?fields%5Bvisit%5D=@default,visitor,country&locale=en_US"
```

### Request Parameters

#### Curriculum Items
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

### Logging Configuration

#### Log Format
```python
LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(funcName)s:%(lineno)d] %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%I:%M:%S"
LOG_LEVEL = logging.INFO
```

## Global Variables

### Download Configuration
```python
# Content selection
dl_assets = False          # Download supplementary assets
dl_captions = False        # Download subtitles
dl_quizzes = False         # Download quizzes
skip_lectures = False      # Skip video downloads

# Language and format
caption_locale = "en"      # Subtitle language
keep_vtt = False           # Keep VTT files after SRT conversion

# Quality and performance
quality = None             # Video quality preference (None = best)
skip_hls = False           # Skip HLS stream processing
concurrent_downloads = 10   # Max concurrent segment downloads

# Video encoding
use_h265 = False           # Use H.265 encoding
h265_crf = 28              # H.265 CRF value (quality)
h265_preset = "medium"     # H.265 encoding preset
use_nvenc = False          # Use NVIDIA hardware encoding
```

### Authentication and Session
```python
bearer_token = None        # API bearer token
browser = None             # Browser for cookie extraction
cj = None                  # Cookie jar instance
portal_name = None         # Udemy portal (www, business, etc.)
```

### File Management
```python
course_name = None         # Course identifier
id_as_course_name = False  # Use course ID as folder name
use_continuous_lecture_numbers = False  # Sequential numbering
chapter_filter = None      # Chapter filter set
DOWNLOAD_DIR = "out_dir"   # Output directory
```

### Caching and Resume
```python
save_to_file = None        # Save course data to file
load_from_file = None      # Load course data from file
keys = {}                  # Decryption key dictionary
```

## Docker Configuration

### Docker Compose (docker-compose.yml)

#### Service Definition
```yaml
services:
  udemy-downloader:
    image: udemy-downloader:latest
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./output:/app/out_dir:rw
      - ./keyfile.json:/app/keyfile.json:ro
    env_file:
      - .env
    command: python main.py -c $COURSE_URL
```

#### Volume Mapping
```yaml
volumes:
  # Output directory (read-write)
  - ./output:/app/out_dir:rw
  
  # Configuration files (read-only)
  - ./keyfile.json:/app/keyfile.json:ro
  - ./cookies.txt:/app/cookies.txt:ro
  
  # Optional: Custom templates
  - ./custom-templates:/app/templates:ro
```

#### Environment Variables
```yaml
environment:
  - UDEMY_BEARER=your_bearer_token
  - COURSE_URL=https://www.udemy.com/course/example/
  - LOG_LEVEL=INFO
```

### Dockerfile Configuration

#### Base Image and Dependencies
```dockerfile
FROM python:3.12-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget aria2 unzip xz-utils jq \
    && rm -rf /var/lib/apt/lists/*

# Install FFmpeg (latest static build)
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    && tar xvf ffmpeg-release-amd64-static.tar.xz \
    && mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ \
    && mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/

# Install Shaka Packager (latest version)
RUN LATEST_TAG=$(curl -s https://api.github.com/repos/shaka-project/shaka-packager/releases/latest | jq -r .tag_name) && \
    wget https://github.com/shaka-project/shaka-packager/releases/download/$LATEST_TAG/packager-linux-x64 -O /usr/local/bin/shaka-packager && \
    chmod +x /usr/local/bin/shaka-packager
```

## Configuration Best Practices

### Security
1. **Never commit sensitive data**: Keep `.env` and `keyfile.json` out of version control
2. **Use environment variables**: For sensitive configuration in production
3. **Rotate tokens**: Regularly update bearer tokens
4. **Secure key storage**: Protect decryption keys appropriately

### Performance
1. **Adjust concurrent downloads**: Based on network capacity and server limits
2. **Use appropriate quality**: Balance quality vs download time/storage
3. **Enable caching**: Use `--save-to-file` for large courses
4. **Skip unnecessary content**: Use content selection flags

### Organization
1. **Consistent naming**: Use meaningful output directory names
2. **Chapter filtering**: Download specific sections as needed
3. **Continuous numbering**: For better file organization
4. **Log retention**: Keep logs for troubleshooting

### Maintenance
1. **Regular updates**: Keep external tools updated
2. **Monitor logs**: Check for errors and warnings
3. **Backup configurations**: Save working configurations
4. **Test changes**: Verify configuration changes before production use