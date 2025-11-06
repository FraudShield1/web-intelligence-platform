"""Advanced site discovery service - Feature G implementation"""
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime
import re
from collections import defaultdict, Counter

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page

from app.services.compliance_checker import compliance_checker


class DiscoveryService:
    """
    Feature G: Advanced Web Discovery
    Ethical, compliant, powerful site intelligence
    """
    
    # Discovery limits (prevent infinite crawling)
    MAX_PAGES_PER_SITE = 50
    MAX_DEPTH = 3
    PAGE_TIMEOUT = 30000  # milliseconds
    
    def __init__(self):
        self.compliance = compliance_checker
        self.discovered_urls: Set[str] = set()
        self.url_patterns: Dict[str, List[str]] = defaultdict(list)
    
    async def discover_site(self, url: str) -> Dict:
        """
        Main entry point for site discovery
        
        Returns complete discovery report with:
        - Site structure
        - Category hierarchy
        - Product patterns
        - API endpoints
        - Selectors
        - Pagination logic
        """
        start_time = datetime.utcnow()
        
        try:
            # Phase 1: Structure Exploration
            print(f"🔍 Phase 1: Exploring {url}...")
            structure = await self._phase1_structure_exploration(url)
            
            if not structure.get("allowed"):
                return {
                    "success": False,
                    "error": structure.get("reason", "Not allowed to crawl"),
                    "url": url
                }
            
            # Phase 2: Category Hierarchy Detection
            print(f"📁 Phase 2: Detecting categories...")
            categories = await self._phase2_category_detection(
                url,
                structure.get("links", [])
            )
            
            # Phase 3: Product Pattern Recognition
            print(f"🛍️ Phase 3: Recognizing product patterns...")
            products = await self._phase3_product_recognition(
                url,
                structure.get("links", []),
                categories
            )
            
            # Phase 4: Selector Extraction
            print(f"🎯 Phase 4: Extracting selectors...")
            selectors = await self._phase4_selector_extraction(
                url,
                products.get("sample_pages", [])
            )
            
            # Phase 5: API Endpoint Discovery
            print(f"🔌 Phase 5: Discovering API endpoints...")
            endpoints = await self._phase5_endpoint_discovery(url)
            
            # Phase 6: Pagination & Render Logic
            print(f"📄 Phase 6: Detecting pagination...")
            pagination = await self._phase6_pagination_detection(
                url,
                products.get("listing_pages", [])
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(
                structure, categories, products, selectors, endpoints, pagination
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": True,
                "url": url,
                "discovered_at": start_time.isoformat(),
                "duration_seconds": duration,
                "confidence_score": confidence,
                "structure": structure,
                "categories": categories,
                "products": products,
                "selectors": selectors,
                "endpoints": endpoints,
                "pagination": pagination,
                "render_hints": {
                    "requires_js": structure.get("requires_js", False),
                    "wait_for_selector": selectors.get("wait_for"),
                    "timeout_seconds": 30
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds()
            }
    
    async def _phase1_structure_exploration(self, url: str) -> Dict:
        """
        Phase 1: Ethical structure exploration
        
        - Check robots.txt compliance
        - Crawl homepage + linked pages (max depth 3)
        - Extract all internal links
        - Detect navigation patterns
        - Build site graph
        """
        # Check robots.txt first
        allowed, reason = await self.compliance.check_robots_txt(url)
        if not allowed:
            self.compliance.log_compliance_decision(url, False, reason)
            return {"allowed": False, "reason": reason}
        
        self.compliance.log_compliance_decision(url, True)
        
        # Fetch homepage
        links = []
        nav_links = []
        requires_js = False
        
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                headers=self.compliance.get_headers(),
                follow_redirects=True
            ) as client:
                # Enforce rate limit
                await self.compliance.enforce_rate_limit(url)
                
                response = await client.get(url)
                html = response.text
                
                # Check if public content
                is_public, public_reason = self.compliance.is_public_content(url, html)
                if not is_public:
                    return {
                        "allowed": False,
                        "reason": f"Private content: {public_reason}"
                    }
                
                # Parse HTML
                soup = BeautifulSoup(html, 'lxml')
                
                # Check if JS required
                body_text = soup.body.get_text(strip=True) if soup.body else ""
                if len(body_text) < 200 or soup.find(id="root") or soup.find(id="app"):
                    requires_js = True
                
                # Extract all links
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    absolute_url = urljoin(url, href)
                    
                    # Check if should crawl
                    should_crawl, crawl_reason = self.compliance.should_crawl_url(
                        absolute_url, url
                    )
                    
                    if should_crawl:
                        links.append({
                            "url": absolute_url,
                            "text": a_tag.get_text(strip=True)[:100],
                            "depth": 1
                        })
                        
                        # Check if in navigation
                        parent = a_tag.parent
                        if parent and parent.name in ['nav', 'header', 'menu']:
                            nav_links.append(absolute_url)
        
        except Exception as e:
            return {
                "allowed": False,
                "reason": f"Error fetching: {str(e)}"
            }
        
        # If JS required, use Playwright for deeper exploration
        if requires_js:
            playwright_links = await self._explore_with_playwright(url)
            links.extend(playwright_links)
        
        # Limit links
        links = links[:self.MAX_PAGES_PER_SITE]
        
        return {
            "allowed": True,
            "links": links,
            "nav_links": nav_links,
            "total_links": len(links),
            "requires_js": requires_js,
            "homepage_html": html if not requires_js else None
        }
    
    async def _explore_with_playwright(self, url: str) -> List[Dict]:
        """
        Use Playwright for JS-heavy sites
        Respects all compliance rules
        """
        links = []
        
        try:
            async with async_playwright() as p:
                # Launch browser (visible, not stealth - we're transparent)
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )
                
                # Create context with our user agent
                context = await browser.new_context(
                    user_agent=self.compliance.USER_AGENT,
                    viewport={"width": 1920, "height": 1080}
                )
                
                page = await context.new_page()
                
                # Enforce rate limit
                await self.compliance.enforce_rate_limit(url)
                
                # Navigate
                await page.goto(url, wait_until="networkidle", timeout=self.PAGE_TIMEOUT)
                
                # Wait for content
                await page.wait_for_timeout(2000)
                
                # Extract links
                link_elements = await page.query_selector_all('a[href]')
                
                for element in link_elements[:100]:  # Limit
                    try:
                        href = await element.get_attribute('href')
                        text = await element.inner_text()
                        
                        if href:
                            absolute_url = urljoin(url, href)
                            should_crawl, _ = self.compliance.should_crawl_url(
                                absolute_url, url
                            )
                            
                            if should_crawl:
                                links.append({
                                    "url": absolute_url,
                                    "text": text[:100] if text else "",
                                    "depth": 1,
                                    "from_js": True
                                })
                    except:
                        continue
                
                await browser.close()
                
        except Exception as e:
            print(f"Playwright error: {e}")
        
        return links
    
    async def _phase2_category_detection(
        self,
        base_url: str,
        links: List[Dict]
    ) -> Dict:
        """
        Phase 2: Category Hierarchy Detection
        
        - Cluster URLs by path similarity
        - Detect breadcrumbs
        - Build category tree
        - Calculate confidence
        """
        if not links:
            return {"categories": {}, "confidence": 0.0}
        
        # Extract paths
        paths = []
        for link in links:
            parsed = urlparse(link["url"])
            path = parsed.path.strip('/')
            if path:
                paths.append(path)
        
        # Cluster by path segments
        category_patterns = defaultdict(list)
        
        for path in paths:
            segments = path.split('/')
            if len(segments) >= 2:
                # Potential category pattern
                category = segments[0]
                subcategory = segments[1] if len(segments) > 1 else None
                
                # Common category indicators
                category_keywords = [
                    'category', 'cat', 'c', 'collection', 'collections',
                    'shop', 'products', 'items', 'browse'
                ]
                
                if any(kw in category.lower() for kw in category_keywords):
                    if subcategory:
                        category_patterns[category].append(subcategory)
        
        # Build hierarchy
        categories = {}
        for category, subcategories in category_patterns.items():
            # Count subcategory frequency
            counter = Counter(subcategories)
            # Only include subcategories that appear multiple times (likely real categories)
            categories[category] = [
                sub for sub, count in counter.items() if count >= 1
            ][:20]  # Limit to 20 subcategories
        
        # Calculate confidence
        confidence = min(len(categories) / 10.0, 1.0)  # More categories = higher confidence
        
        return {
            "categories": categories,
            "total_categories": len(categories),
            "confidence": round(confidence, 2)
        }
    
    async def _phase3_product_recognition(
        self,
        base_url: str,
        links: List[Dict],
        categories: Dict
    ) -> Dict:
        """
        Phase 3: Product Pattern Recognition
        
        - Identify listing pages
        - Detect product detail pages
        - Extract URL patterns
        - Sample pages for analysis
        """
        listing_pages = []
        product_pages = []
        sample_pages = []
        
        # Common product URL patterns
        product_patterns = [
            r'/product/',
            r'/item/',
            r'/p/',
            r'/pd/',
            r'/products/',
            r'/detail/',
            r'-p-\d+',
            r'/\d+\.html',
            r'/sku-'
        ]
        
        # Common listing patterns
        listing_patterns = [
            r'/category/',
            r'/collection/',
            r'/shop/',
            r'/products',
            r'/browse/',
            r'/search'
        ]
        
        for link in links:
            url = link["url"]
            path = urlparse(url).path.lower()
            
            # Check for product patterns
            if any(re.search(pattern, path) for pattern in product_patterns):
                product_pages.append(url)
                if len(sample_pages) < 5:
                    sample_pages.append(url)
            
            # Check for listing patterns
            elif any(re.search(pattern, path) for pattern in listing_patterns):
                listing_pages.append(url)
        
        return {
            "listing_pages": listing_pages[:20],
            "product_pages": product_pages[:50],
            "sample_pages": sample_pages,
            "product_url_pattern": self._infer_url_pattern(product_pages),
            "total_products_found": len(product_pages)
        }
    
    def _infer_url_pattern(self, urls: List[str]) -> Optional[str]:
        """Infer common URL pattern from list of URLs"""
        if not urls:
            return None
        
        # Find common path structure
        paths = [urlparse(url).path for url in urls[:10]]
        
        # Simple pattern detection
        if all('/product/' in p for p in paths):
            return "/product/:slug"
        elif all('/p/' in p for p in paths):
            return "/p/:id"
        elif all('/item/' in p for p in paths):
            return "/item/:id"
        
        return None
    
    async def _phase4_selector_extraction(
        self,
        base_url: str,
        sample_pages: List[str]
    ) -> Dict:
        """
        Phase 4: Selector Extraction
        
        - Analyze DOM structure of sample pages
        - Find repeating patterns
        - Generate CSS selectors
        - Validate selectors
        """
        if not sample_pages:
            return {"selectors": {}, "confidence": 0.0}
        
        selectors = {}
        selector_votes = defaultdict(lambda: defaultdict(int))
        
        # Analyze up to 3 sample pages
        for sample_url in sample_pages[:3]:
            try:
                # Enforce compliance
                allowed, reason = await self.compliance.validate_request(
                    sample_url, base_url
                )
                if not allowed:
                    continue
                
                async with httpx.AsyncClient(
                    timeout=20.0,
                    headers=self.compliance.get_headers()
                ) as client:
                    response = await client.get(sample_url)
                    html = response.text
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Try to find common product selectors
                    # Title/Name
                    title_candidates = [
                        'h1.product-title', 'h1[itemprop="name"]', 'h1.title',
                        '.product-name', '[data-testid="product-name"]'
                    ]
                    for selector in title_candidates:
                        if soup.select_one(selector):
                            selector_votes['name'][selector] += 1
                    
                    # Price
                    price_candidates = [
                        '.price', '[itemprop="price"]', '.product-price',
                        '[data-price]', '.price--final', '.current-price'
                    ]
                    for selector in price_candidates:
                        if soup.select_one(selector):
                            selector_votes['price'][selector] += 1
                    
                    # Image
                    image_candidates = [
                        'img.product-image', '[itemprop="image"]',
                        '.product-img img', '.main-image img'
                    ]
                    for selector in image_candidates:
                        if soup.select_one(selector):
                            selector_votes['image'][selector] += 1
                    
                    # Description
                    desc_candidates = [
                        '[itemprop="description"]', '.description',
                        '.product-description', '#description'
                    ]
                    for selector in desc_candidates:
                        if soup.select_one(selector):
                            selector_votes['description'][selector] += 1
                
            except Exception as e:
                print(f"Error analyzing {sample_url}: {e}")
                continue
        
        # Select most common selectors
        for field, votes in selector_votes.items():
            if votes:
                best_selector = max(votes.items(), key=lambda x: x[1])
                selectors[field] = best_selector[0]
        
        confidence = min(len(selectors) / 4.0, 1.0)  # 4 main fields
        
        return {
            "selectors": selectors,
            "confidence": round(confidence, 2),
            "fields_found": list(selectors.keys())
        }
    
    async def _phase5_endpoint_discovery(self, url: str) -> Dict:
        """
        Phase 5: API Endpoint Discovery
        
        - Look for inline JSON
        - Detect GraphQL/REST patterns
        - Extract API schemas
        """
        endpoints = []
        
        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                headers=self.compliance.get_headers()
            ) as client:
                await self.compliance.enforce_rate_limit(url)
                response = await client.get(url)
                html = response.text
                
                # Look for common API patterns in HTML
                api_patterns = [
                    (r'/api/[^"\']+', 'REST'),
                    (r'/graphql[^"\']*', 'GraphQL'),
                    (r'/v\d+/[^"\']+', 'REST'),
                    (r'/_next/data/[^"\']+', 'Next.js Data')
                ]
                
                for pattern, api_type in api_patterns:
                    matches = re.findall(pattern, html)
                    for match in matches[:5]:  # Limit
                        full_url = urljoin(url, match)
                        if full_url not in [e['url'] for e in endpoints]:
                            endpoints.append({
                                "url": match,
                                "type": api_type,
                                "method": "GET",
                                "discovered_from": "html_analysis"
                            })
        
        except Exception as e:
            print(f"Endpoint discovery error: {e}")
        
        return {
            "endpoints": endpoints,
            "total_endpoints": len(endpoints)
        }
    
    async def _phase6_pagination_detection(
        self,
        base_url: str,
        listing_pages: List[str]
    ) -> Dict:
        """
        Phase 6: Pagination Detection
        
        - Detect pagination patterns
        - Find filter parameters
        - Identify infinite scroll
        """
        pagination = {
            "type": None,
            "param": None,
            "max_pages": None,
            "infinite_scroll": False
        }
        
        if not listing_pages:
            return pagination
        
        # Analyze first listing page
        sample_url = listing_pages[0]
        
        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                headers=self.compliance.get_headers()
            ) as client:
                await self.compliance.enforce_rate_limit(sample_url)
                response = await client.get(sample_url)
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                
                # Look for pagination links
                pagination_selectors = [
                    'a[href*="page="]',
                    'a[href*="/page/"]',
                    '.pagination a',
                    '[class*="pagination"] a'
                ]
                
                for selector in pagination_selectors:
                    links = soup.select(selector)
                    if links:
                        # Found pagination
                        href = links[0].get('href', '')
                        if 'page=' in href:
                            pagination['type'] = 'query_param'
                            pagination['param'] = 'page'
                        elif '/page/' in href:
                            pagination['type'] = 'path_param'
                            pagination['param'] = 'page'
                        
                        # Try to find max pages
                        page_numbers = []
                        for link in links:
                            href = link.get('href', '')
                            page_match = re.search(r'page[=/](\d+)', href)
                            if page_match:
                                page_numbers.append(int(page_match.group(1)))
                        
                        if page_numbers:
                            pagination['max_pages'] = max(page_numbers)
                        
                        break
                
                # Check for infinite scroll indicators
                infinite_scroll_indicators = [
                    'data-infinite-scroll',
                    'class*="infinite"',
                    'load-more',
                    'show-more'
                ]
                
                for indicator in infinite_scroll_indicators:
                    if soup.select(f'[{indicator}]') or indicator in html.lower():
                        pagination['infinite_scroll'] = True
                        break
        
        except Exception as e:
            print(f"Pagination detection error: {e}")
        
        return pagination
    
    def _calculate_confidence(
        self,
        structure: Dict,
        categories: Dict,
        products: Dict,
        selectors: Dict,
        endpoints: Dict,
        pagination: Dict
    ) -> float:
        """Calculate overall discovery confidence score"""
        scores = []
        
        # Structure score
        if structure.get("allowed"):
            scores.append(1.0 if structure.get("total_links", 0) > 10 else 0.5)
        
        # Categories score
        scores.append(categories.get("confidence", 0.0))
        
        # Products score
        if products.get("total_products_found", 0) > 5:
            scores.append(0.8)
        elif products.get("total_products_found", 0) > 0:
            scores.append(0.5)
        else:
            scores.append(0.0)
        
        # Selectors score
        scores.append(selectors.get("confidence", 0.0))
        
        # Endpoints score
        if endpoints.get("total_endpoints", 0) > 0:
            scores.append(0.7)
        else:
            scores.append(0.0)
        
        # Pagination score
        if pagination.get("type"):
            scores.append(0.8)
        else:
            scores.append(0.3)
        
        # Average
        return round(sum(scores) / len(scores), 2) if scores else 0.0


# Global instance
discovery_service = DiscoveryService()

