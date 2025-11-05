# LLM Prompt Templates
## Complete Prompt Library for Web Intelligence Platform

---

## 1. CATEGORY DISCOVERY PROMPTS

### 1.1 Main Category Extraction

```markdown
## System Prompt
You are an expert web analyst specializing in e-commerce site structure.
Your task is to identify category navigation on e-commerce websites.
You think step-by-step and provide confidence scores for each finding.

## User Prompt

### Context
- **Base URL**: {base_url}
- **Site Name**: {site_name}
- **Platform**: {platform_hint}

### Task
Analyze the provided HTML and identify ALL product categories visible in:
1. Main navigation bar
2. Mega-menu (if present)
3. Side navigation
4. Footer category links
5. Breadcrumbs or category indicators

### HTML Content (first 50KB)
```
{html_content}
```

### Output Requirements
Return a JSON array with this structure for each category:

```json
{
  "categories": [
    {
      "name": "Category Name",
      "url": "https://example.com/categories/category-name",
      "selector": ".nav-item a[href*='category']",
      "parent_category": "Parent Name or null",
      "depth": 1,
      "confidence": 0.95,
      "reasoning": "Found in main nav, standard e-commerce pattern",
      "is_collection": true
    }
  ],
  "notes": "Found 12 main categories and 45 subcategories.",
  "structure_type": "hierarchical",
  "total_depth": 3
}
```

### Confidence Scoring Guide
- 0.95-1.0: Clear, standard e-commerce category
- 0.80-0.94: Likely category, minor ambiguity
- 0.65-0.79: Possible category, needs validation
- <0.65: Questionable, mark for manual review

### Important Rules
1. Be thorough—don't miss subcategories
2. Only include actual product collections, not blogs/support/about
3. Provide full URLs, not just paths
4. Include CSS selector that uniquely identifies the link
5. Mark confidence honestly—be conservative on uncertain findings
```

### 1.2 Category Validation

```markdown
## Task: Validate Category Extraction

Given these extracted categories, validate they are real product categories:

**Categories to validate:**
```json
{categories_json}
```

**Sample product listing page HTML:**
```
{sample_listing_html}
```

### Validation Checks
1. Does visiting this URL lead to a product listing page?
2. Are the selectors still valid on product pages?
3. Is this a real product category or a filter/subcollection?
4. Are there any parent-child relationships I missed?

### Output Format
```json
{
  "validations": [
    {
      "category_id": "cat-001",
      "is_valid": true,
      "issues": [],
      "confidence": 0.92
    }
  ],
  "summary": "12/12 categories validated successfully"
}
```
```

---

## 2. SELECTOR & FIELD EXTRACTION PROMPTS

### 2.1 Product Listing Selector Generation

```markdown
## System Prompt
You are an expert CSS and XPath selector generator for web scraping.
Your selectors must be:
- Specific (not matching unintended elements)
- Robust (work across similar pages on the same site)
- Readable (maintainable by other engineers)

## Task: Generate Selectors for Product Fields

**Listing Page HTML:**
```
{listing_page_html}
```

**Fields to extract from each product:**
- title
- price
- sale_price (if applicable)
- image_url
- product_url
- rating (if available)
- availability (if shown)
- sku (if visible)

### Instructions
1. Analyze the HTML structure
2. Identify the repeating product container selector
3. For each field, find the most robust CSS selector
4. Provide alternative XPath if CSS is unreliable
5. Test mentally on 2-3 products to ensure accuracy

### Output Format
```json
{
  "product_container": ".product-item",
  "selectors": {
    "title": {
      "css": ".product-title",
      "xpath": ".//h2[@class='product-title']/text()",
      "type": "text",
      "confidence": 0.98,
      "explanation": "Consistent across all products"
    },
    "price": {
      "css": ".product-price",
      "xpath": ".//span[@class='price']/text()",
      "type": "currency",
      "confidence": 0.95,
      "explanation": "Standard e-commerce pattern"
    },
    "image_url": {
      "css": ".product-image img",
      "xpath": ".//img[@class='product-image']/@src",
      "type": "url",
      "confidence": 0.97,
      "explanation": "Direct img src attribute"
    }
  },
  "notes": "Site uses BEM class naming, very clean structure"
}
```

### Confidence Rules
- 0.95+: Highly specific, standard pattern
- 0.80-0.94: Good selector, minor robustness concerns
- <0.80: Risky, may break on other pages
```

