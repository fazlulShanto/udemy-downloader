# Project Overview

## What is Udemy Downloader?

Udemy Downloader is a Python-based tool designed to download Udemy courses, including those with DRM (Digital Rights Management) protection. It provides comprehensive support for downloading various course materials including videos, articles, quizzes, coding assignments, and supplementary assets.

## Key Capabilities

### Content Types Supported
- **Video Lectures**: Both encrypted (DRM) and non-encrypted videos
- **Articles**: HTML-based lecture content
- **Quizzes**: Interactive quiz content with multiple choice questions
- **Coding Assignments**: Programming exercises with test cases and solutions
- **Supplementary Assets**: PDFs, source code, presentations, audio files, e-books
- **External Links**: References to external resources
- **Subtitles/Captions**: Multi-language subtitle support with VTT to SRT conversion

### Video Processing Features
- **Quality Selection**: Download specific video quality or best available
- **DRM Decryption**: Support for Widevine DRM-protected content
- **Format Support**: HLS (HTTP Live Streaming) and DASH (Dynamic Adaptive Streaming)
- **Video Encoding**: Optional H.265 encoding with hardware acceleration (NVENC)
- **Concurrent Downloads**: Multi-threaded segment downloading for faster speeds

### Organization Features
- **Chapter-based Structure**: Maintains course organization with chapters and lectures
- **Continuous Numbering**: Option for sequential lecture numbering across chapters
- **Chapter Filtering**: Download specific chapters only
- **Filename Sanitization**: Safe filename generation with emoji removal
- **Path Length Management**: Course ID as folder name option for long paths

## Technical Architecture

### Core Components
1. **Main Application** (`main.py`): Orchestrates the entire download process
2. **Udemy API Client** (`Udemy` class): Handles authentication and API interactions
3. **Session Management** (`Session`, `UdemyAuth`): Manages HTTP sessions and authentication
4. **Content Parsers**: Extract and process different content types
5. **Download Managers**: Handle file downloads with resume capability
6. **Template Engine**: Renders HTML content for articles and quizzes

### External Dependencies
- **ffmpeg**: Video processing and muxing
- **aria2c**: High-speed file downloading
- **shaka-packager**: DASH stream processing
- **yt-dlp**: Stream extraction and downloading

### Security & DRM
- **Widevine Support**: Handles Widevine DRM decryption
- **Key Management**: Secure storage and retrieval of decryption keys
- **PSSH Parsing**: Extracts protection system specific headers
- **MP4 Box Parsing**: Analyzes MP4 container structure for DRM metadata

## Workflow Overview

1. **Authentication**: Authenticate with Udemy using bearer token or browser cookies
2. **Course Discovery**: Fetch course information and curriculum structure
3. **Content Analysis**: Parse lectures, chapters, and associated media
4. **Download Planning**: Determine what content to download based on user preferences
5. **Asset Retrieval**: Download videos, assets, and supplementary materials
6. **Post-Processing**: Convert subtitles, encode videos, organize files
7. **Cleanup**: Remove temporary files and organize final output

## Use Cases

### Educational Content Archival
- Backup purchased courses for offline access
- Create local course libraries
- Preserve course content for future reference

### Content Analysis
- Extract course structure and metadata
- Analyze course content without downloading
- Generate course information reports

### Accessibility Enhancement
- Download subtitles for improved accessibility
- Convert VTT captions to SRT format
- Extract audio-only versions of lectures

## Legal and Ethical Considerations

⚠️ **Important Notice**: This tool is designed for educational and archival purposes only. Users must:

- Only download courses they have legitimately purchased or have access to
- Respect Udemy's Terms of Service
- Not redistribute downloaded content
- Use decryption keys obtained through legal means only

The developers are not responsible for any misuse of this tool or violations of terms of service.

## System Requirements

### Minimum Requirements
- Python 3.7+
- 2GB RAM
- 10GB free disk space (varies by course size)
- Internet connection for downloading

### Recommended Requirements
- Python 3.9+
- 8GB RAM
- SSD storage for better performance
- High-speed internet connection
- NVIDIA GPU (for hardware-accelerated encoding)

### Supported Platforms
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+, CentOS 7+, etc.)
- Docker containers