# Udemy Downloader

A Python library and CLI tool for downloading Udemy courses.

## 🚀 New Library Structure

This project has been restructured into a proper Python library! You can now:

- **Use it as a library** in your own Python projects
- **Install it via pip** (when published)
- **Import specific components** you need
- **Extend functionality** more easily

## 📦 Installation

### From Source (Development)
```bash
git clone https://github.com/Puyodead1/udemy-downloader.git
cd udemy-downloader
pip install -e .
```

### From PyPI (when published)
```bash
pip install udemy-downloader
```

## 🖥️ Command Line Usage

### Using the CLI command
```bash
udemy-downloader -c "https://udemy.com/course/example" -b "your_bearer_token"
```

### Using Python module
```bash
python -m udemy_downloader -c "https://udemy.com/course/example" -b "your_bearer_token"
```

### Using the wrapper script
```bash
python main_new.py -c "https://udemy.com/course/example" -b "your_bearer_token"
```

### Common Options
```bash
# Download with specific quality
udemy-downloader -c "course_url" -b "token" -q 720

# Download captions and assets
udemy-downloader -c "course_url" -b "token" --download-captions --download-assets

# Use browser cookies instead of bearer token
udemy-downloader -c "course_url" --browser chrome

# Download specific chapters
udemy-downloader -c "course_url" -b "token" --chapter "1,3-5,7"

# Get course info only
udemy-downloader -c "course_url" -b "token" --info
```

## 📚 Library Usage

### Basic Example
```python
from udemy_downloader import UdemyDownloader

# Initialize with bearer token
downloader = UdemyDownloader(bearer_token="your_token_here")

# Download a course
downloader.download_course(
    "https://udemy.com/course/example",
    quality=720,
    download_captions=True,
    download_assets=True,
    caption_locale="en"
)
```

### Using Browser Cookies
```python
from udemy_downloader import UdemyDownloader

# Initialize with browser cookies
downloader = UdemyDownloader(browser="chrome")

# Get course information
course_info = downloader.get_course_info("https://udemy.com/course/example")
print(f"Course: {course_info['title']}")
print(f"Chapters: {course_info['total_chapters']}")
print(f"Lectures: {course_info['total_lectures']}")
```

### Advanced Usage
```python
from udemy_downloader import UdemyDownloader

downloader = UdemyDownloader(bearer_token="your_token")

# Download with custom options
downloader.download_course(
    "https://udemy.com/course/example",
    quality=1080,                    # Video quality
    concurrent_downloads=5,          # Parallel downloads
    download_captions=True,          # Download subtitles
    download_quizzes=True,           # Download quizzes
    download_assets=True,            # Download supplementary files
    caption_locale="all",            # All caption languages
    use_h265=True,                   # Use H.265 encoding
    skip_hls=False,                  # Don't skip HLS streams
    chapter_filter={1, 2, 3},        # Download specific chapters
)
```

### Save and Load Course Data
```python
from udemy_downloader import UdemyDownloader

downloader = UdemyDownloader(bearer_token="your_token")

# Get and save course data
course_data = downloader.get_course_info("https://udemy.com/course/example")
downloader.save_course_data(course_data, "my_course.json")

# Load course data later
loaded_data = downloader.load_course_data("my_course.json")
```

## 🏗️ Library Architecture

The library is organized into several modules:

- **`UdemyDownloader`**: Main class for downloading courses
- **`UdemyAuth`**: Handles authentication (bearer tokens, cookies)
- **`Session`**: Manages HTTP sessions and requests
- **`ContentExtractor`**: Extracts different types of content
- **`LectureProcessor`**: Processes lecture content
- **`QuizProcessor`**: Processes quiz content
- **`AssetProcessor`**: Processes supplementary assets

## 🔧 Configuration

### Environment Variables
```bash
export UDEMY_BEARER="your_bearer_token_here"
```

### Configuration Files
- **Keyfile**: `keyfile.json` - Contains decryption keys for DRM content
- **Cookies**: `cookies.txt` - Netscape format cookies file
- **Logs**: `logs/` - Application logs

## 📋 Requirements

### System Dependencies
- **aria2c**: For downloading files
- **ffmpeg**: For video processing
- **shaka-packager**: For DRM content

### Python Dependencies
All Python dependencies are automatically installed with the package.

## 🔄 Migration from Old Version

If you were using the old `main.py` script, see [MIGRATION.md](MIGRATION.md) for detailed migration instructions.

### Quick Migration
- **Old**: `python main.py -c "url" -b "token"`
- **New**: `python main_new.py -c "url" -b "token"` (backward compatible)
- **Better**: `udemy-downloader -c "url" -b "token"` (new CLI)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Make sure you have the right to download the content and comply with Udemy's Terms of Service.

## 🙏 Acknowledgments

- Original project by Puyodead1
- Contributors and community members
- Open source libraries used in this project