"""LLM integration service for site analysis"""
import os
from typing import Dict, List, Optional
import anthropic
from app.config import settings


class LLMService:
    """Service for LLM-powered site analysis"""
    
    def __init__(self):
        self.client = None
        if settings.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def analyze_site_structure(self, html: str, url: str) -> Dict:
        """Analyze site HTML to detect structure and categories"""
        if not self.client:
            return self._mock_analysis()
        
        prompt = f"""Analyze this e-commerce website and identify:
1. Main product categories (name, URL pattern)
2. Likely CMS/platform (Shopify, WooCommerce, Custom, etc.)
3. Navigation structure
4. Product listing patterns

URL: {url}
HTML (first 5000 chars): {html[:5000]}

Respond in JSON format with:
{{
  "platform": "detected_platform",
  "categories": [{"name": "Category", "url_pattern": "/category/*"}],
  "nav_selectors": ["selector1", "selector2"],
  "confidence": 0.95
}}
"""
        
        try:
            message = self.client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"success": True, "analysis": message.content[0].text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_selectors(self, html: str, field_name: str) -> List[str]:
        """Generate CSS selectors for a given field"""
        if not self.client:
            return self._mock_selectors(field_name)
        
        prompt = f"""Given this HTML, generate robust CSS selectors to extract: {field_name}

HTML: {html[:3000]}

Return 3 selector candidates ranked by robustness, in JSON:
{{
  "selectors": [
    {{"selector": "div.product h1", "confidence": 0.95}},
    {{"selector": "h1[itemprop='name']", "confidence": 0.90}},
    {{"selector": ".product-title", "confidence": 0.85}}
  ]
}}
"""
        
        try:
            message = self.client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=1024,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"success": True, "selectors": message.content[0].text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def repair_selector(self, old_selector: str, html: str, expected_field: str) -> str:
        """Repair a broken selector"""
        if not self.client:
            return old_selector  # Return original if no LLM
        
        prompt = f"""This CSS selector is failing: {old_selector}
It should extract: {expected_field}

New HTML: {html[:2000]}

Provide an updated selector that works with the new HTML structure.
Return only the selector string.
"""
        
        try:
            message = self.client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=256,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            return old_selector
    
    async def score_site_complexity(self, html: str, url: str) -> float:
        """Score site complexity (0-1)"""
        if not self.client:
            return 0.5  # Default complexity
        
        # Simple heuristic analysis for now
        factors = {
            "js_heavy": "window." in html or "document." in html,
            "spa": "React" in html or "Vue" in html or "Angular" in html,
            "dynamic": "data-react" in html or "ng-" in html,
            "anti_bot": "cloudflare" in html.lower() or "recaptcha" in html.lower()
        }
        
        score = sum(factors.values()) / len(factors)
        return min(score + 0.2, 1.0)  # Baseline + factors
    
    def _mock_analysis(self) -> Dict:
        """Mock analysis when no LLM available"""
        return {
            "success": True,
            "analysis": {
                "platform": "unknown",
                "categories": [],
                "nav_selectors": ["nav", ".navigation", "#menu"],
                "confidence": 0.3
            }
        }
    
    def _mock_selectors(self, field_name: str) -> List[str]:
        """Mock selectors when no LLM available"""
        selector_map = {
            "title": ["h1", ".product-title", "[itemprop='name']"],
            "price": [".price", "[itemprop='price']", ".product-price"],
            "description": [".description", "[itemprop='description']", ".product-desc"],
            "image": ["img.product-image", "[itemprop='image']", ".main-image"]
        }
        return selector_map.get(field_name.lower(), [f".{field_name}", f"#{field_name}"])


llm_service = LLMService()