### 2.2 Complex Selector Analysis

```markdown
## Task: Analyze & Improve Problematic Selectors

**Current selectors that are failing:**
```json
{failing_selectors}
```

**Failure examples:**
```
{failure_html_samples}
```

### Analysis
1. Why is this selector failing? (Element structure changed, class renamed, etc.)
2. What's the pattern on working vs. failing pages?
3. Suggest 2-3 alternative selectors ordered by robustness

### Output
```json
{
  "analysis": "Class names are generated dynamically; need content-based selector",
  "alternatives": [
    {
      "selector": ".product-grid > div[data-testid='product']",
      "confidence": 0.88,
      "reason": "Uses stable data attribute"
    },
    {
      "selector": "main > section > div > article",
      "confidence": 0.75,
      "reason": "Semantic HTML structure"
    }
  ]
}
```
```

---

## 3. API ENDPOINT DISCOVERY PROMPTS

### 3.1 Network Request Analysis

```markdown
## Task: Identify API Endpoints from Network Requests

**Network trace captured during page load and user interaction:**
```json
{network_requests}
```

**Context:**
- Domain: {domain}
- Platform: {platform}
- Interactions: scrolling, filtering, pagination

### Analysis
1. Identify all unique API endpoints called
2. Categorize by purpose (product listing, search, cart, etc.)
3. Extract request/response patterns
4. Note authentication method if present
5. Identify rate limiting headers

### Output Format
```json
{
  "endpoints": [
    {
      "url": "/api/v1/products",
      "method": "GET",
      "purpose": "product_listing",
      "query_params": {
        "page": 1,
        "limit": 50,
        "sort": "popularity"
      },
      "response_example": {...},
      "confidence": 0.95,
      "authentication": "bearer_token"
    },
    {
      "url": "/api/v1/search",
      "method": "POST",
      "purpose": "product_search",
      "body_params": {"q": "string", "filters": "object"},
      "response_example": {...},
      "confidence": 0.88
    }
  ],
  "authentication_method": "JWT in Authorization header",
  "rate_limit": "1000 requests per minute",
  "notes": "GraphQL endpoint also detected at /graphql"
}
```

### Scoring Criteria
- Endpoints with clear, stable structure: 0.90+
- Endpoints that may be internal or change: 0.70-0.89
- Experimental or undocumented: <0.70
```

### 3.2 GraphQL Schema Detection

```markdown
## Task: Discover GraphQL Schema from Network Traffic

**GraphQL queries/responses captured:**
```json
{graphql_requests}
```

### Tasks
1. Extract the GraphQL schema structure
2. Identify key Query fields (products, search, categories)
3. Find available filters and arguments
4. Determine field availability

### Output
```json
{
  "has_graphql": true,
  "graphql_endpoint": "/api/graphql",
  "schema": {
    "Query": {
      "products": {
        "args": ["first", "after", "filter"],
        "fields": ["id", "title", "price", "image"]
      },
      "search": {
        "args": ["query", "first"],
        "fields": ["id", "title", "type"]
      }
    }
  },
  "authentication": "JWT token required",
  "confidence": 0.92
}
```
```

---

## 4. PLATFORM FINGERPRINTING PROMPTS

### 4.1 Technology Stack Detection

