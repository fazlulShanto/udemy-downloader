# Installation & Setup

## Prerequisites

Before installing Udemy Downloader, ensure you have the following tools installed on your system:

### Required External Tools

#### 1. Python 3.7+
```bash
# Check Python version
python --version
# or
python3 --version
```

#### 2. FFmpeg
FFmpeg is required for video processing and muxing.

**Windows:**
- Download from [FFmpeg official website](https://ffmpeg.org/download.html)
- Add to system PATH
- Recommended: Use builds from [yt-dlp team](https://github.com/yt-dlp/FFmpeg-Builds/releases/tag/latest)

**macOS:**
```bash
# Using Homebrew
brew install ffmpeg
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

#### 3. aria2c
High-speed download utility for concurrent downloads.

**Windows:**
- Download from [aria2 releases](https://github.com/aria2/aria2/releases)
- Add to system PATH

**macOS:**
```bash
brew install aria2
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install aria2

# CentOS/RHEL
sudo yum install aria2

# Arch Linux
sudo pacman -S aria2
```

#### 4. Shaka Packager
Required for DASH stream processing.

**All Platforms:**
- Download from [Shaka Packager releases](https://github.com/shaka-project/shaka-packager/releases/latest)
- Rename executable to `shaka-packager` (or `shaka-packager.exe` on Windows)
- Add to system PATH

## Installation Methods

### Method 1: Direct Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Puyodead1/udemy-downloader.git
cd udemy-downloader
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify installation:**
```bash
python main.py --help
```

### Method 2: Docker Installation

1. **Build Docker image:**
```bash
docker build -t udemy-downloader .
```

2. **Run with Docker Compose:**
```bash
# Copy and configure environment files first
cp .env.sample .env
cp keyfile.example.json keyfile.json
# Edit .env and keyfile.json with your credentials
docker-compose up
```

## Configuration Setup

### 1. Environment Configuration

Copy the sample environment file:
```bash
cp .env.sample .env
```

Edit `.env` file:
```bash
# Your Udemy bearer token
UDEMY_BEARER=your_bearer_token_here

# For docker compose only
COURSE_URL=https://www.udemy.com/course/your-course-name/
```

### 2. Decryption Keys Setup

Copy the sample keyfile:
```bash
cp keyfile.example.json keyfile.json
```

Edit `keyfile.json` with your decryption keys:
```json
{
    "key_id_1": "decryption_key_1",
    "key_id_2": "decryption_key_2"
}
```

**Note:** You must obtain decryption keys through legal means. The tool will not work with encrypted courses without proper keys.

### 3. Directory Structure

The application will create the following directories:
```
udemy-downloader/
├── out_dir/          # Downloaded courses (default output)
├── saved/            # Cached course data
├── logs/             # Application logs
├── temp/             # Temporary files during processing
└── cookies.txt       # Browser cookies (if using cookie authentication)
```

## Authentication Setup

### Method 1: Bearer Token (Recommended)

1. **Extract Bearer Token from Browser:**
   - Open Udemy in your browser
   - Open Developer Tools (F12)
   - Go to Network tab
   - Navigate to any course page
   - Look for API requests to `udemy.com`
   - Find the `Authorization` header with `Bearer` token

2. **Add to environment:**
```bash
# In .env file
UDEMY_BEARER=your_extracted_bearer_token
```

### Method 2: Browser Cookies

The tool can extract cookies directly from your browser:

**Supported browsers:**
- Chrome
- Firefox
- Opera
- Edge
- Brave
- Chromium
- Vivaldi
- Safari

**Usage:**
```bash
python main.py -c <course_url> --browser chrome
```

### Method 3: Cookie File

For manual cookie management:
1. Export cookies from browser to `cookies.txt` (Netscape format)
2. Use with `--browser file` option

## Verification

### Test Installation
```bash
# Check all dependencies
python main.py --help

# Test with course info only (no download)
python main.py -c <course_url> -b <bearer_token> --info
```

### Verify External Tools
```bash
# Check FFmpeg
ffmpeg -version

# Check aria2c
aria2c --version

# Check Shaka Packager
shaka-packager --version
```

## Common Installation Issues

### Python Dependencies
```bash
# If pip install fails, try:
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

# For Python 3.x specifically:
python3 -m pip install -r requirements.txt
```

### PATH Issues
Ensure all external tools are in your system PATH:
```bash
# Test each tool
which ffmpeg
which aria2c
which shaka-packager
```

### Permission Issues (Linux/macOS)
```bash
# Make scripts executable
chmod +x main.py

# Install with user permissions
pip install --user -r requirements.txt
```

### Windows-Specific Issues
- Use Command Prompt or PowerShell as Administrator
- Ensure Python is added to PATH during installation
- Use forward slashes or escaped backslashes in paths

## Docker-Specific Setup

### Environment Variables
```yaml
# docker-compose.yml
services:
  udemy-downloader:
    environment:
      - UDEMY_BEARER=your_token_here
      - COURSE_URL=your_course_url_here
```

### Volume Mapping
```yaml
volumes:
  - ./output:/app/out_dir:rw      # Output directory
  - ./keyfile.json:/app/keyfile.json:ro  # Decryption keys
  - ./cookies.txt:/app/cookies.txt:ro    # Optional cookies
```

### Custom Commands
```bash
# Run specific command in container
docker run -it udemy-downloader python main.py -c <url> --info

# Interactive shell
docker run -it udemy-downloader /bin/bash
```

## Next Steps

After successful installation:
1. Review [Configuration](configuration.md) for detailed settings
2. Check [Main Application](main-application.md) for usage examples
3. See [Troubleshooting](troubleshooting.md) for common issues