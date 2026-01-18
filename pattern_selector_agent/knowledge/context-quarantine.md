---
name: context-quarantine
title: Context Quarantine
description: Subagents isolate large tool outputs from main agent context through summarization
category: multi-agent
complexity: medium
---

## When to Use

- Tool outputs are very large (10K+ tokens)
- Main agent needs sustained reasoning over many turns
- Raw data would degrade main agent's performance
- Only summaries of large data are needed for decisions
- Processing large datasets, documents, or API responses
- Context efficiency is critical for long conversations

## When NOT to Use

- Tool outputs are small (a few hundred tokens)
- Raw data is needed for detailed analysis
- You need to reference specific details from tool outputs
- Short conversations where context isn't a concern

## Key Characteristics

| Capability | Rating |
|------------|--------|
| Context Efficiency | Very High |
| Large Data Processing | Very High |
| Detail Preservation | Low |
| Sustained Reasoning | Very High |
| Setup Complexity | Medium |

## Decision Triggers

Ask yourself these questions:

1. "Are tool outputs typically large (10K+ tokens)?" -> HIGH fit if yes
2. "Does the main agent need to reason over many conversation turns?" -> HIGH fit if yes
3. "Can summaries replace raw data for decision-making?" -> HIGH fit if yes
4. "Would raw data clutter the main conversation context?" -> HIGH fit if yes

## Example Use Cases

- **Database Queries**: Query returns 10,000 rows -> Summarize key statistics
- **Document Analysis**: 100-page document -> Extract key points
- **API Integration**: Large JSON response -> Summarize relevant fields
- **Log Analysis**: 50MB of logs -> Summarize error patterns
- **Code Review**: Entire repository -> Summarize architecture

## Trade-offs

**Pros:**
- Prevents context bloat from large outputs
- Main agent maintains coherent reasoning
- Dramatically reduces token usage
- Enables processing of arbitrary data sizes

**Cons:**
- Summaries may lose important details
- Cannot reference specific raw data later
- Requires careful summary prompts
- Extra processing step for each large output

## Architecture Pattern

```
User <-> Main Agent (clean context)
              |
         Quarantine Subagent
              |
         [large tool call]
              |
         ~100K tokens raw data
              |
         Summarization
              |
         ~500 tokens summary
              |
         Main Agent receives summary only
```

## Code Reference

See: `examples/context_quarantine.py`

## Key APIs

- `StateGraph` for workflow definition
- Quarantine subagents with summarization
- `SummarizationMiddleware` for context compression
- Strategic context clearing
