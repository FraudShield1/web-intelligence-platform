
Purpose: Defines how you’ll use LLMs (and heuristics) in the pipeline: prompt templates, evaluation and feedback loops, data labeling strategy.
Template:

# LLM & Prompt Strategy

## 1. Use Cases for LLM
- Generating CSS/XPath selectors for category links, listing fields.  
- Normalizing category names and generating slugs.  
- Interpreting network traces to propose endpoint URLs & params.  
- Generating natural-language metadata (notes, confidence explanation).  

## 2. Prompt Templates
### Prompt Template A: “Extract category links”


You are an assistant that, given HTML of a web page and the base URL, identify all category links.
Input:
{
"base_url": "<url>",
"html": "<full html>"
}
Output JSON:
{
"categories": [
{ "name": "...", "url": "...", "selector": "...", "confidence": 0.0-1.0 }
],
"notes": "..."
}


### Prompt Template B: “Synthesize selectors for listing fields”


Input:
{
"html": "<listing page html>",
"field_examples": ["price", "title", "image_url"]
}
Output:
{
"selectors": {
"price": {"css": "...", "xpath": "...", "confidence": 0.0-1.0},
"title": {...},
...
},
"notes": "..."
}


### Prompt Template C: “Interpret network logs and propose API endpoints”


Input:
{
"network_requests": [ { "url": "...", "method": "...", "response": "{…}" } , ... ],
"base_url": "<url>"
}
Output:
{
"endpoints": [
{
"url": "...",
"method": "...",
"params": {...},
"example_response_schema": {...},
"confidence": 0.0-1.0
}
],
"notes": "..."
}


## 3. Evaluation & Feedback Loop
- Automatically calculate confidence scores; human review anything below a threshold (e.g., < 0.8).  
- Feed human-review labels back into LLM fine-tuning or prompt refinement.  
- Keep track of selector failure rate (when scrapers break) by selector origin (LLM-generated vs heuristic) to determine if prompt needs improvement.

## 4. Data Labeling Strategy
- Create a “label queue” for ambiguous cases flagged by the system.  
- Label schema: HTML snapshot + expected selector(s) + category names + endpoint info.  
- Use these to train a classifier for “category vs non-category link” and refine prompts.

## 5. Ethical & Usage Considerations
- Track usage of LLM calls (cost + latency).  
- Limit high-cost calls to high-value or low-confidence sites.  
- Log prompt-response pairs for audit & improvement (but mask sensitive data).

