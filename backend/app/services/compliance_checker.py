"""Compliance and ethics checker for web discovery operations"""
import asyncio
from typing import Optional, Dict, List
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import httpx
from datetime import datetime, timedelta


class ComplianceChecker:
    """Ensures all discovery operations are legal and ethical"""
    
    # Required minimum delay between requests (seconds)
    MIN_REQUEST_DELAY = 2.0
    
    # User agent for all requests (transparent identity)
    USER_AGENT = "WebIntelligencePlatform/1.0 (Research; +https://github.com/FraudShield1/web-intelligence-platform)"
    
    # Cache for robots.txt parsers
    _robots_cache: Dict[str, tuple[RobotFileParser, datetime]] = {}
    _cache_ttl = timedelta(hours=1)
    
    def __init__(self):
        self.last_request_time: Dict[str, datetime] = {}
    
    async def check_robots_txt(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Check if URL is allowed by robots.txt
        
        Returns:
            (is_allowed, reason_if_blocked)
        """
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = urljoin(base_url, "/robots.txt")
        
        # Check cache
        if base_url in self._robots_cache:
            parser, cached_at = self._robots_cache[base_url]
            if datetime.utcnow() - cached_at < self._cache_ttl:
                if parser.can_fetch(self.USER_AGENT, url):
                    return True, None
                else:
                    return False, f"Disallowed by robots.txt for {self.USER_AGENT}"
        
        # Fetch robots.txt
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    robots_url,
                    headers={"User-Agent": self.USER_AGENT},
                    follow_redirects=True
                )
                
                parser = RobotFileParser()
                parser.parse(response.text.splitlines())
                
                # Cache the parser
                self._robots_cache[base_url] = (parser, datetime.utcnow())
                
                if parser.can_fetch(self.USER_AGENT, url):
                    return True, None
                else:
                    return False, f"Disallowed by robots.txt for {self.USER_AGENT}"
                    
        except Exception as e:
            # If robots.txt is unreachable, assume allowed (standard practice)
            # but log the error
            return True, None
    
    async def enforce_rate_limit(self, domain: str) -> None:
        """
        Enforce minimum delay between requests to same domain
        Implements polite crawling
        """
        parsed = urlparse(domain)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if base_domain in self.last_request_time:
            elapsed = (datetime.utcnow() - self.last_request_time[base_domain]).total_seconds()
            if elapsed < self.MIN_REQUEST_DELAY:
                wait_time = self.MIN_REQUEST_DELAY - elapsed
                await asyncio.sleep(wait_time)
        
        self.last_request_time[base_domain] = datetime.utcnow()
    
    def get_headers(self) -> Dict[str, str]:
        """Get standard headers with transparent identification"""
        return {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",  # Do Not Track
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def is_public_content(self, url: str, html: str) -> tuple[bool, Optional[str]]:
        """
        Check if content is publicly accessible (not behind login/paywall)
        
        Returns:
            (is_public, reason_if_private)
        """
        # Check for common login indicators
        login_indicators = [
            "login", "signin", "sign-in", "sign_in",
            "authentication", "password", "username",
            "member-only", "subscription", "paywall"
        ]
        
        url_lower = url.lower()
        html_lower = html.lower()
        
        # Check URL
        for indicator in login_indicators:
            if indicator in url_lower:
                return False, f"URL suggests private content: {indicator}"
        
        # Check for meta tags indicating private content
        if 'name="robots" content="noindex"' in html_lower:
            return False, "Page marked with noindex"
        
        # Check for common paywall/login forms
        paywall_patterns = [
            'class="paywall"',
            'id="paywall"',
            'data-paywall',
            'type="password"',
            'class="login-form"',
            'id="login-form"'
        ]
        
        for pattern in paywall_patterns:
            if pattern in html_lower:
                return False, f"Private content detected: {pattern}"
        
        return True, None
    
    def should_crawl_url(self, url: str, base_domain: str) -> tuple[bool, Optional[str]]:
        """
        Check if URL should be crawled based on various criteria
        
        Returns:
            (should_crawl, reason_if_not)
        """
        parsed = urlparse(url)
        base_parsed = urlparse(base_domain)
        
        # Must be same domain (no external links)
        if parsed.netloc != base_parsed.netloc:
            return False, "External domain"
        
        # Skip common non-content URLs
        skip_patterns = [
            '/login', '/signin', '/sign-in', '/register', '/signup',
            '/logout', '/account', '/profile', '/settings',
            '/cart', '/checkout', '/payment', '/order',
            '/wp-admin', '/admin', '/dashboard',
            '/api/auth', '/oauth', '/sso',
            '.pdf', '.zip', '.exe', '.dmg',
            '/download', '/file'
        ]
        
        path_lower = parsed.path.lower()
        for pattern in skip_patterns:
            if pattern in path_lower:
                return False, f"Excluded pattern: {pattern}"
        
        # Skip query parameters that suggest session/tracking
        if parsed.query:
            session_params = ['session', 'token', 'auth', 'key', 'sid']
            query_lower = parsed.query.lower()
            for param in session_params:
                if param in query_lower:
                    return False, f"Session parameter detected: {param}"
        
        return True, None
    
    async def validate_request(
        self,
        url: str,
        base_domain: str,
        html: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Complete validation check for a request
        
        Returns:
            (is_valid, reason_if_invalid)
        """
        # Check robots.txt
        robots_ok, robots_reason = await self.check_robots_txt(url)
        if not robots_ok:
            return False, f"Compliance: {robots_reason}"
        
        # Check if URL should be crawled
        should_crawl, crawl_reason = self.should_crawl_url(url, base_domain)
        if not should_crawl:
            return False, f"Policy: {crawl_reason}"
        
        # If HTML provided, check for public content
        if html:
            is_public, public_reason = self.is_public_content(url, html)
            if not is_public:
                return False, f"Privacy: {public_reason}"
        
        # Enforce rate limit
        await self.enforce_rate_limit(url)
        
        return True, None
    
    def log_compliance_decision(
        self,
        url: str,
        allowed: bool,
        reason: Optional[str] = None
    ) -> None:
        """Log compliance decisions for audit trail"""
        timestamp = datetime.utcnow().isoformat()
        status = "ALLOWED" if allowed else "BLOCKED"
        
        log_entry = f"[{timestamp}] {status}: {url}"
        if reason:
            log_entry += f" - {reason}"
        
        # In production, this would go to a proper logging system
        print(log_entry)


# Global instance
compliance_checker = ComplianceChecker()

