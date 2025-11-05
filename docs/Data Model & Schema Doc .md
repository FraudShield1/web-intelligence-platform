# Data Model & Schema

## 1. Key Entities

### Site
- site_id (UUID)  
- domain (string)  
- platform (enum) e.g. Shopify, Magento, Custom  
- discovery_method (enum) Static/Browser/API  
- complexity_score (float)  
- business_value_score (float)  
- created_at, updated_at  
- last_discovered_at  
- blueprint_version (int)  
- status (enum) Pending, Ready, Review, Failed

### Blueprint
- blueprint_id (UUID)  
- site_id (FK)  
- version (int)  
- categories_json (file/path)  
- endpoints_json (file/path)  
- render_hints_json (file/path)  
- selectors_json (file/path)  
- confidence_score (float)  
- created_at

### Job
- job_id  
- site_id  
- job_type (enum: Fingerprint, Discovery, Extraction)  
- method (enum: Static, Browser, API)  
- status (enum) Queued, Running, Success, Fail  
- attempt_count  
- started_at, ended_at  
- error_code, error_message

### Selector
- selector_id  
- blueprint_id  
- field_name (e.g., price, title, image_url)  
- css_selector (string)  
- xpath (string)  
- confidence (float)  
- created_at

### Analytics_Metric
- metric_id  
- site_id  
- date  
- discovery_time_seconds  
- num_categories_found  
- selector_failure_rate  
- fetch_cost_usd  
- etc.

## 2. Blueprint JSON Formats

### categories.json
[
{
"id": "cat-uuid",
"name": "Televisions & Home Audio",
"slug": "televisions-home-audio",
"url": "https://example.com/collections/tv-home
",
"parent_id": null,
"depth": 1,
"example_product_url": "...",
"confidence": 0.92
},
...
]


### endpoints.json


{
"api_base": "https://api.example.com/v1/
",
"endpoints": [
{
"url": "/products",
"method": "GET",
"params": {"page":1,"size":50},
"example_response_schema": {...},
"confidence": 0.88
},
...
]
}


### render_hints.json


{
"requires_js": true,
"browser_type": "chromium",
"wait_for_selector": ".product-list",
"timeout_seconds": 20
}


## 3. Versioning & Change Tracking
- Blueprints get version numbers; previous versions retained for rollback.  
- Store diffs between versions (e.g., categories added/removed, selectors changed).  
- Include `updated_at`, `changed_by` fields where relevant.

## 4. Analytics Schema
Define tables/fields for monitoring jobs, success/fail rates, cost metrics, selector churn, etc (see Analytics section in Architecture doc).


