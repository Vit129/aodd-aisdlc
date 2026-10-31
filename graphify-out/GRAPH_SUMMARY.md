# Graph Summary — delivery-workflow-completion
_Auto-generated from GRAPH_REPORT.md · do not edit manually_
_Regen: `graphify update .`_

## Summary
- 2399 nodes · 2567 edges · 226 communities (201 shown, 25 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output


## Graph Freshness
- Built from commit: `77084625`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).


## God Nodes (most connected - your core abstractions)
1. `Fix Generated Playwright Files (Postman Migration)` - 33 edges
2. `UX/UI Designer` - 21 edges
3. `Browser Automation with playwright-cli` - 17 edges
4. `Changelog` - 16 edges
5. `Frontend Development` - 16 edges
6. `AI-SDLC Progress Spec — Task Breakdown & Progress Tracking` - 15 edges
7. `aodd-aisdlc` - 14 edges
8. `main()` - 13 edges
9. `Coding Principles` - 13 edges
10. `Running Custom Playwright Code` - 13 edges


## Cross-Cutting Nodes (span the most distinct areas of the codebase)
A high-degree node isn't always architecturally central - a widely-used
utility/config file can rack up more edges than a real coupler while only
ever touching one area. This ranks by how many DIFFERENT communities a
node's neighbors span, not by raw edge count.
1. `search()` - bridges 2 areas (10 edges)
2. `generate_design_system()` - bridges 2 areas (8 edges)
3. `Tracing` - bridges 2 areas (8 edges)
4. `_resolve_color_mode()` - bridges 2 areas (5 edges)
5. `_select_palette_for_mode()` - bridges 2 areas (4 edges)
6. `Browser Automation with playwright-cli` - bridges 1 areas (17 edges)
7. `Running Custom Playwright Code` - bridges 1 areas (13 edges)
8. `main()` - bridges 1 areas (11 edges)
9. `DesignSystemGenerator` - bridges 1 areas (11 edges)

## Surprising Connections (you probably didn't know these)
- `candidates()` --calls--> `memory_dirs()`  [EXTRACTED]
  optional/agent-memory/hooks/memory-recall.py → hooks/_aodd_paths.py
- `candidates()` --calls--> `project()`  [EXTRACTED]
  optional/agent-memory/hooks/memory-recall.py → hooks/_aodd_paths.py
- `main()` --calls--> `session_id()`  [EXTRACTED]
  scripts/audit.py → hooks/_aodd_paths.py
- `main()` --calls--> `reports()`  [EXTRACTED]
  optional/agent-memory/hooks/session-start-recent.py → hooks/_aodd_paths.py
- `write_report()` --calls--> `reports()`  [EXTRACTED]
  optional/schedules/scripts/aodd_job.py → hooks/_aodd_paths.py


_Full map → GRAPH_REPORT.md · query: `graphify query "..."`_
