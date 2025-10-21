"""
Authentication handling for Udemy.
"""

import logging
from typing import Optional
from .session import Session

logger = logging.getLogger(__name__)


class UdemyAuth:
    """Handles authentication for Udemy."""
    
    def __init__(self, username: str = "", password: str = "", cache_session: bool = False):
        """
        Initialize UdemyAuth.
        
        Args:
            username: Udemy username (currently unused)
            password: Udemy password (currently unused)
            cache_session: Whether to cache the session
        """
        self.username = username
        self.password = password
        self._cache = cache_session
        self._session = Session()

    def set_bearer_token(self, bearer_token: str) -> None:
        """
        Set the bearer token for authentication.
        
        Args:
            bearer_token: The bearer token to use for authentication
        """
        if bearer_token:
            self._session._session.headers.update({
                "x-udemyandroid-skip-local-cache": "true",
                "cache-control": "no-cache",
                "x-udemy-bearer-token": bearer_token,
                "authorization": f"Bearer {bearer_token}",
            })
            logger.info("Bearer token set successfully")
        else:
            logger.warning("Empty bearer token provided")

    def set_cookies(self, cookies) -> None:
        """
        Set cookies for the session.
        
        Args:
            cookies: Cookie jar to use for requests
        """
        # Cookies are handled at the request level in the session
        pass