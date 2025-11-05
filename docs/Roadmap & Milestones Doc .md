# Roadmap & Milestones

## Phase 0 – Foundations (Weeks 0-4)
- Task: Build fingerprinter service & sitemap/nav crawler  
- Task: Setup metadata DB + blueprint store  
- Task: Build “Add site and view status” UI (minimal)  
- Milestone: Submit 10 pilot sites manually and produce blueprints  
- Responsible: Platform & Ops team  

## Phase 1 – Scale & Quality (Weeks 5-12)
- Task: Integrate headless browser worker + network trace capture  
- Task: Build selector/endpoint extractor (LLM + rules)  
- Task: Dashboard MVP (overview + site list)  
- Task: Metrics collection pipeline (jobs, failures, time)  
- Milestone: 100 sites processed end-to-end, basic metrics captured  
- Responsible: Platform + Data Engineers  

## Phase 2 – Intelligence & Automation (Weeks 13-24)
- Task: Build scoring engine (complexity + business value)  
- Task: Build template library and reuse logic for 5 platforms  
- Task: Build analytics dashboards (method performance, ROI)  
- Task: Active-learning workflow (human review integration)  
- Milestone: ≥ 80% of new sites processed automatically without human review; cost per item reduced by 50%  
- Responsible: ML/NLP + Data Science + Platform  

## Phase 3 – Optimization & Business Integration (Weeks 25-52)
- Task: Selector survival model + churn forecasting  
- Task: Visual extraction module (for obfuscated sites)  
- Task: Self-healing scrapers (auto-regenerate selectors on failure)  
- Task: Business-ROI integration (scraper output → reselling value pipeline)  
- Milestone: Platform processes 10,000 sites/month; dashboards fully operational; autonomous prioritization in place.  
- Responsible: All teams  

## Dependencies & Risks
- Need proxy infrastructure and budget by Week 2 (risk: delay).  
- LLM API quota & cost must be capped and monitored.  
- Human review capacity needed from Week 5 onward.  
- Regulatory review: ensure compliance with scraping/terms by Week 4.

## Review Cadence
- Weekly stand-up on progress vs tasks.  
- Monthly milestone review with stakeholders.  
- Quarterly business-impact review (cost vs value, platform ROI).  

