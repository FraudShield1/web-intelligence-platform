# API Specification
## Complete OpenAPI 3.0 Schema & Endpoint Reference

---

## 1. AUTHENTICATION & AUTHORIZATION

### 1.1 JWT Authentication

All requests (except `/health` and `/auth/login`) require JWT bearer token:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Payload:**
```json
{
  "sub": "user_id",
  "exp": 1234567890,
  "iat": 1234567800,
  "role": "admin|product_lead|scraper_engineer|viewer",
  "org_id": "org_uuid"
}
```

### 1.2 Role-Based Access Control

| Endpoint Pattern | Admin | Product Lead | Scraper Eng | Viewer |
|-----------------|-------|-------------|------------|--------|
| `GET /sites` | ✓ | ✓ | ✓ | ✓ |
| `POST /sites` | ✓ | ✓ | ✗ | ✗ |
| `PUT /sites/{id}` | ✓ | ✓ | ✗ | ✗ |
| `DELETE /sites/{id}` | ✓ | ✗ | ✗ | ✗ |
| `POST /jobs` | ✓ | ✓ | ✓ | ✗ |
| `GET /blueprints` | ✓ | ✓ | ✓ | ✓ |
| `GET /analytics` | ✓ | ✓ | ✓ | ✓ |

---

## 2. SITES ENDPOINTS

### 2.1 Create Site

**POST** `/api/v1/sites`

Creates a new site and initiates fingerprinting.

**Request:**
```json
{
  "domain": "example-store.com",
  "business_value_score": 0.85,
  "priority": "high",
  "notes": "Major category"
}
```

**Response:** `201 Created`
```json
{
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "domain": "example-store.com",
  "status": "pending",
  "fingerprinting_job_id": "job-uuid",
  "created_at": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T10:35:00Z"
}
```

**Errors:**
- `400 Bad Request` – Invalid domain format
- `409 Conflict` – Domain already exists
- `429 Too Many Requests` – Rate limit exceeded

---

### 2.2 List Sites

**GET** `/api/v1/sites`

Retrieve all sites with filtering and pagination.

