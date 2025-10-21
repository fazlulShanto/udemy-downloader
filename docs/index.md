# Udemy Downloader Documentation

A comprehensive tool for downloading Udemy courses with DRM support. This documentation provides detailed information about all components, functions, and usage patterns.

## Table of Contents

- [Project Overview](overview.md)
- [Installation & Setup](installation.md)
- [Core Components](core-components.md)
- [Main Application](main-application.md)
- [Utility Functions](utilities.md)
- [Template System](templates.md)
- [Configuration](configuration.md)
- [Docker Deployment](docker.md)
- [API Reference](api-reference.md)
- [Troubleshooting](troubleshooting.md)

## Quick Start

1. **Prerequisites**: Ensure you have Python 3.x, ffmpeg, aria2c, and shaka-packager installed
2. **Setup**: Copy `.env.sample` to `.env` and `keyfile.example.json` to `keyfile.json`
3. **Configure**: Add your bearer token and decryption keys
4. **Run**: `python main.py -c <course_url> -b <bearer_token>`

## Key Features

- **DRM Support**: Downloads encrypted courses with proper decryption keys
- **Multiple Formats**: Supports video, audio, articles, quizzes, and supplementary materials
- **Quality Selection**: Choose specific video quality or download best available
- **Subtitle Support**: Download captions in multiple languages with VTT to SRT conversion
- **Resume Downloads**: Continue interrupted downloads
- **Chapter Filtering**: Download specific chapters only
- **H.265 Encoding**: Optional video re-encoding with hardware acceleration support

## Architecture

The application follows a modular architecture:

- **Main Application** (`main.py`): Entry point and orchestration
- **Core Classes**: `Udemy`, `Session`, `UdemyAuth` for API interaction
- **Utilities**: Helper functions for parsing, conversion, and file operations
- **Templates**: HTML templates for rendering articles, quizzes, and coding assignments
- **Configuration**: Constants, URLs, and environment settings

For detailed information about each component, see the respective documentation sections.