```markdown
## Task: Identify the E-Commerce Platform

**HTML Head Section:**
```html
{html_head}
```

**HTTP Response Headers:**
```
{http_headers}
```

**Page Content (first 20KB):**
```
{page_content}
```

### Detection Strategy
1. Look for platform-specific meta tags
2. Check for platform-specific JavaScript libraries
3. Analyze HTTP headers (Server, X-Powered-By)
4. Look for API endpoints or configuration in page
5. Check for platform-specific CSS class patterns

### Platform Indicators
- **Shopify**: Shopify.AppBridge, myshopify.com, Shopify meta tag
- **Magento**: Magento_Js, mage namespace, Magento_*
- **WooCommerce**: wp-content, woocommerce class names
- **BigCommerce**: bigcommerce, storefront
- **Custom**: No clear indicators

### Output
```json
{
  "platform": "shopify",
  "confidence": 0.98,
  "indicators": [
    "Shopify.AppBridge found in window object",
    "myshopify.com domain detected",
    "meta name='shopify' found"
  ],
  "version_hint": "2023.04 (estimated)",
  "has_rest_api": true,
  "has_graphql_api": true,
  "js_frameworks": ["liquid", "jquery"],
  "cdn": "Shopify CDN"
}
```
```

### 4.2 JavaScript Rendering Detection

```markdown
## Task: Determine if JavaScript Rendering is Required

**Analysis data:**
```json
{analysis_data}
```

Where analysis includes:
- Initial HTML content
- Network requests during page load
- Timing of content availability
- Network trace

### Questions
1. Is critical content rendered on initial HTML load?
2. Are products visible without JavaScript?
3. Does pagination/filtering require JS?
4. Is there a GraphQL/API endpoint called on load?

### Output
```json
{
  "requires_js_rendering": true,
  "for_content": "product_listings",
  "why": "Products loaded dynamically via /api/products endpoint",
  "recommended_browser": "chromium",
  "wait_for_selector": ".product-grid",
  "timeout_seconds": 30,
  "cost_multiplier": 3.0,
  "confidence": 0.95
}
```
```

---

## 5. SITE SCORING PROMPTS

### 5.1 Business Value Assessment

```markdown
## Task: Estimate Business Value of Site

**Site Information:**
- Domain: {domain}
- Platform: {platform}
- Estimated Monthly Traffic: {monthly_traffic}
- Niche/Category: {category}
- Geographic Focus: {geo}
- Language: {language}

**Additional Context:**
```json
{site_metadata}
```

### Factors to Consider
1. **Market Size**: How large is the target market?
2. **Data Quality**: Are product listings complete and clean?
3. **Update Frequency**: How often do products/prices change?
4. **Availability**: 24/7 accessible without CAPTCHAs?
5. **Data Freshness Need**: Real-time vs. daily vs. weekly
6. **Competitive Landscape**: Are competitors already scraping this?
7. **Product Diversity**: Number of unique products available
8. **Price Volatility**: Do prices change frequently?

### Output
```json
{
  "business_value_score": 0.87,
  "breakdown": {
    "market_size": 0.9,
    "data_quality": 0.85,
    "accessibility": 0.88,
    "update_frequency": 0.82,
    "product_diversity": 0.90,
    "uniqueness": 0.75
  },
  "estimated_roi_months": 2.5,
  "recommendation": "High priority - large market, good data, reasonable costs",
  "risk_factors": ["Frequent page structure changes", "IP blocking"],
  "opportunity": "3.2x ROI if selector reliability > 85%"
}
```
```

### 5.2 Complexity Assessment