**Query Parameters:**
```
GET /api/v1/sites?status=ready&platform=shopify&limit=50&offset=0&sort_by=-created_at
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | string | - | Filter: pending, ready, review, failed |
| `platform` | string | - | Filter: shopify, magento, woocommerce, custom |
| `search` | string | - | Search domain or notes |
| `min_score` | float | - | Filter: business_value_score >= value |
| `limit` | int | 50 | Results per page (max 100) |
| `offset` | int | 0 | Pagination offset |
| `sort_by` | string | -created_at | Sort field: created_at, complexity_score, business_value_score |

**Response:** `200 OK`
```json
{
  "total": 1234,
  "limit": 50,
  "offset": 0,
  "sites": [
    {
      "site_id": "123e4567-e89b-12d3-a456-426614174000",
      "domain": "example.com",
      "platform": "shopify",
      "status": "ready",
      "complexity_score": 0.72,
      "business_value_score": 0.85,
      "last_discovered_at": "2024-01-15T10:30:00Z",
      "blueprint_version": 3,
      "current_job_status": "success"
    },
    ...
  ]
}
```

---

### 2.3 Get Site Details

**GET** `/api/v1/sites/{site_id}`

Retrieve detailed information about a specific site.

**Path Parameters:**
```
site_id (UUID): Unique site identifier
```

**Response:** `200 OK`
```json
{
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "domain": "example.com",
  "platform": "shopify",
  "status": "ready",
  "complexity_score": 0.72,
  "business_value_score": 0.85,
  "fingerprint_data": {
    "cms": "shopify",
    "js_frameworks": ["react", "jquery"],
    "tech_stack": ["nginx", "cloudflare", "fastly"],
    "has_graphql_api": true,
    "has_rest_api": true
  },
  "blueprint_version": 3,
  "last_discovered_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-10T08:00:00Z",
  "notes": "Premium e-commerce client"
}
```

**Errors:**
- `404 Not Found` – Site does not exist

---

### 2.4 Update Site

**PUT** `/api/v1/sites/{site_id}`

Update site metadata (does not trigger rediscovery).

**Request:**
```json
{
  "business_value_score": 0.95,
  "priority": "critical",
  "notes": "Updated due to revenue increase"
}
```

**Response:** `200 OK`
```json
{
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "updated_at": "2024-01-15T14:22:00Z"
}
```

---

### 2.5 Delete Site

**DELETE** `/api/v1/sites/{site_id}`

Delete a site and all associated blueprints/jobs.

**Response:** `204 No Content`

**Errors:**
- `403 Forbidden` – Insufficient permissions (admin only)

---

## 3. JOBS ENDPOINTS

### 3.1 Create Job

**POST** `/api/v1/jobs`

Manually trigger discovery or other jobs for a site.

**Request:**
```json
{
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "job_type": "discovery",
  "method": "auto",
  "priority": "high",
  "parameters": {
    "force_refresh": true,
    "skip_cache": false
  }
}
```

**Response:** `201 Created`
```json
{
  "job_id": "job-987f6543-21a0-b456-d789-012345678901",
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "job_type": "discovery",
  "status": "queued",
  "position_in_queue": 42,
  "estimated_start": "2024-01-15T10:45:00Z",
  "created_at": "2024-01-15T10:35:00Z"
}
```

**Errors:**
- `400 Bad Request` – Invalid job_type or method
- `404 Not Found` – Site not found
- `409 Conflict` – Job already running for this site

---

### 3.2 Get Job Status

**GET** `/api/v1/jobs/{job_id}`

Retrieve job progress and results.

**Response:** `200 OK`
```json
{
  "job_id": "job-987f6543-21a0-b456-d789-012345678901",
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "job_type": "discovery",
  "method": "static",
  "status": "running",
  "progress": {
    "current_step": "extracting_selectors",
    "percentage": 65,
    "message": "Extracting product selectors..."
  },
  "attempt_count": 1,
  "started_at": "2024-01-15T10:40:00Z",
  "estimated_completion": "2024-01-15T10:55:00Z",
  "heartbeat_at": "2024-01-15T10:45:30Z"
}
```

**When Completed (status: success):**
```json
{
  "job_id": "job-...",
  "status": "success",
  "ended_at": "2024-01-15T10:55:00Z",
  "duration_seconds": 900,
  "result": {
    "blueprint_id": "bp-uuid",
    "blueprint_version": 1,
    "categories_found": 47,
    "endpoints_found": 8,
    "selectors_generated": 156,
    "confidence_score": 0.89
  }
}
```

**When Failed (status: failed):**
```json
{
  "job_id": "job-...",
  "status": "failed",
  "ended_at": "2024-01-15T10:45:00Z",
  "error": {
    "code": "4002",
    "message": "IP blocked (403 Forbidden)",
    "recovery_action": "Escalating to human review"
  },
  "next_retry": "2024-01-15T11:00:00Z"
}
```

---

### 3.3 List Jobs

**GET** `/api/v1/jobs`

List jobs with filters.

**Query Parameters:**
```
GET /api/v1/jobs?site_id=uuid&status=running&limit=20&sort_by=-created_at
```

| Param | Type | Description |
|-------|------|-------------|
| `site_id` | UUID | Filter by site |
| `status` | string | Filter: queued, running, success, failed |
| `job_type` | string | Filter: fingerprint, discovery, extraction |
| `limit` | int | Results per page (default 50) |
| `sort_by` | string | Sort order |

**Response:** `200 OK`
```json
{
  "total": 523,
  "jobs": [
    {
      "job_id": "job-uuid",
      "site_id": "site-uuid",
      "job_type": "discovery",
      "status": "success",
      "created_at": "2024-01-15T10:00:00Z",
      "ended_at": "2024-01-15T10:20:00Z"
    },
    ...
  ]
}
```

---

### 3.4 Cancel Job

**POST** `/api/v1/jobs/{job_id}/cancel`

Cancel a queued or running job.

**Response:** `200 OK`
```json
{
  "job_id": "job-uuid",
  "status": "cancelled",
  "cancelled_at": "2024-01-15T10:50:00Z"
}
```

**Errors:**
- `409 Conflict` – Job already completed
- `404 Not Found` – Job not found

---

### 3.5 Retry Job

**POST** `/api/v1/jobs/{job_id}/retry`

Retry a failed job.

**Request:**
```json
{
  "increment_priority": true
}
```

**Response:** `201 Created`
```json
{
  "old_job_id": "job-uuid",
  "new_job_id": "job-uuid-2",
  "new_status": "queued"
}
```

**Errors:**
- `400 Bad Request` – Job not in failed state
- `409 Conflict` – Max retries exceeded

---

## 4. BLUEPRINTS ENDPOINTS

### 4.1 Get Latest Blueprint

**GET** `/api/v1/sites/{site_id}/blueprint`

Retrieve the most recent blueprint for a site.

**Response:** `200 OK`
```json
{
  "blueprint_id": "bp-123e4567-e89b-12d3-a456-426614174000",
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "version": 3,
  "confidence_score": 0.92,
  "created_at": "2024-01-15T10:30:00Z",
  "created_by": "job-uuid",
  "categories_data": [
    {
      "id": "cat-001",
      "name": "Electronics",
      "slug": "electronics",
      "url": "https://example.com/collections/electronics",
      "parent_id": null,
      "depth": 1,
      "confidence": 0.95
    },
    ...
  ],
  "endpoints_data": [
    {
      "url": "/api/v1/products",
      "method": "GET",
      "params": {
        "page": 1,
        "limit": 50
      },
      "example_response_schema": {...},
      "confidence": 0.88
    },
    ...
  ],
  "render_hints_data": {
    "requires_js": true,
    "browser_type": "chromium",
    "wait_for_selector": ".product-grid",
    "timeout_seconds": 30
  },
  "selectors_data": [
    {
      "selector_id": "sel-001",
      "field_name": "title",
      "css_selector": ".product-title",
      "xpath": "//h2[@class='product-title']",
      "confidence": 0.94,
      "generation_method": "llm",
      "test_pass_rate": 0.98
    },
    ...
  ]
}
```

**Errors:**
- `404 Not Found` – Site or blueprint not found

---

### 4.2 Get Blueprint By ID

**GET** `/api/v1/blueprints/{blueprint_id}`

Retrieve a specific blueprint version.

**Response:** `200 OK` (same as above)

---

### 4.3 List Blueprint Versions

**GET** `/api/v1/sites/{site_id}/blueprints`

List all versions of a site's blueprints.

**Query Parameters:**
```
limit=10&sort_by=-version
```

**Response:** `200 OK`
```json
{
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "total_versions": 5,
  "versions": [
    {
      "blueprint_id": "bp-uuid-1",
      "version": 5,
      "confidence_score": 0.94,
      "created_at": "2024-01-15T14:00:00Z",
      "changes": {
        "added_categories": 3,
        "removed_categories": 1,
        "updated_selectors": 8
      }
    },
    {
      "blueprint_id": "bp-uuid-2",
      "version": 4,
      "confidence_score": 0.91,
      "created_at": "2024-01-10T12:00:00Z"
    },
    ...
  ]
}
```

---

### 4.4 Rollback Blueprint

**POST** `/api/v1/blueprints/{blueprint_id}/rollback`

Revert to a previous blueprint version.

**Request:**
```json
{
  "to_version": 3,
  "reason": "Previous version had better selector accuracy"
}
```

**Response:** `201 Created`
```json
{
  "blueprint_id": "bp-new-uuid",
  "version": 6,
  "from_version": 5,
  "to_version": 3,
  "created_at": "2024-01-15T15:00:00Z"
}
```

---

### 4.5 Export Blueprint

**GET** `/api/v1/blueprints/{blueprint_id}/export`

Download blueprint in various formats for integration with scrapers.

**Query Parameters:**
```
?format=json&include=categories,endpoints,selectors,render_hints
```

| Param | Type | Options | Default |
|-------|------|---------|---------|
| `format` | string | json, yaml, csv | json |
| `include` | string | Comma-separated: categories, endpoints, selectors, render_hints | all |

**Response:** `200 OK` with appropriate Content-Type
```json
{
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "blueprint_version": 3,
  "exported_at": "2024-01-15T15:00:00Z",
  "categories": [...],
  "endpoints": [...],
  "selectors": [...],
  "render_hints": {...}
}
```

**Alternative Format (YAML):**
```
Site Blueprint Export
Site ID: 123e4567-e89b-12d3-a456-426614174000
Version: 3
Exported At: 2024-01-15T15:00:00Z

