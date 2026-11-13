# Graph Summary — aodd-aisdlc
_Auto-generated from GRAPH_REPORT.md · do not edit manually_
_Regen: `graphify update .`_

## Summary
- 2474 nodes · 2681 edges · 250 communities (222 shown, 28 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output


## Graph Freshness
- Built from commit: `6e0e8317`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).


## God Nodes (most connected - your core abstractions)
1. `Fix Generated Playwright Files (Postman Migration)` - 33 edges
2. `UX/UI Designer` - 20 edges
3. `Changelog` - 17 edges
4. `Browser Automation with playwright-cli` - 16 edges
5. `Frontend Development` - 15 edges
6. `aodd-aisdlc` - 14 edges
7. `AI-SDLC Progress Spec — Task Breakdown & Progress Tracking` - 14 edges
8. `main()` - 13 edges
9. `Coding Principles` - 13 edges
10. `Running Custom Playwright Code` - 13 edges


## Cross-Cutting Nodes (span the most distinct areas of the codebase)
A high-degree node isn't always architecturally central - a widely-used
utility/config file can rack up more edges than a real coupler while only
ever touching one area. This ranks by how many DIFFERENT communities a
node's neighbors span, not by raw edge count.
1. `Changelog` - bridges 10 areas (17 edges)
2. `state()` - bridges 5 areas (10 edges)
3. `claude_home()` - bridges 3 areas (9 edges)
4. `Browser Automation with playwright-cli` - bridges 2 areas (16 edges)
5. `search()` - bridges 2 areas (10 edges)
6. `generate_design_system()` - bridges 2 areas (8 edges)
7. `session_id()` - bridges 2 areas (6 edges)
8. `_resolve_color_mode()` - bridges 2 areas (5 edges)
9. `_select_palette_for_mode()` - bridges 2 areas (4 edges)

## Surprising Connections (you probably didn't know these)
- `write_report()` --calls--> `reports()`  [EXTRACTED]
  optional/schedules/scripts/aodd_job.py → hooks/_aodd_paths.py
- `housekeeping_scan()` --calls--> `state()`  [EXTRACTED]
  optional/schedules/scripts/aodd_job.py → hooks/_aodd_paths.py
- `main()` --calls--> `state()`  [EXTRACTED]
  optional/schedules/scripts/install-schedules.py → hooks/_aodd_paths.py
- `candidates()` --calls--> `memory_dirs()`  [EXTRACTED]
  optional/agent-memory/hooks/memory-recall.py → hooks/_aodd_paths.py
- `job_memory_backup()` --calls--> `memory()`  [EXTRACTED]
  optional/schedules/scripts/aodd_job.py → hooks/_aodd_paths.py


_Full map → GRAPH_REPORT.md · query: `graphify query "..."`_
