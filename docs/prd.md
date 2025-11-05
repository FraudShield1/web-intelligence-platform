# Project Requirements Document (PRD)

## 1. Project Overview
- Name: “Web Intelligence Platform” (temporary)  
- Purpose: Automatically discover, score, and prepare extraction surfaces for websites so scrapers can run reliably at scale.  
- Stakeholders: [Your name/company], Data & Analytics team, Scraper engineering team, Operations, BD/sales team.

## 2. Objectives & Success Metrics
- Objective A: Discover category trees for ≥ 90% of new e-commerce sites within 30 min.  
- Objective B: Achieve selector robustness median lifetime ≥ 30 days.  
- Objective C: Prioritize high-ROI sites reducing manual effort by 80%.  
- Key metrics: Discovery recall/precision, throughput (items/minute), cost per item, site prioritization accuracy.

## 3. User Personas & Use Cases
- Persona 1: Scraper Ops Lead — uploads a new site URL, views blueprint, triggers scraper.  
- Persona 2: Data Analyst — reviews dashboards to choose next sites.  
- Persona 3: Business/Sales Lead — reviews pipeline of new sites and value estimates.

Use Cases:
- UC1: “Add new site” → system fetches sitemap, runs discovery, produces site blueprint.  
- UC2: “View existing sites” → filter by score, status, platform.  
- UC3: “Dashboard” → show health, throughput, failures, value.  
- UC4: “Export blueprint” → generate files for downstream scraper pipeline.

## 4. Features
- Feature A: Site fingerprinting module (tech detection, sitemap, nav).  
- Feature B: Selector/endpoint extraction engine with LLM-assisted synthesis.  
- Feature C: Scoring engine for site prioritization.  
- Feature D: Dashboard for operations, data analytics, business view.  
- Feature E: Blueprint export service (categories.json, endpoints.json, render_hints.json).  
- Feature F: Template library management for common platforms.

## 5. Non-functional Requirements
- Scalability: Should support 10,000+ sites/month, concurrent discovery processes.  
- Robustness: Automatic recovery from failures, logging, monitoring.  
- Maintainability: Modular architecture, plug-in selectors, versioning of templates.  
- Security & Compliance: Respect robots.txt, handle proxy rotation, no protected data scraping.  
- Performance: Average time to first blueprint ≤ 30 minutes for standard sites.  
- Availability: Dashboard should have 99.9% uptime; discovery jobs have retry mechanism.

## 6. Constraints & Assumptions
- Constraint: Some sites will use CAPTCHAs or heavy JS — may fallback to human review.  
- Assumption: Using Cursor + an LLM backend + headless browser service.  
- Assumption: We have proxy infrastructure and rotate IPs for scale.

## 7. Success Criteria & Milestones
- Milestone 1: Minimum-viable pipeline working for 5 platforms in 4 weeks.  
- Milestone 2: Dashboard MVP showing discovery results & site scoring in 8 weeks.  
- Milestone 3: Automated blueprint export integrated with scraper engine in 12 weeks.  
- Milestone 4: 100 sites processed end-to-end, metrics tracked and improved in 16 weeks.

## 8. Risks & Mitigations
- Risk: Site structure heavily obfuscated → Mitigation: escalate to human review + visual extraction.  
- Risk: LLM generated selectors unstable → Mitigation: selector lifetime monitoring, fallback.  
- Risk: Proxy/IP block → Mitigation: rotate proxies, monitor failure spikes, throttle by site.