Categories:
  - id: cat-001
    name: Electronics
    url: https://example.com/collections/electronics
    confidence: 0.95
...
```

---

## 5. ANALYTICS ENDPOINTS

### 5.1 Dashboard Overview

**GET** `/api/v1/analytics/dashboard`

High-level metrics for executive/operations overview.

**Query Parameters:**
```
?date_range=7d&include=overview,trends,alerts
```

| Param | Options | Default |
|-------|---------|---------|
| `date_range` | 1d, 7d, 30d, 90d, 1y | 7d |
| `include` | overview, trends, alerts, top_sites | all |

**Response:** `200 OK`
```json
{
  "period": {
    "start_date": "2024-01-08",
    "end_date": "2024-01-15",
    "range_days": 7
  },
  "overview": {
    "total_sites": 1234,
    "sites_new": 45,
    "sites_ready": 892,
    "sites_in_review": 234,
    "sites_failed": 68
  },
  "discovery_metrics": {
    "total_discoveries": 156,
    "successful_discoveries": 142,
    "success_rate": 0.91,
    "avg_discovery_time_seconds": 823,
    "avg_cost_usd": 1.32
  },
  "site_distribution": {
    "by_platform": {
      "shopify": 512,
      "magento": 234,
      "woocommerce": 156,
      "custom": 332
    },
    "by_method": {
      "static": 756,
      "browser": 342,
      "api": 136
    }
  },
  "quality_metrics": {
    "avg_blueprint_confidence": 0.88,
    "selector_failure_rate": 0.12,
    "categories_average": 48,
    "endpoints_average": 6.2
  },
  "trends": [
    {
      "metric": "discovery_success_rate",
      "trend": "improving",
      "change_percent": 3.2,
      "data_points": [0.85, 0.86, 0.87, 0.88, 0.89, 0.89, 0.91]
    },
    {
      "metric": "avg_discovery_time",
      "trend": "improving",
      "change_percent": -8.5,
      "data_points": [920, 910, 890, 870, 850, 840, 823]
    }
  ],
  "alerts": [
    {
      "severity": "warning",
      "message": "Selector failure rate increased to 12% (was 9%)",
      "action": "Review recent LLM changes"
    },
    {
      "severity": "info",
      "message": "Queue depth < 5 jobs, system healthy"
    }
  ]
}
```

---

### 5.2 Site Metrics

**GET** `/api/v1/analytics/sites/{site_id}`

Detailed metrics for a specific site.

**Query Parameters:**
```
?start_date=2024-01-01&end_date=2024-01-15&metrics=discovery_time,selector_failures,cost
```

**Response:** `200 OK`
```json
{
  "site_id": "123e4567-e89b-12d3-a456-426614174000",
  "domain": "example.com",
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-15"
  },
  "summary": {
    "discovery_count": 4,
    "last_discovery": "2024-01-15T10:30:00Z",
    "avg_discovery_time_seconds": 890,
    "total_cost_usd": 5.28,
    "selector_failure_count": 3,
    "selector_failure_rate": 0.08
  },
  "timeline": [
    {
      "date": "2024-01-01",
      "discovery_time": 920,
      "selector_failures": 0,
      "cost_usd": 1.20
    },
    {
      "date": "2024-01-08",
      "discovery_time": 890,
      "selector_failures": 1,
      "cost_usd": 1.32
    },
    {
      "date": "2024-01-15",
      "discovery_time": 850,
      "selector_failures": 0,
      "cost_usd": 1.44
    }
  ],
  "trend_analysis": {
    "discovery_time_trend": "improving",
    "efficiency_score": 0.87,
    "recommendation": "Site is optimizing well. Consider for template creation."
  }
}
```

---

### 5.3 Method Performance

**GET** `/api/v1/analytics/methods/performance`

Compare discovery method effectiveness across platforms.

**Query Parameters:**
```
?groupby=platform,method&start_date=2024-01-01&end_date=2024-01-15
```

**Response:** `200 OK`
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-15"
  },
  "method_performance": [
    {
      "method": "static",
      "total_jobs": 150,
      "success_count": 142,
      "success_rate": 0.947,
      "avg_time_seconds": 45,
      "avg_cost_usd": 0.15,
      "avg_blueprint_confidence": 0.85
    },
    {
      "method": "browser",
      "total_jobs": 45,
      "success_count": 43,
      "success_rate": 0.956,
      "avg_time_seconds": 180,
      "avg_cost_usd": 0.45,
      "avg_blueprint_confidence": 0.92
    },
    {
      "method": "api",
      "total_jobs": 12,
      "success_count": 10,
      "success_rate": 0.833,
      "avg_time_seconds": 60,
      "avg_cost_usd": 0.25,
      "avg_blueprint_confidence": 0.88
    }
  ],
  "by_platform": {
    "shopify": {
      "static": { "success_rate": 0.95, "avg_cost": 0.10 },
      "browser": { "success_rate": 0.97, "avg_cost": 0.40 }
    },
    "magento": {
      "static": { "success_rate": 0.92, "avg_cost": 0.15 },
      "browser": { "success_rate": 0.96, "avg_cost": 0.50 }
    }
  },
  "recommendations": [
    "Use static method for Shopify sites (95% success, lower cost)",
    "Browser method significantly improves confidence (0.92 vs 0.85)"
  ]
}
```

