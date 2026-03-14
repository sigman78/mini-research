# M6: LangGraph Orchestration

## Goal

Wire all pipeline components (agents, search/scrape, state, memory) into a LangGraph evaluation loop. The orchestrator will coordinate multi-agent workflows and route control flow based on coverage evaluation.

## Key Components

### LangGraph StateGraph
- Manages state transitions and data flow through pipeline
- Typed with `ResearchState` to ensure type safety across nodes
- Implicit state passing between nodes

### Pipeline Nodes
1. **plan_node** - Enriches user query, generates 3-5 sub-queries, composes research plan
2. **gather_node** - Executes searches and scrapes; extracts facts; builds working memory with citations
3. **evaluate_node** - Checks fact coverage and query satisfaction; sets `coverage_sufficient` flag
4. **report_node** - Drafts final Markdown report with inline citations

### Conditional Routing
- After evaluate_node, route based on `coverage_sufficient` flag
- If insufficient: loop back to plan_node (max 3 iterations to prevent infinite loops)
- If sufficient: proceed to report_node and END
- Iteration count tracked to enforce `max_research_iterations` limit

## Graph Flow

```
START
  ↓
plan_node
  ↓
gather_node
  ↓
evaluate_node
  ↓
  ├─→ [coverage_sufficient == False && iterations < max] → plan_node (loop)
  │
  └─→ [coverage_sufficient == True || iterations >= max] → report_node
                                                            ↓
                                                           END
```

## Test Strategy

### Tool-Layer Unit Tests
- Mock LLM calls and API responses
- Test search/scrape providers independently (DuckDuckGo, Brave, Reddit, trafilatura, etc.)
- Verify fact extraction and parsing logic
- Use VCR.py to record/replay HTTP interactions for deterministic tests

### Graph-Node Unit Tests
- Test each node function independently with synthetic state inputs
- Mock upstream dependencies (search, scrape, LLM calls)
- Verify output state mutations and data transformations
- Test routing decisions (conditional edge logic)

### Full Pipeline Integration Tests
- End-to-end flow with mocked external services (LLM, search, scrape)
- Verify state evolves correctly through all nodes
- Test loop termination conditions (coverage met, iteration limit)
- Capture and replay agent traces for reproducibility
