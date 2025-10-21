# Troubleshooting

This document provides solutions for common issues, error messages, and debugging techniques for the Udemy Downloader.

## Common Issues

### Authentication Problems

#### Bearer Token Issues

**Problem**: "No bearer token was provided" or authentication failures
```
ERROR: No bearer token was provided, and no browser for cookie extraction was specified.
```

**Solutions**:
1. **Extract Bearer Token from Browser**:
   - Open Udemy in browser and log in
   - Open Developer Tools (F12)
   - Go to Network tab
   - Navigate to any course page
   - Look for API requests to `udemy.com`
   - Find `Authorization` header with `Bearer` token
   - Copy token (without "Bearer " prefix)

2. **Set Bearer Token**:
   ```bash
   # Command line
   python main.py -c <url> -b "your_bearer_token_here"
   
   # Environment file
   echo "UDEMY_BEARER=your_bearer_token_here" > .env
   ```

3. **Use Browser Cookies**:
   ```bash
   python main.py -c <url> --browser chrome
   ```

**Problem**: "Failed to find the course, are you enrolled?"
```
FATAL: Failed to find the course, are you enrolled?
```

**Solutions**:
1. **Verify Enrollment**: Ensure you're enrolled in the course
2. **Check URL**: Verify the course URL is correct
3. **Try Subscription Flag**: For subscription courses:
   ```bash
   python main.py -c <url> -sc
   ```
4. **Check Portal**: Ensure using correct portal (www vs business)

#### Cookie Authentication Issues

**Problem**: Browser cookie extraction fails
```
WARNING: No bearer token was provided, attempting to use browser cookies.
```

**Solutions**:
1. **Close Browser**: Ensure target browser is completely closed
2. **Check Browser Support**: Use supported browsers:
   - Chrome, Firefox, Opera, Edge, Brave, Chromium, Vivaldi, Safari
3. **Manual Cookie File**:
   ```bash
   # Export cookies to cookies.txt (Netscape format)
   python main.py -c <url> --browser file
   ```

### External Tool Issues

#### Missing Dependencies

**Problem**: "aria2c is missing from your system or path!"
```
FATAL: Aria2c is missing from your system or path!
```

**Solutions**:
1. **Install aria2c**:
   ```bash
   # Windows: Download from GitHub releases
   # macOS
   brew install aria2
   # Linux
   sudo apt install aria2  # Ubuntu/Debian
   sudo yum install aria2  # CentOS/RHEL
   ```

2. **Verify Installation**:
   ```bash
   aria2c --version
   which aria2c  # Linux/macOS
   where aria2c  # Windows
   ```

**Problem**: "FFMPEG is missing from your system or path!"
```
FATAL: FFMPEG is missing from your system or path!
```

**Solutions**:
1. **Install FFmpeg**:
   ```bash
   # Windows: Download from ffmpeg.org
   # macOS
   brew install ffmpeg
   # Linux
   sudo apt install ffmpeg  # Ubuntu/Debian
   ```

