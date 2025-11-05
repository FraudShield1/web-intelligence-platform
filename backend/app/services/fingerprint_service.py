"""Site fingerprinting service - detect CMS, frameworks, tech stack"""
import re
from typing import Dict, List
import httpx
from bs4 import BeautifulSoup


class FingerprintService:
    """Detect website platform, CMS, and technology stack"""
    
    async def fingerprint_site(self, url: str) -> Dict:
        """Complete site fingerprinting"""
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                html = response.text
                headers = dict(response.headers)
            
            fingerprint = {
                "platform": await self._detect_platform(html, headers),
                "cms": await self._detect_cms(html, headers),
                "javascript_frameworks": await self._detect_js_frameworks(html),
                "anti_bot": await self._detect_anti_bot(html, headers),
                "requires_js": await self._requires_javascript(html),
                "complexity_score": await self._calculate_complexity(html, headers)
            }
            
            return fingerprint
            
        except Exception as e:
            return {"error": str(e), "platform": "unknown"}
    
    async def _detect_platform(self, html: str, headers: Dict) -> str:
        """Detect e-commerce platform"""
        patterns = {
            "Shopify": [
                r"cdn\.shopify\.com",
                r"Shopify\.theme",
                r"shopify-section"
            ],
            "WooCommerce": [
                r"woocommerce",
                r"wp-content/plugins/woocommerce"
            ],
            "Magento": [
                r"Mage\.Cookies",
                r"/static/frontend/",
                r"mage/cookies"
            ],
            "BigCommerce": [
                r"bigcommerce\.com",
                r"cdn\d+\.bigcommerce"
            ],
            "PrestaShop": [
                r"prestashop",
                r"/themes/[^/]+/assets"
            ],
            "Custom": []
        }
        
        for platform, patterns_list in patterns.items():
            if any(re.search(pattern, html, re.IGNORECASE) for pattern in patterns_list):
                return platform
        
        # Check headers
        if "X-ShopifyTrace" in headers or "X-Shopify-Stage" in headers:
            return "Shopify"
        
        return "Custom"
    
    async def _detect_cms(self, html: str, headers: Dict) -> str:
        """Detect CMS"""
        if "WordPress" in html or "wp-content" in html:
            return "WordPress"
        elif "Drupal" in html or "sites/default" in html:
            return "Drupal"
        elif "Joomla" in html:
            return "Joomla"
        return "None"
    
    async def _detect_js_frameworks(self, html: str) -> List[str]:
        """Detect JavaScript frameworks"""
        frameworks = []
        
        if re.search(r"react", html, re.IGNORECASE) or "data-react" in html:
            frameworks.append("React")
        if "ng-app" in html or "angular" in html.lower():
            frameworks.append("Angular")
        if "Vue" in html or "_vue" in html:
            frameworks.append("Vue")
        if "next" in html.lower() and "/_next/" in html:
            frameworks.append("Next.js")
        if "nuxt" in html.lower():
            frameworks.append("Nuxt")
        
        return frameworks or ["None"]
    
    async def _detect_anti_bot(self, html: str, headers: Dict) -> Dict:
        """Detect anti-bot/protection systems"""
        protections = {
            "cloudflare": bool(re.search(r"cloudflare", html, re.IGNORECASE)) or "cf-ray" in headers,
            "recaptcha": "recaptcha" in html.lower(),
            "datadome": "datadome" in html.lower(),
            "imperva": "imperva" in html.lower() or "_Incapsula" in html,
            "perimeterx": "perimeterx" in html.lower()
        }
        
        return {
            "detected": any(protections.values()),
            "services": [k for k, v in protections.items() if v]
        }
    
    async def _requires_javascript(self, html: str) -> bool:
        """Check if site requires JS rendering"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check for SPA indicators
        body_text = soup.body.get_text(strip=True) if soup.body else ""
        
        # If body is nearly empty, likely needs JS
        if len(body_text) < 200:
            return True
        
        # Check for common SPA root elements
        if soup.find(id="root") or soup.find(id="app"):
            return True
        
        # Check script dominance
        scripts = soup.find_all('script')
        if len(scripts) > 20:
            return True
        
        return False
    
    async def _calculate_complexity(self, html: str, headers: Dict) -> float:
        """Calculate site complexity score (0-1)"""
        score = 0.0
        
        # Base factors
        if await self._requires_javascript(html):
            score += 0.3
        
        anti_bot = await self._detect_anti_bot(html, headers)
        if anti_bot["detected"]:
            score += 0.2 * len(anti_bot["services"])
        
        # Framework complexity
        frameworks = await self._detect_js_frameworks(html)
        if "React" in frameworks or "Vue" in frameworks or "Angular" in frameworks:
            score += 0.2
        
        # HTML complexity
        if len(html) > 100000:
            score += 0.1
        
        return min(score, 1.0)


fingerprint_service = FingerprintService()