---

### 5.4 Selector Performance

**GET** `/api/v1/analytics/selectors/performance`

Track selector reliability and lifetime.

**Query Parameters:**
```
?metric_type=failure_rate,lifetime&order_by=-failure_rate&limit=50
```

**Response:** `200 OK`
```json
{
  "selectors": [
    {
      "selector_id": "sel-001",
      "field_name": "title",
      "site_id": "site-001",
      "domain": "example.com",
      "generation_method": "llm",
      "created_at": "2024-01-10T10:00:00Z",
      "css_selector": ".product-title",
      "test_pass_rate": 0.98,
      "failure_count": 2,
      "failure_rate": 0.02,
      "days_alive": 5,
      "reliability_score": 0.95,
      "status": "healthy"
    },
    {
      "selector_id": "sel-002",
      "field_name": "price",
      "site_id": "site-002",
      "generation_method": "heuristic",
      "test_pass_rate": 0.65,
      "failure_rate": 0.35,
      "days_alive": 3,
      "reliability_score": 0.60,
      "status": "at_risk",
      "recommendation": "Re-generate with LLM"
    }
  ],
  "summary": {
    "total_selectors": 2847,
    "avg_failure_rate": 0.08,
    "avg_lifetime_days": 28,
    "llm_generated_avg_reliability": 0.92,
    "heuristic_generated_avg_reliability": 0.78
  }
}
```

