# Operations & Monitoring

## 1. Job Orchestration
- Job types: Fingerprint, Discovery, Extraction, Blueprint Update.  
- Queueing system: each job submitted into priority queue; worker picks up by method.  
- Retry policy: 3 attempts max, then escalate to human review or dead-letter queue.  
- Rate limiting: per-site host delay, global concurrency cap, proxy reuse delay.

## 2. Monitoring Metrics
- Jobs/hour, avg time/job, jobs pending in queue.  
- Failure rate by cause (timeout, blocked, JS error, selector missing).  
- Selector failure rate (per site, per selector).  
- Site churn rate (how often blueprint changes).  
- Proxy pool metrics: used, failed, blacklisted.  
- Dashboards for SLA: average time to first blueprint, backlog size.

## 3. Alerting & Automated Escalation
- Alert if failure rate > X% for a site group for > Y minutes.  
- Alert if queue depth > threshold.  
- Automatic pause on a site if it appears blocked (403s, CAPTCHAs) — trigger review.  
- Weekly health report: top failing sites, top method cost by site.

## 4. Maintenance & Updates
- Template library review every month.  
- Selector robustness audit: identify top 10 sites with frequent breaks.  
- Proxy health audit monthly.  
- LLM prompt audit quarterly: review failed cases and refine prompts.

## 5. Logging & Audit Trails
- Central log service (ELK/Stackdriver) with structured logs: job_id, site_id, method, worker_id, duration, result, error.  
- Audit log for blueprint changes: who/what/when.  
- Data retention policy: raw HTML and logs archived after 90 days (or per compliance).  

## 6. Incident Response
- Define incident classification (major/minor).  
- Runbooks: e.g., “selector break” incident — isolate site, revert blueprint, schedule update, notify ops.  
- Post-mortem process after major failures.

