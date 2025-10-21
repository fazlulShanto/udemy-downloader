"""
Session management for Udemy API requests.
"""

import time
import logging
import requests
from typing import Optional, Dict, Any

from .tls import SSLCiphers
from .constants import HEADERS, URLS

logger = logging.getLogger(__name__)


class Session:
    """Handles HTTP session management for Udemy API requests."""
    
    def __init__(self):
        self._session = requests.sessions.Session()
        self._session.headers.update(HEADERS)
        self._session.mount(
            "https://",
            SSLCiphers(
                cipher_list="ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:AES256-SH"
            ),
        )

    def visit(self, portal_name: str) -> bool:
        """
        Makes a visit request to get the cloudflare bot cookies.
        
        Args:
            portal_name: The portal name for the Udemy instance
            
        Returns:
            bool: True if visit was successful, False otherwise
        """
        try:
            r = self._session.get(URLS.VISIT.format(portal_name=portal_name))
            if r.ok:
                logger.info("Visit request successful")
                return True
            logger.error(f"Visit request failed: {r.status_code} {r.reason}")
            return False
        except Exception as e:
            logger.error(f"Visit request failed with exception: {e}")
            return False

    def _get(self, url: str, params: Optional[Dict[str, Any]] = None, cookies=None):
        """
        Performs GET request with retry logic.
        
        Args:
            url: The URL to request
            params: Optional query parameters
            cookies: Optional cookies to include
            
        Returns:
            requests.Response: The response object
        """
        for i in range(10):
            try:
                req = self._session.get(url, cookies=cookies, params=params)
                if req.ok or req.status_code in [502, 503]:
                    return req
                if not req.ok:
                    logger.error(f"Failed request {url}")
                    logger.error(f"{req.status_code} {req.reason}, retrying (attempt {i})...")
                    time.sleep(0.8)
            except Exception as e:
                logger.error(f"Request failed with exception: {e}, retrying (attempt {i})...")
                time.sleep(0.8)
        
        raise Exception(f"Failed to complete request after 10 attempts: {url}")

    def _post(self, url: str, data: Dict[str, Any], redirect: bool = True, cookies=None):
        """
        Performs POST request.
        
        Args:
            url: The URL to post to
            data: The data to post
            redirect: Whether to allow redirects
            cookies: Optional cookies to include
            
        Returns:
            requests.Response: The response object
        """
        req = self._session.post(url, data, allow_redirects=redirect, cookies=cookies)
        if req.ok:
            return req
        if not req.ok:
            raise Exception(f"{req.status_code} {req.reason}")