```markdown
## Task: Assess Site Complexity Score

**Site Characteristics:**
```json
{site_characteristics}
```

### Complexity Factors
1. **Structure Complexity**: Simple table-based vs. complex SPA
2. **Rendering Method**: Static HTML vs. JS-heavy
3. **Dynamic Content**: Fixed structure vs. frequently changing
4. **Anti-scraping Measures**: None vs. aggressive
5. **Pagination Style**: Offset vs. cursor vs. infinite scroll
6. **Data Nesting**: Flat structure vs. deeply nested
7. **Image Handling**: Direct URLs vs. CDN with tokens
8. **Maintenance Burden**: Selector stability

### Output
```json
{
  "complexity_score": 0.68,
  "breakdown": {
    "structure": 0.7,
    "rendering": 0.6,
    "dynamic_content": 0.65,
    "anti_scraping": 0.75,
    "pagination": 0.8,
    "data_nesting": 0.65,
    "maintenance": 0.65
  },
  "difficulty_level": "medium",
  "estimated_setup_time_hours": 8,
  "estimated_monthly_maintenance_hours": 4,
  "main_challenges": [
    "Heavy JavaScript rendering",
    "Dynamic class names",
    "Aggressive IP rate limiting"
  ],
  "recommendation": "Browser method recommended; 30-day selector lifetime expected"
}
```
```

---

## 6. QUALITY ASSURANCE PROMPTS

### 6.1 Blueprint Validation

```markdown
## Task: Validate Generated Blueprint

**Generated Blueprint:**
```json
{generated_blueprint}
```

**Sample Pages Tested:**
```
{sample_pages}
```

### Validation Checklist
1. Are all categories real product collections?
2. Do all selectors work on test pages?
3. Are confidence scores accurate?
4. Is the blueprint internally consistent?
5. Are there obvious missing categories?
6. Are endpoints correctly documented?
7. Are render hints accurate?

### Output
```json
{
  "valid": true,
  "issues": [],
  "warnings": [
    "Subcategory detection incomplete (found 12/15 expected)",
    "One selector has 85% pass rate, recommend review"
  ],
  "passes": [
    "All main categories detected",
    "API endpoints correctly identified",
    "Render hints appropriate"
  ],
  "approval": "Ready for use",
  "confidence": 0.91
}
```
```

### 6.2 Selector Testing Analysis

```markdown
## Task: Analyze Selector Test Failures

**Selector that failed:**
```json
{failed_selector}
```

**Failure details:**
```
{failure_details}
```

**Working HTML example:**
```html
{working_html}
```

**Broken HTML example:**
```html
{broken_html}
```

### Analysis
1. What changed between working and broken versions?
2. Is this a temporary styling change or structural?
3. Is a more robust selector possible?
4. Should we escalate for manual review?

### Output
```json
{
  "analysis": "Class names were minified; structure remains stable",
  "recommendation": "regenerate_selector",
  "new_selector": ".product-item:first-child",
  "expected_reliability": 0.92,
  "action": "Auto-regenerate and test"
}
```
```

---

## 7. ADVANCED PROMPTS

### 7.1 Visual Content Extraction (for obfuscated sites)

```markdown
## Task: Extract Information from Visual Layout

**Screenshot/Visual Content:**
```
{visual_content}
```

**Context:**
- Site uses heavy obfuscation
- CSS selectors are dynamic/minified
- Need to extract by visual position

### Task
Identify key elements by position and visual characteristics:
1. Product title (top, bold text)
2. Price (red/highlighted, numeric)
3. Image (large visual, top-left)
4. Links (underlined, colored text)

### Output
```json
{
  "visual_elements": [
    {
      "element_type": "product_title",
      "visual_description": "Bold text, 16px, black, top area",
      "approximate_position": "x: 10-50%, y: 5-10%",
      "confidence": 0.75,
      "extraction_method": "ocr_or_ml_model"
    }
  ],
  "recommendation": "Use ML-based visual extraction service for this site"
}
```
```

### 7.2 Auto-Repair Prompt

```markdown
## Task: Repair Broken Selectors

**Broken Selectors Report:**
```json
{broken_selectors_report}
```

**Current Blueprint Version:** 3
**Last Successful Blueprint Version:** 2

### Strategy
1. Fetch fresh HTML sample from site
2. Compare old working structure with current
3. Identify minimal CSS class/structure changes
4. Propose new selectors for 50%+ fix rate

### Output
```json
{
  "analysis": "Site migrated to new CSS class naming (prefix changed from 'shop-' to 'market-')",
  "fixes": [
    {
      "selector_id": "sel-001",
      "old_selector": ".shop-product-title",
      "new_selector": ".market-product-title",
      "confidence": 0.94,
      "action": "update"
    }
  ],
  "new_blueprint_version": 4,
  "expected_fix_rate": 0.68,
  "needs_manual_review": ["sel-005", "sel-008"]
}
```
```

