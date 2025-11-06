"""Template matching service - match sites to platform templates"""
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PlatformTemplate


class TemplateMatcher:
    """Match sites to platform templates based on fingerprint data"""
    
    async def find_template(
        self,
        platform_name: str,
        fingerprint_data: Optional[Dict[str, Any]] = None,
        variant: Optional[str] = None,
        db: AsyncSession = None
    ) -> Optional[PlatformTemplate]:
        """
        Find the best matching template for a platform
        
        Args:
            platform_name: Detected platform name (e.g., 'shopify', 'magento')
            fingerprint_data: Optional fingerprint data for pattern matching
            variant: Optional platform variant (e.g., '2.x')
            db: Database session (required)
        
        Returns:
            Best matching template or None
        """
        if not db:
            return None
        
        try:
            # Build query for active templates
            stmt = select(PlatformTemplate).where(
                PlatformTemplate.platform_name == platform_name.lower(),
                PlatformTemplate.active == True
            )
            
            # Filter by variant if provided
            if variant:
                stmt = stmt.where(PlatformTemplate.platform_variant == variant)
            
            # Order by confidence and match patterns
            stmt = stmt.order_by(
                PlatformTemplate.confidence.desc().nulls_last(),
                PlatformTemplate.created_at.desc()
            )
            
            result = await db.execute(stmt)
            templates = result.scalars().all()
            
            if not templates:
                return None
            
            # If fingerprint data provided, try pattern matching
            if fingerprint_data and len(templates) > 1:
                best_match = self._match_by_patterns(templates, fingerprint_data)
                if best_match:
                    return best_match
            
            # Return highest confidence template
            return templates[0]
            
        except Exception as e:
            print(f"Error finding template: {e}")
            return None
    
    def _match_by_patterns(
        self,
        templates: list[PlatformTemplate],
        fingerprint_data: Dict[str, Any]
    ) -> Optional[PlatformTemplate]:
        """Match template by analyzing fingerprint patterns"""
        html = fingerprint_data.get("html", "") or ""
        headers = fingerprint_data.get("headers", {}) or {}
        
        best_match = None
        best_score = 0.0
        
        for template in templates:
            if not template.match_patterns:
                continue
            
            score = self._calculate_match_score(template.match_patterns, html, headers)
            if score > best_score:
                best_score = score
                best_match = template
        
        # Only return if score is above threshold
        if best_score >= 0.5:
            return best_match
        
        return None
    
    def _calculate_match_score(
        self,
        match_patterns: Dict[str, Any],
        html: str,
        headers: Dict[str, str]
    ) -> float:
        """Calculate how well fingerprint matches template patterns"""
        score = 0.0
        indicators = match_patterns.get("indicators", [])
        
        if not indicators:
            return 0.0
        
        # Check HTML indicators
        html_indicators = [ind for ind in indicators if isinstance(ind, str)]
        for indicator in html_indicators:
            if indicator.lower() in html.lower():
                score += 1.0
        
        # Check header indicators
        header_indicators = match_patterns.get("header_indicators", {})
        for header_name, expected_value in header_indicators.items():
            header_value = headers.get(header_name, "").lower()
            if expected_value.lower() in header_value:
                score += 0.5
        
        # Normalize score
        total_indicators = len(html_indicators) + len(header_indicators)
        if total_indicators > 0:
            score = score / total_indicators
        
        return min(score, 1.0)
    
    def apply_template_to_blueprint(
        self,
        template: PlatformTemplate,
        discovered_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply template data to discovered blueprint, merging intelligently
        
        Args:
            template: Platform template to apply
            discovered_data: Data from discovery service
        
        Returns:
            Merged blueprint data
        """
        result = discovered_data.copy()
        
        # Merge category selectors (template as base, discovery as enhancement)
        if template.category_selectors:
            if "categories" not in result:
                result["categories"] = {}
            if "category_selectors" not in result["categories"]:
                result["categories"]["category_selectors"] = {}
            
            # Template takes precedence but discovery can add new ones
            template_cats = template.category_selectors or {}
            discovered_cats = result["categories"].get("category_selectors", {}) or {}
            result["categories"]["category_selectors"] = {**template_cats, **discovered_cats}
            result["categories"]["template_applied"] = True
        
        # Merge product selectors
        if template.product_list_selectors:
            if "selectors" not in result:
                result["selectors"] = {}
            if "selectors" not in result["selectors"]:
                result["selectors"]["selectors"] = {}
            
            template_selectors = template.product_list_selectors or {}
            discovered_selectors = result["selectors"].get("selectors", {}) or {}
            result["selectors"]["selectors"] = {**template_selectors, **discovered_selectors}
            result["selectors"]["template_applied"] = True
        
        # Merge API patterns
        if template.api_patterns:
            if "endpoints" not in result:
                result["endpoints"] = {}
            if "endpoints" not in result["endpoints"]:
                result["endpoints"]["endpoints"] = []
            
            template_endpoints = template.api_patterns.get("endpoints", []) or []
            discovered_endpoints = result["endpoints"].get("endpoints", []) or []
            
            # Combine and deduplicate
            all_endpoints = {ep.get("url"): ep for ep in discovered_endpoints}
            for ep in template_endpoints:
                url = ep.get("url")
                if url and url not in all_endpoints:
                    all_endpoints[url] = ep
            
            result["endpoints"]["endpoints"] = list(all_endpoints.values())
            result["endpoints"]["template_applied"] = True
        
        # Merge render hints (template takes precedence)
        if template.render_hints:
            if "render_hints" not in result:
                result["render_hints"] = {}
            result["render_hints"] = {**result.get("render_hints", {}), **template.render_hints}
            result["render_hints"]["template_applied"] = True
        
        # Add template metadata
        result["template_used"] = {
            "template_id": str(template.template_id),
            "platform_name": template.platform_name,
            "platform_variant": template.platform_variant,
            "confidence": template.confidence
        }
        
        return result


# Singleton instance
template_matcher = TemplateMatcher()

