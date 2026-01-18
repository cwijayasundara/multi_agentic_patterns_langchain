---
name: supervisor-forward
title: Supervisor with Forward Tool
description: Supervisor forwards subagent responses verbatim to users without modification
category: multi-agent
complexity: medium
---

## When to Use

- Exact wording of responses matters (legal, medical, financial)
- You need clear attribution of which agent provided the response
- Liability concerns require verbatim forwarding
- Audit trails must show original responses unchanged
- Supervisor should not paraphrase or summarize specialist output
- Regulated industries with compliance requirements

## When NOT to Use

- Supervisor should synthesize or improve responses
- Attribution is not important
- Responses benefit from supervisor's additional context
- You need the supervisor to add commentary or explanations

## Key Characteristics

| Capability | Rating |
|------------|--------|
| Response Accuracy | Very High |
| Attribution | Very High |
| Audit Trail | Very High |
| Response Customization | Low |
| Supervisor Synthesis | Low |

## Decision Triggers

Ask yourself these questions:

1. "Does exact wording matter for compliance or legal reasons?" -> HIGH fit if yes
2. "Do you need clear attribution of which specialist responded?" -> HIGH fit if yes
3. "Would paraphrasing introduce liability risks?" -> HIGH fit if yes
4. "Is there a regulatory requirement for unchanged responses?" -> HIGH fit if yes

## Example Use Cases

- **Legal Services**: Legal expert's response forwarded exactly as written
- **Medical Information**: Medical specialist's advice delivered verbatim
- **Financial Advisory**: Investment recommendations preserved exactly
- **Compliance Queries**: Regulatory specialist's responses unchanged
- **Expert Systems**: Where expert authority must be preserved

## Trade-offs

**Pros:**
- No risk of paraphrasing errors or misinterpretation
- Clear accountability for each response
- Perfect audit trail for compliance
- Preserves specialist expertise exactly

**Cons:**
- Supervisor cannot add context or improve responses
- Responses may lack conversational polish
- No synthesis of multiple specialist inputs
- User may notice different response styles

## Architecture Pattern

```
User <-> Supervisor Agent
              |
         [forward tool]
              |
         Subagent (specialist)
              |
         Response forwarded verbatim
```

## Code Reference

See: `examples/supervisor_forward_tool.py`

## Key APIs

- `create_react_agent()` for supervisor
- Forward tools that pass responses unchanged
- No post-processing of subagent outputs
