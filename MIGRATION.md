# Migration Guide

This document explains how to migrate from the old monolithic `main.py` to the new library structure.

## What Changed

The project has been restructured from a single `main.py` file into a proper Python library with the following structure:

```
udemy_downloader/
├── __init__.py          # Main library exports
├── __main__.py          # Module entry point
├── auth.py              # Authentication handling
├── cli.py               # Command-line interface
├── config.py            # Configuration and constants
├── constants.py         # API URLs and parameters
├── downloader.py        # Main downloader class
├── extractors.py        # Content extraction logic
├── processors.py        # Content processing logic
├── session.py           # HTTP session management
├── tls.py               # TLS/SSL configuration
├── utils.py             # Utility functions
├── vtt_to_srt.py        # Subtitle conversion
└── templates/           # HTML templates
    ├── article_template.html
    ├── coding_assignment_template.html
    └── quiz_template.html
```

## Command Line Usage

### Before (Old)
```bash
python main.py -c "https://udemy.com/course/example" -b "your_bearer_token"
```

### After (New)
```bash
# Using the new main.py wrapper
python main_new.py -c "https://udemy.com/course/example" -b "your_bearer_token"

# Or using the library directly
python -m udemy_downloader -c "https://udemy.com/course/example" -b "your_bearer_token"

# Or if installed as a package
udemy-downloader -c "https://udemy.com/course/example" -b "your_bearer_token"
```

## Library Usage

### Basic Example
```python
from udemy_downloader import UdemyDownloader

# Initialize with bearer token
downloader = UdemyDownloader(bearer_token="your_token")

# Download a course
downloader.download_course(
    "https://udemy.com/course/example",
    quality=720,
    download_captions=True,
    download_assets=True
)
```

### Using Browser Cookies
```python
from udemy_downloader import UdemyDownloader

# Initialize with browser cookies
downloader = UdemyDownloader(browser="chrome")

# Get course info only
course_info = downloader.get_course_info("https://udemy.com/course/example")
print(f"Course: {course_info['title']}")
```

## Installation

### Development Installation
```bash
# Clone the repository
git clone https://github.com/Puyodead1/udemy-downloader.git
cd udemy-downloader

# Install in development mode
pip install -e .
```

### Package Installation
```bash
pip install udemy-downloader
```

## Breaking Changes

1. **Import Changes**: If you were importing functions from the old `main.py`, you'll need to update imports:
   ```python
   # Old
   from main import Udemy, UdemyAuth
   
   # New
   from udemy_downloader import UdemyDownloader, UdemyAuth
   ```

2. **Class Names**: Some classes have been renamed for clarity:
   - `Udemy` → `UdemyDownloader`

3. **Configuration**: Global variables are now organized in `config.py` and can be imported:
   ```python
   from udemy_downloader.config import DOWNLOAD_DIR, DEFAULT_CONCURRENT_DOWNLOADS
   ```

## Benefits of the New Structure

1. **Modularity**: Code is organized into logical modules
2. **Reusability**: Can be used as a library in other projects
3. **Maintainability**: Easier to maintain and extend
4. **Testing**: Better structure for unit testing
5. **Distribution**: Can be installed via pip
6. **Documentation**: Better organized documentation

## Backward Compatibility

The `main_new.py` file provides backward compatibility with the original CLI interface. All command-line arguments work the same way.

## Dependencies

All dependencies are now properly managed in `pyproject.toml`. Install them with:

```bash
pip install -e .
```

For development dependencies:
```bash
pip install -e ".[dev]"
```