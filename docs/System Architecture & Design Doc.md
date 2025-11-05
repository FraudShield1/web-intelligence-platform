# System Architecture & Design

## 1. System Overview
Describe the system’s major modules: Discovery Engine, Selector Synthesizer, Blueprint Store, Dashboard/BI Layer, Scraper Integration.

## 2. Component Diagram
- Fingerprinting Service  
- Discovery Orchestrator  
- Browser + Network Trace Worker  
- Static HTTP Crawler Worker  
- Selector/Endpoint Extractor (LLM + rule engine)  
- Confidence & Scoring Engine  
- Blueprint Storage (metadata DB + file-store)  
- Template Repository  
- Scheduler & Queue (job queue, prioritization)  
- Dashboard Front-End + API Layer  
- Analytics/ML Layer (model training, monitoring)  
- Proxy/Fetcher Infrastructure  
- Logging/Monitoring stack

## 3. Data Flow
1. User submits domain → Fingerprinter  
2. Discovery Orchestrator chooses method → runs crawler/worker  
3. Raw data (HTML, network logs) stored → Extractor generates blueprint  
4. Blueprint stored → Scoring engine assigns site priority  
5. Dashboard fetches site metadata & metrics  
6. Scraper engine consumes blueprint to start data extraction  
7. Analytics module collects performance data, feeds ML/retraining.

## 4. Technology Stack (suggested)
- Backend: Python/Go/Kotlin microservices  
- Queue: RabbitMQ / Kafka  
- Browser automation: Playwright / Puppeteer cluster  
- Storage: PostgreSQL for metadata, S3 (or object store) for raw logs & blueprints  
- Front-end: React/Vue + dashboard UI  
- Monitoring: Prometheus + Grafana  
- ML/LLM: Use an LLM API + fine-tuning; embeddings with e.g. OpenAI/Rocket-models  
- Containerization: Docker + Kubernetes for scale

## 5. Scaling & Performance Considerations
- Worker autoscaling based on queue depth  
- Proxy pool size & regional IP allocation  
- Rate-limiting per domain, exponential back-off  
- Cache reuse of templates & selectors for known platforms  
- Batch processing and parallelization of discovery jobs  
- Versioning of blueprints to allow roll-back

## 6. Security & Compliance
- Secure LLM credentials, encryption at rest, IAM for blueprint files  
- Respect robots.txt and site-terms by default, opt-out mechanism  
- Logging of sensitive events, audit trail  
- Proxy IP hygiene (no blacklisted proxies)  
- TLS everywhere for dashboard/API

## 7. Open Interfaces / API Specifications
- `POST /site` → submit domain, returns job ID  
- `GET /site/{id}` → retrieve site metadata & blueprint link  
- `GET /site/{id}/dashboard` → site-specific metrics  
- `GET /blueprint/{id}` → download JSON schema

## 8. Error Handling & Retry Strategy
- Worker retry limits (e.g., 3 retries with back-off)  
- Fallback to alternate method if primary fails (static → browser)  
- Escalation queue if human review required  
- Dead-letter queue for unrecoverable failures  

## 9. Logging, Monitoring & Alerting
- Job status logs (enqueue, start, success/fail)  
- Metric dashboards: jobs per hour, failures by cause, average time to blueprint  
- Alert on unusual failure spikes, timeouts, proxy exhaustion  
- Regular reports: selector failure rate per site, site churn alerts  

## 10. Deployment & DevOps
- CI/CD pipeline for backend, front-end, template repo  
- Canary roll-out of material changes (selector logic, LLM prompts)  
- Versioning blueprints and tracking changes with Git & DB migrations  
- Disaster recovery: backup metadata, raw logs, blueprint store