2. **Use yt-dlp Builds** (Recommended):
   - Download from [yt-dlp FFmpeg builds](https://github.com/yt-dlp/FFmpeg-Builds/releases)
   - Add to system PATH

**Problem**: "Shaka Packager is missing from your system or path!"
```
FATAL: Shaka Packager is missing from your system or path!
```

**Solutions**:
1. **Download Shaka Packager**:
   - Get latest from [GitHub releases](https://github.com/shaka-project/shaka-packager/releases)
   - Rename to `shaka-packager` (or `shaka-packager.exe` on Windows)
   - Add to system PATH

2. **Verify Installation**:
   ```bash
   shaka-packager --version
   ```

### DRM and Decryption Issues

#### Missing Decryption Keys

**Problem**: "Keyfile not found! You won't be able to decrypt any encrypted videos!"
```
WARNING: Keyfile not found! You won't be able to decrypt any encrypted videos!
```

**Solutions**:
1. **Create Keyfile**:
   ```bash
   cp keyfile.example.json keyfile.json
   ```

2. **Add Keys**: Edit `keyfile.json` with your decryption keys:
   ```json
   {
       "key_id_here": "decryption_key_here"
   }
   ```

**Problem**: "Audio key not found" or "Video key not found"
```
ERROR: Audio key not found for abc123..., if you have the key then you probably didn't add them to the key file correctly.
```

**Solutions**:
1. **Check Key Format**: Ensure keys are lowercase hexadecimal
2. **Verify Key ID**: Match the KID from error message
3. **Update Keyfile**: Add missing keys to `keyfile.json`

#### Key Extraction Issues

**Problem**: "Error extracting video kid" or "Error extracting audio kid"
```
ERROR: Error extracting video kid
```

**Solutions**:
1. **Check File Integrity**: Verify downloaded segments aren't corrupted
2. **Retry Download**: Delete partial files and retry
3. **Check Disk Space**: Ensure sufficient storage available

### Download Issues

#### Network Problems

**Problem**: Connection timeouts or network errors
```
FATAL: Connection error: HTTPSConnectionPool(host='www.udemy.com', port=443)
```

**Solutions**:
1. **Check Internet Connection**: Verify network connectivity
2. **Retry**: Network issues are often temporary
3. **Reduce Concurrent Downloads**:
   ```bash
   python main.py -c <url> --concurrent-downloads 5
   ```
4. **Use VPN**: If region-blocked

#### Download Failures

**Problem**: "Return code from the downloader was non-0 (error)"
```
WARNING: Return code from the downloader was non-0 (error), skipping!
```

**Solutions**:
1. **Check Disk Space**: Ensure sufficient storage
2. **Verify Permissions**: Check write permissions to output directory
3. **Retry**: Temporary server issues
4. **Check URL Validity**: Ensure course URLs are still valid

#### Segment Download Issues

**Problem**: yt-dlp or aria2c failures during segment downloads
```
ERROR: Failed to download segments
```

**Solutions**:
1. **Update yt-dlp**:
   ```bash
   pip install --upgrade yt-dlp
   ```
2. **Reduce Concurrent Downloads**:
   ```bash
   python main.py -c <url> -cd 5
   ```
3. **Check Temporary Directory**: Ensure temp directory has space and permissions

### File System Issues

#### Path Length Problems (Windows)

**Problem**: "The filename or extension is too long" on Windows
```
OSError: [Errno 36] File name too long
```

**Solutions**:
1. **Use Course ID as Name**:
   ```bash
   python main.py -c <url> --id-as-course-name
   ```
2. **Shorter Output Path**:
   ```bash
   python main.py -c <url> -o C:\udemy
   ```
3. **Enable Long Paths** (Windows 10+):
   - Group Policy: Computer Configuration > Administrative Templates > System > Filesystem > Enable Win32 long paths

#### Permission Issues

**Problem**: "Permission denied" errors
```
PermissionError: [Errno 13] Permission denied: 'output_file.mp4'
```

**Solutions**:
1. **Check Directory Permissions**:
   ```bash
   # Linux/macOS
   chmod 755 out_dir/
   chown -R $USER:$USER out_dir/
   
   # Windows: Run as Administrator or check folder permissions
   ```

2. **Close File Handles**: Ensure no programs have files open
3. **Antivirus**: Check if antivirus is blocking file operations

### Video Processing Issues

#### FFmpeg Errors

**Problem**: "Muxing returned a non-zero exit code"
```
ERROR: Return code from ffmpeg was non-0 (error), skipping!
```

**Solutions**:
1. **Check FFmpeg Version**: Ensure recent version installed
2. **Verify Input Files**: Check if video/audio files are valid
3. **Disk Space**: Ensure sufficient space for output
4. **Debug FFmpeg**:
   ```bash
   python main.py -c <url> --log-level DEBUG
   ```

#### H.265 Encoding Issues

**Problem**: H.265 encoding fails or produces errors
```
ERROR: Encoding returned non-zero return code
```

**Solutions**:
1. **Check Hardware Support**: Verify GPU supports NVENC (if using `--use-nvenc`)
2. **Adjust Settings**:
   ```bash
   # Lower CRF for better compatibility
   python main.py -c <url> --use-h265 --h265-crf 23
   
   # Faster preset
   python main.py -c <url> --use-h265 --h265-preset faster
   ```
3. **Disable H.265**: Remove `--use-h265` flag if issues persist

### Content Processing Issues

#### Quiz Processing Problems

**Problem**: Quiz HTML files not generating correctly
```
ERROR: Failed to process quiz
```

**Solutions**:
1. **Check Template Files**: Ensure templates exist in `templates/` directory
2. **Verify Quiz Data**: Some quizzes may have incomplete data
3. **Check Permissions**: Ensure write access to chapter directories

#### Subtitle Issues

**Problem**: "Error converting caption" or VTT conversion fails
```
ERROR: Error converting caption
```

**Solutions**:
1. **Check Dependencies**: Ensure `webvtt-py` and `pysrt` are installed
2. **Skip VTT Conversion**:
   ```bash
   python main.py -c <url> --download-captions --keep-vtt
   ```
3. **Manual Conversion**: Use external tools if needed

### Performance Issues

#### Slow Downloads

**Problem**: Downloads are slower than expected

**Solutions**:
1. **Increase Concurrent Downloads**:
   ```bash
   python main.py -c <url> --concurrent-downloads 20
   ```
2. **Skip HLS Processing**:
   ```bash
   python main.py -c <url> --skip-hls
   ```
3. **Check Network**: Verify internet speed and stability

#### High Memory Usage

**Problem**: Application uses excessive memory

**Solutions**:
1. **Reduce Concurrent Downloads**: Lower the `-cd` value
2. **Process Chapters Individually**:
   ```bash
   python main.py -c <url> --chapter "1"
   python main.py -c <url> --chapter "2"
   ```
3. **Monitor Resources**: Use system monitoring tools

## Debugging Techniques

### Enable Debug Logging

```bash
python main.py -c <url> --log-level DEBUG
```

**Debug Information Includes**:
- Detailed API requests and responses
- File operations and paths
- Subprocess command execution
- Error stack traces

### Check Log Files

Log files are automatically created in the `logs/` directory:
```bash
# View latest log
tail -f logs/$(ls -t logs/ | head -1)

# Search for errors
grep -i error logs/*.log
```

### Verify Configuration

```bash
# Check keyfile format
python -m json.tool keyfile.json

# Verify environment variables
cat .env

# Test external tools
aria2c --version
ffmpeg -version
shaka-packager --version
```

### Test Course Access

```bash
# Get course information only
python main.py -c <url> --info

# Test with minimal options
python main.py -c <url> --skip-lectures --log-level DEBUG
```

### Network Debugging

```bash
# Test connectivity
curl -I https://www.udemy.com

# Check DNS resolution
nslookup www.udemy.com

# Test with different DNS
# Windows: ipconfig /flushdns
# Linux/macOS: sudo dscacheutil -flushcache
```

## Error Message Reference

### Authentication Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "No bearer token was provided" | Missing authentication | Add bearer token or use browser cookies |
| "Failed to find the course" | Course not accessible | Check enrollment, URL, or use `-sc` flag |
| "Visit request failed" | Cloudflare blocking | Retry, use VPN, or check network |

### Dependency Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "aria2c is missing" | aria2c not installed | Install aria2c and add to PATH |
| "FFMPEG is missing" | FFmpeg not installed | Install FFmpeg and add to PATH |
| "Shaka Packager is missing" | Shaka Packager not installed | Download and install Shaka Packager |

### Download Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Connection error" | Network issues | Check internet, retry, reduce concurrency |
| "Return code non-0" | Download failure | Check disk space, permissions, retry |
| "File name too long" | Path length limit | Use `--id-as-course-name` or shorter paths |

### Processing Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Muxing returned non-zero" | FFmpeg failure | Check FFmpeg version, disk space, input files |
| "Key not found" | Missing decryption key | Add key to keyfile.json |
| "Error extracting kid" | Corrupted segments | Retry download, check disk space |

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Enable debug logging** and review logs
3. **Verify all dependencies** are installed correctly
4. **Test with minimal configuration** to isolate issues
5. **Check GitHub issues** for similar problems

### Information to Include

When reporting issues, include:

1. **Command used**: Full command line with arguments
2. **Error message**: Complete error output
3. **Log files**: Relevant portions of debug logs
4. **System information**: OS, Python version, dependency versions
5. **Course information**: Type of course (free/paid/subscription)

### Useful Commands for Diagnostics

```bash
# System information
python --version
pip list | grep -E "(requests|yt-dlp|aria2|ffmpeg)"

# Dependency check
aria2c --version
ffmpeg -version
shaka-packager --version

# Test minimal functionality
python main.py -c <url> --info --log-level DEBUG

# Check configuration
python -c "import json; print(json.load(open('keyfile.json')))"
```

### Community Resources

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/Puyodead1/udemy-downloader/issues)
- **Discord Server**: Join for community support
- **Documentation**: Review all documentation sections

### Professional Support

For commercial use or complex deployments:
- Consider professional support options
- Review enterprise deployment guides
- Implement proper monitoring and logging
- Follow security best practices