"""
Blogger RSS Feed Parser
Extracts all post URLs from a Blogger RSS/Atom feed
"""

import feedparser
import logging
from typing import List
from urllib.parse import urlparse
from datetime import datetime

class BloggerFeedParser:
    def __init__(self, feed_url: str):
        self.feed_url = feed_url
        self.logger = logging.getLogger(__name__)
        
    def get_all_post_urls(self, max_results: int = 500) -> List[str]:
        urls = []
        try:
            feed = feedparser.parse(self.feed_url)
            
            if feed.bozo:
                self.logger.error(f"Error parsing feed: {feed.bozo_exception}")
                return urls
                
            for entry in feed.entries:
                # 1. Check primary link
                if hasattr(entry, 'link'):
                    url = entry.link
                    if self._is_valid_post_url(url):
                        urls.append(url)
                        
                # 2. Check alternate links
                if hasattr(entry, 'links'):
                    for link in entry.links:
                        if link.get('rel') == 'alternate' and link.get('type') == 'text/html':
                            url = link.get('href')
                            if url and self._is_valid_post_url(url):
                                urls.append(url)
                                
            urls = list(dict.fromkeys(urls))
            self.logger.info(f"Found {len(urls)} valid post URLs")
            return urls[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error fetching feed: {str(e)}")
            return urls
            
    def _is_valid_post_url(self, url: str) -> bool:
        if not url:
            return False
        parsed = urlparse(url)
        if parsed.path.endswith('.html'):
            excluded_paths = ['/p/', '/search', '/feeds/', '?m=1', '?m=0']
            for excluded in excluded_paths:
                if excluded in parsed.path or excluded in url:
                    return False
            return True
        return False