### 7.3 Competitive Scraping Analysis

```markdown
## Task: Analyze Scraper Resilience

Given multiple sites in the same e-commerce category:

```json
{sites_list}
```

### Analyze
1. Which site is most resilient to changes?
2. Which has most stable data format?
3. Which offers best ROI?
4. Rank by sustainability score

### Output
```json
{
  "sustainability_ranking": [
    {
      "domain": "site-a.com",
      "sustainability_score": 0.92,
      "reasoning": "Uses stable data attributes, minimal styling changes",
      "estimate_useful_lifetime_months": 24
    },
    {
      "domain": "site-b.com",
      "sustainability_score": 0.76,
      "reasoning": "Frequent redesigns, dynamic classes",
      "estimate_useful_lifetime_months": 8
    }
  ],
  "recommended_priority": "site-a"
}
```
```

---

## 8. PROMPT BEST PRACTICES

### 8.1 Optimization Techniques

1. **Temperature Settings**
   - Category extraction: 0.3 (deterministic)
   - Analysis & reasoning: 0.7 (more creative)
   - Validation: 0.1 (strict)

2. **Token Optimization**
   - Summarize HTML to first 30-50KB
   - Provide JSON schema structure upfront
   - Use examples in prompt

3. **Error Handling**
   - Add fallback instructions
   - Request JSON-only output
   - Validate output schema

4. **Confidence Calibration**
   - Provide confidence scoring guidelines
   - Request reasoning with every score
   - Track LLM confidence vs. actual success

### 8.2 Cost Optimization

```
# Cost per type (approximate, using Claude):
- Category extraction: $0.10-0.30 per site
- Selector generation: $0.20-0.50 per site
- API analysis: $0.15-0.40 per site
- Blueprint validation: $0.10-0.25 per site

# Optimization strategies:
1. Batch similar sites together
2. Use cached selectors for known platforms
3. Reuse templates to reduce tokens
4. Async processing for low-priority sites
```

### 8.3 Quality Metrics

Track for each prompt:
- Output validity (schema match)
- Confidence score accuracy
- Time-to-fix when wrong
- Cost per successful extraction
- Failure rate by issue type

---

## 9. PROMPT VERSIONING & AB TESTING

### Version History
- **v1.0** (Jan 2024): Initial prompts
- **v1.1** (Feb 2024): Added confidence scoring, improved selector specificity
- **v1.2** (Mar 2024): Enhanced API detection, GraphQL support

### AB Testing Examples

**Test 1: Category Extraction Format**
- Control: Narrative descriptions
- Test: Structured JSON only
- Result: JSON performed 12% better on selector generation

**Test 2: Selector Confidence Scoring**
- Control: 0-1.0 scale
- Test: 5-tier scale (Very Low, Low, Medium, High, Very High)
- Result: No significant difference, keeping 0-1.0 for compatibility

---

## 10. DEPLOYMENT & MONITORING

### Monitoring Queries

```python
# Track prompt effectiveness
SELECT
    prompt_version,
    AVG(actual_success_rate) as success_rate,
    AVG(confidence_score) as avg_confidence,
    STDDEV(confidence_score) as confidence_stddev,
    COUNT(*) as usage_count
FROM llm_calls_log
WHERE prompt_type = 'category_extraction'
GROUP BY prompt_version
ORDER BY success_rate DESC;
```

### Escalation Rules

- If confidence > 0.9 and actual success < 0.85: Review prompt
- If output validation fails: Log for manual review
- If cost exceeds threshold: Switch to cheaper model
- If latency > 30s: Use async processing


