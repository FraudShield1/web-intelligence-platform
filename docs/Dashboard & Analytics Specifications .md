# Dashboard & Analytics Specifications

## 1. Audience & Key Use Cases
### Audience:
- Executive (C-level, BD): high-level overview, strategic decisions  
- Product / Ops Lead: site prioritization, method tuning  
- Scraper Engineer: site health, blueprint versioning  
- Data Analyst: method performance, selector lifetime, ROI  

### Use Cases:
- “Which sites should we focus on next?”  
- “Why did scraper yield drop on Site X?”  
- “How is our selector robustness trending?”  
- “What’s our cost per item and how is it changing?”  

## 2. Metrics Catalogue
- **Sites processed** (count, trend)  
- **Discovery recall/precision** (for sampled sites)  
- **Selector lifetime** (median days)  
- **Fetch cost per 1k items** (USD)  
- **Jobs per hour / backlog size**  
- **Failure rate** (overall & by cause)  
- **Site churn rate** (blueprint changes per site/month)  
- **Business value pipeline** (sum of site scores, top 10)  
- **Method yield matrix** (method × platform × cost/yield)  
- **ROI per site** (value estimate ÷ cost)  
- **Automation rate** (% of sites processed without human review)

## 3. Dashboard Wireframes
### Panel A: Overview
- Top row: total sites, new this week, average discovery time, average cost/item  
- Mid row: pie chart of platform distribution (Shopify, Magento, Custom)  
- Bottom row: heatmap of failure rate by day + backlog gauge

### Panel B: Site Priority
- Table: Site | Score | Platform | Discovery Time | Method recommended | Action button (“Export blueprint” / “Re-scan”)  
- Filters: by score, by status, by platform

### Panel C: Health & Ops
- Trend: selector failure rate over last 30 days  
- Jobs per hour — stacked by status (success/fail)  
- Proxy health: used vs failed vs blocked  
- Alert feed: recent high-failure sites

### Panel D: Analytics & Learning
- Method Performance Matrix: bar chart or heatmap (methods on y-axis, platforms on x-axis, color = cost/yield)  
- Selector Lifetime Distribution: boxplot by generation origin (LLM vs heuristic)  
- Churn forecast: list of sites likely to need re-scan soon

## 4. Data Refresh / SLA
- Real-time: job status, queue depth (update every 1–5 min)  
- Daily aggregate: cost metrics, selector lifetime, site scores (update at midnight)  
- Weekly / Monthly: trend reports, ROI, method experiments (update offline, visible next day)

## 5. Access & Roles
- Role: Admin — full view + site management  
- Role: Product Lead — view dashboards + trigger site scans  
- Role: Scraper Engineer — view site blueprints + logs  
- Role: Viewer — read-only metrics  

