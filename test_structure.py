#!/usr/bin/env python3
"""
Simple test to verify the new library structure works.
"""

def test_imports():
    """Test that all main imports work."""
    try:
        from udemy_downloader import UdemyDownloader, UdemyAuth, Session
        print("✓ Main imports successful")
        
        from udemy_downloader.config import DOWNLOAD_DIR, DEFAULT_CONCURRENT_DOWNLOADS
        print("✓ Config imports successful")
        
        from udemy_downloader.constants import URLS, HEADERS
        print("✓ Constants imports successful")
        
        from udemy_downloader.utils import extract_kid, download_aria
        print("✓ Utils imports successful")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_class_initialization():
    """Test that classes can be initialized."""
    try:
        from udemy_downloader import UdemyAuth, Session
        
        # Test Session
        session = Session()
        print("✓ Session initialization successful")
        
        # Test UdemyAuth
        auth = UdemyAuth()
        print("✓ UdemyAuth initialization successful")
        
        # Test UdemyDownloader (this will fail without proper auth, but should import)
        from udemy_downloader import UdemyDownloader
        print("✓ UdemyDownloader import successful")
        
        return True
    except Exception as e:
        print(f"✗ Class initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing new library structure...")
    print()
    
    success = True
    success &= test_imports()
    success &= test_class_initialization()
    
    print()
    if success:
        print("🎉 All tests passed! The library structure is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)