---

### 5.5 Export Report

**POST** `/api/v1/analytics/export`

Generate and download a complete analytics report.

**Request:**
```json
{
  "report_type": "monthly",
  "format": "pdf",
  "metrics": ["discovery_metrics", "method_comparison", "top_sites", "trends"],
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**Response:** `200 OK` with `Content-Type: application/pdf`
```
Binary PDF file download
```

---

## 6. HEALTH & MONITORING ENDPOINTS

### 6.1 System Health

**GET** `/health`

Check system status (no authentication required).

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T15:30:00Z",
  "services": {
    "database": "up",
    "cache": "up",
    "queue": "up",
    "llm_service": "up"
  },
  "queue_depth": 42,
  "active_workers": 8
}
```

---

### 6.2 Metrics (Prometheus)

**GET** `/metrics`

Prometheus-format metrics for monitoring.

**Response:** `200 OK` (text/plain)
```
# HELP jobs_submitted_total Total jobs submitted
# TYPE jobs_submitted_total counter
jobs_submitted_total 12345

# HELP job_duration_seconds Job execution time
# TYPE job_duration_seconds histogram
job_duration_seconds_bucket{le="10",job_type="fingerprint"} 892
job_duration_seconds_bucket{le="60",job_type="fingerprint"} 1203
...
```

---

## 7. ERROR RESPONSES

All error responses follow this format:

```json
{
  "error": {
    "code": "ERR_CODE",
    "message": "Human-readable message",
    "details": {
      "field": "specific_error_details"
    },
    "request_id": "req-uuid",
    "timestamp": "2024-01-15T15:30:00Z"
  }
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `204` | No Content |
| `400` | Bad Request |
| `401` | Unauthorized |
| `403` | Forbidden |
| `404` | Not Found |
| `409` | Conflict |
| `429` | Too Many Requests |
| `500` | Internal Server Error |
| `502` | Bad Gateway |
| `503` | Service Unavailable |

---

## 8. PAGINATION

All list endpoints support pagination:

**Query Parameters:**
```
?limit=50&offset=0
?limit=50&page=1  (alternative)
```

**Response Headers:**
```
X-Total-Count: 1234
X-Limit: 50
X-Offset: 0
Link: <https://api.example.com/v1/sites?limit=50&offset=50>; rel="next"
```

---

## 9. RATE LIMITING

**Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 2024-01-15T16:00:00Z
```

**Rate Limits by Endpoint:**
- Discovery endpoints: 100 req/minute
- Read endpoints: 1000 req/minute
- Write endpoints: 100 req/minute

---

## 10. WEBHOOKS (Optional Future)

Systems can subscribe to events:

```
POST /api/v1/webhooks
Body: {
  "events": ["job.completed", "site.discovered", "blueprint.updated"],
  "url": "https://external.com/webhook",
  "secret": "webhook_secret"
}
```

Events would be POSTed to the registered URL with HMAC signature.


