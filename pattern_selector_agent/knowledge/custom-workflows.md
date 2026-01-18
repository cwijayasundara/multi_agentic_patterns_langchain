---
name: custom-workflows
title: Custom Workflows (StateGraph)
description: StateGraph with custom node sequences, conditional edges, and feedback loops
category: workflow
complexity: variable
---

## When to Use

- Workflow doesn't fit standard patterns
- Need custom node sequences (A -> B -> C)
- Conditional branching based on state
- Feedback loops with quality gates (write -> review -> revise)
- Complex state transformations between nodes
- Full control over execution flow

## When NOT to Use

- Standard patterns cover your needs
- Simple linear flows (use **Handoffs**)
- Just need agent coordination (use **Subagents**)
- Parallelization is the main concern (use **Router**)

## Key Characteristics

| Capability | Rating |
|------------|--------|
| Flexibility | Very High |
| Custom Logic | Very High |
| Feedback Loops | High |
| Learning Curve | Medium |
| Debugging Complexity | Medium |

## Decision Triggers

Ask yourself these questions:

1. "Does no standard pattern fit your workflow?" -> HIGH fit if yes
2. "Do you need conditional branching in the workflow?" -> HIGH fit if yes
3. "Are there quality gates with revision loops?" -> HIGH fit if yes
4. "Do you need full control over execution flow?" -> HIGH fit if yes

## Example Use Cases

- **Content Pipeline**:
  ```
  research -> outline -> write -> review
                                    |
                          [pass?]--+--[fail?]
                            |           |
                          publish     revise -> review
  ```

- **Code Generation**:
  ```
  spec -> generate -> test
                        |
              [pass?]--+--[fail?]
                |           |
              deploy      fix -> test
  ```

- **Document Processing**:
  ```
  extract -> validate -> transform -> load
                |
        [invalid?]
                |
            clean -> validate
  ```

- **Approval Workflow**:
  ```
  submit -> review -> [approve?] -> finalize
                |
          [reject?]
                |
            revise -> submit
  ```

## Trade-offs

**Pros:**
- Ultimate flexibility
- Can model any workflow
- Conditional logic and loops
- Fine-grained state control
- Visual graph representation

**Cons:**
- More setup code required
- Must handle all edge cases
- Testing can be complex
- May reinvent existing patterns

## Architecture Pattern

```
          START
            |
        +---+---+
        |       |
     Node A   Node B (conditional)
        |       |
        +---+---+
            |
         Node C
            |
      [condition]
       /       \
    Node D   Node E (loop back)
      |         |
    END      Node C
```

## Code Reference

See: `examples/custom_workflow_content_pipeline.py`

## Key APIs

- `StateGraph` for workflow definition
- `add_node()` for adding processing nodes
- `add_edge()` for linear connections
- `add_conditional_edges()` for branching
- Node functions receive and return state
- `START` and `END` constants for entry/exit
