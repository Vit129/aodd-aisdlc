# Graph Summary — aodd-aisdlc
_Auto-generated from GRAPH_REPORT.md · do not edit manually_
_Regen: `graphify update .`_

## Summary
- 2533 nodes · 2774 edges · 261 communities (226 shown, 35 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output


## Graph Freshness
- Built from commit: `3a7bb429`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).


## God Nodes (most connected - your core abstractions)
1. `Fix Generated Playwright Files (Postman Migration)` - 33 edges
2. `Changelog` - 22 edges
3. `UX/UI Designer` - 20 edges
4. `Browser Automation with playwright-cli` - 16 edges
5. `Frontend Development` - 15 edges
6. `state()` - 14 edges
7. `aodd-aisdlc` - 14 edges
8. `AI-SDLC Progress Spec — Task Breakdown & Progress Tracking` - 14 edges
9. `main()` - 13 edges
10. `Coding Principles` - 13 edges


## Cross-Cutting Nodes (span the most distinct areas of the codebase)
A high-degree node isn't always architecturally central - a widely-used
utility/config file can rack up more edges than a real coupler while only
ever touching one area. This ranks by how many DIFFERENT communities a
node's neighbors span, not by raw edge count.
1. `Changelog` - bridges 15 areas (22 edges)
2. `state()` - bridges 9 areas (14 edges)
3. `aodd-aisdlc` - bridges 3 areas (14 edges)
4. `claude_home()` - bridges 3 areas (9 edges)
5. `Storage Management` - bridges 3 areas (8 edges)
6. `main()` - bridges 2 areas (13 edges)
7. `search()` - bridges 2 areas (10 edges)
8. `generate_design_system()` - bridges 2 areas (8 edges)
9. `session_id()` - bridges 2 areas (6 edges)

## Surprising Connections (you probably didn't know these)
- `write_report()` --calls--> `reports()`  [EXTRACTED]
  optional/schedules/scripts/aodd_job.py → hooks/_aodd_paths.py
- `unseen_hits()` --calls--> `state()`  [EXTRACTED]
  optional/agent-memory/hooks/memory-recall.py → hooks/_aodd_paths.py
- `first_time()` --calls--> `state()`  [EXTRACTED]
  optional/agent-memory/hooks/memory-write-scan.py → hooks/_aodd_paths.py
- `main()` --calls--> `state()`  [EXTRACTED]
  optional/agent-memory/hooks/session-start-recent.py → hooks/_aodd_paths.py
- `housekeeping_scan()` --calls--> `state()`  [EXTRACTED]
  optional/schedules/scripts/aodd_job.py → hooks/_aodd_paths.py


_Full map → GRAPH_REPORT.md · query: `graphify query "..."`_
