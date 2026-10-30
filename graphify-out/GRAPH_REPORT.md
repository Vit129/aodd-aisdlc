# Graph Report - aodd-aisdlc  (2026-10-30)

## Corpus Check
- 237 files · ~171,471 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2361 nodes · 2527 edges · 223 communities (199 shown, 24 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ebd898c1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## God Nodes (most connected - your core abstractions)
1. `Fix Generated Playwright Files (Postman Migration)` - 33 edges
2. `UX/UI Designer` - 21 edges
3. `Browser Automation with playwright-cli` - 17 edges
4. `Frontend Development` - 16 edges
5. `Changelog` - 15 edges
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
2. `Browser Session Management` - bridges 2 areas (10 edges)
3. `generate_design_system()` - bridges 2 areas (8 edges)
4. `_resolve_color_mode()` - bridges 2 areas (5 edges)
5. `_select_palette_for_mode()` - bridges 2 areas (4 edges)
6. `Browser Automation with playwright-cli` - bridges 1 areas (17 edges)
7. `Running Custom Playwright Code` - bridges 1 areas (13 edges)
8. `main()` - bridges 1 areas (11 edges)
9. `DesignSystemGenerator` - bridges 1 areas (11 edges)
10. `Delivery Workflow` - bridges 1 areas (10 edges)

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

## Import Cycles
- None detected.

## Communities (223 total, 24 thin omitted)

### Community 0 - "_aodd_paths.py"
Cohesion: 0.07
Nodes (62): claude_home(), home(), memory(), memory_dirs(), plans(), project(), Path, Where AODD keeps its files. Standard library only; every variable is optional. (+54 more)

### Community 1 - "Fix Generated Playwright Files (Postman Migration)"
Cohesion: 0.04
Nodes (47): 10. Request Body Types 📦, 11. Response Headers 📋, 12. Path Parameters & Query Parameters 🔗, 13. Postman Dynamic Variables 🎲, 14. Folder-level Auth Inheritance 🔐, 15. Folder-level Pre-request Script → beforeAll / beforeEach 🔧, 16. Nested Folders → File Structure 📁, 17. Collection Runner + Data File (Data-Driven) 📊 (+39 more)

### Community 2 - "Changelog"
Cohesion: 0.04
Nodes (46): [0.1.0] - 2026-10-16, [0.2.0] - 2026-10-17, [0.3.0] - 2026-10-17, [0.3.1] - 2026-10-17, [0.3.2] - 2026-10-17, [0.3.3] - 2026-10-17, [0.3.4] - 2026-10-17, [0.3.5] - 2026-10-17 (+38 more)

### Community 3 - "SKILL.md"
Cohesion: 0.05
Nodes (33): Android application artifacts, Choose the remedy from the observed failure, Codex tool approval is separate from REA readiness, Connection and task recovery, Continue through an installed CLI, Repair registration when needed, Evidence, comparison, and verification workflows, JavaScript and Electron application artifacts (+25 more)

### Community 4 - "Cookies"
Cohesion: 0.06
Nodes (35): Advanced: Multiple Cookies or Custom Options, Advanced: Multiple Operations, Authentication State Reuse, Clear All Cookies, Clear All localStorage, Clear sessionStorage, Common Patterns, Cookies (+27 more)

### Community 5 - "UX/UI Designer"
Cohesion: 0.06
Nodes (32): Anti-Patterns (Hard Bans), Color, Command Workflows, Context Gathering (REQUIRED), Conventions, Core Capabilities, Credits, Design Direction (+24 more)

### Community 6 - "aodd-aisdlc"
Cohesion: 0.07
Nodes (26): done-gate behaviour, How the audit works, Codex, Curation, How to write it, Proposals from other agents (evidence gate), Skill capture (self-improving skills), Skill learning: how an agent improves its own skills (+18 more)

### Community 7 - "Finance Industry Rules (21 Rules)"
Cohesion: 0.07
Nodes (29): 10. Accessibility for Vision Impairment, 11. Trust & Security (Navy, Dark Gray), 12. Growth & Gain (Deep Green), 13. Caution & Loss (Dark Red), 14. Traditional Yet Modern, 15. Numbers Are Content, 16. Clear Instructions & Warnings, 17. Subtle Feedback on Input (+21 more)

### Community 8 - "Creative Industry Rules (20 Rules)"
Cohesion: 0.07
Nodes (28): 10. Vibrant High-Energy for Viral/Social Creative Tools, 11. Bold Primaries & Artistic Freedom, 12. Dark Studio + Neon Accents, 13. AI Purple + Aurora Gradients, 14. Bold Expressive Display Type, 15. Minimal/Elegant for Portfolio & Photography, 16. Gaming & Music Impact Type, 17. Parallax & Scroll-Triggered Reveals (+20 more)

### Community 9 - "E-commerce Industry Rules (20 Rules)"
Cohesion: 0.07
Nodes (28): 10. Fast, Smooth Performance, 11. Action & Energy (Orange/Red), 12. Trust & Confidence (Blue), 13. Value & Savings (Green), 14. Product-Focused Clarity, 15. Scannable Product Descriptions, 16. Trust-Building Microcopy, 17. Smooth Cart & Checkout Interactions (+20 more)

### Community 10 - "Emerging Tech Industry Rules (20 Rules)"
Cohesion: 0.07
Nodes (28): 10. Minimal Chrome for AI-Native Interfaces, 11. Neon on Deep Black, 12. AI Purple + Aurora Gradients, 13. Earth Green + Solar Yellow for Climate/Sustainability, 14. Futuristic Monospace/Technical Type, 15. Spatial Clear System Type, 16. Scientific/Academic Clarity, 17. Wallet-Connect & Transaction State Animations (+20 more)

### Community 11 - "Healthcare Industry Rules (20 Rules)"
Cohesion: 0.07
Nodes (28): 10. Calm, Minimal Aesthetic, 11. Trust & Care (Soft Blue), 12. Health & Wellness (Green), 13. Caution & Urgency (Orange/Red), 14. Clear, Accessible Fonts, 15. Patient-Friendly Language, 16. Hierarchical Information, 17. Reassuring Feedback (+20 more)

### Community 12 - "Lifestyle Industry Rules (20 Rules)"
Cohesion: 0.07
Nodes (28): 10. Shared Color-Coding for Family/Couple Apps, 11. Warm Streak Amber + Progress Green, 12. Calm Lavender & Midnight Pastels, 13. Nature Green + Earth Tones, 14. Playful Rounded for Habit & Family Apps, 15. Calm Wellness Serif/Sans, 16. Handwritten/Sketch for Journaling, 17. Breathing & Ambient Micro-Animations (+20 more)

### Community 13 - "Services Industry Rules (20 Rules)"
Cohesion: 0.07
Nodes (28): 10. Accessibility First for Vulnerable Users, 11. Trust Navy + Gold (Professional Services), 12. Warm Hospitality (Restaurant, Beauty, Wedding), 13. Booking-Blue + Confirm-Green (Transactional Services), 14. Formal Authority Serif/Sans, 15. Warm Editorial for Hospitality, 16. Clean Functional for Booking & Operator Tools, 17. Confirmation & Reminder Feedback (+20 more)

### Community 14 - "Tech & SaaS Industry Rules (20 Rules)"
Cohesion: 0.07
Nodes (28): 10. Dense Information Display, 11. Trust & Stability (Blues), 12. Growth & Success (Greens), 13. Caution & Urgency (Reds/Oranges), 14. Sans-Serif + Monospace Combination, 15. Clear Hierarchy, 16. Readability Over Personality, 17. Consistent Font Weights (+20 more)

### Community 15 - "Browser Automation with playwright-cli"
Cohesion: 0.07
Nodes (27): Attaching screenshots and videos to pull requests, Browser Automation with playwright-cli, Browser Sessions, Commands, Core, DevTools, Example: Debugging with DevTools, Example: Form submission (+19 more)

### Community 16 - "Postman → Playwright Migration (AI-Driven)"
Cohesion: 0.07
Nodes (26): 1. `collection.md` (API Structure & Endpoints), 1. URL Placeholders, 2. Auth Header, 2. `env.md` (Environment Variables), 3. Fixtures & Schemas (MANDATORY — create before spec file), 4. Runtime State (stateStore), AI Auto-Heal Workflow, Common Failure Patterns & Remedies (+18 more)

### Community 17 - "skill_learning_report.py"
Cohesion: 0.15
Nodes (25): Counter, date, archive(), auto_captured_skills(), capture_outcome(), curate(), frontmatter(), main() (+17 more)

### Community 18 - "1. Global Standards & Tooling Facts"
Cohesion: 0.08
Nodes (24): 1. Global Standards & Tooling Facts, 1. Hybrid Setup (API + Mobile), 2. Automation Strategy, 2. Expert Locators Fallback, 3. Screen Record on Failure, 4. Advanced Data Orchestration (Python Integration), 4. Mobile Expert Patterns & Gems, 5. Mobile Platform Differences (Android vs iOS) (+16 more)

### Community 19 - "design_system.py"
Cohesion: 0.12
Nodes (24): ansi_ljust(), _detect_page_type(), format_ascii_box(), format_markdown(), format_master_md(), format_page_override_md(), generate_design_system(), _generate_intelligent_overrides() (+16 more)

### Community 20 - "Reasoning Engine: 4-Stage Design System Generation"
Cohesion: 0.08
Nodes (23): 161 Industry Rules, Accessibility Check (WCAG AA), BM25 Ranking, Deliverables, Example Flow, Five Search Domains, Input, Integration (+15 more)

### Community 21 - "3. Heal"
Cohesion: 0.09
Nodes (23): 0. How generation works, 1.1 Prerequisite: workspace, 1.2 Prerequisite: seed test, 1.3 Explore the app, 1.4 Write the spec file, 1. Planning, 2.1 Inputs, 2.2 Generate one scenario (+15 more)

### Community 22 - "The `study` Trigger — Extracting Design DNA from a Screenshot or URL"
Cohesion: 0.09
Nodes (22): 1. Surface (color), 2. Type, 3. Structure (pattern), 4. Motion, 5. Rhythm, Emission-refusal layer (tighter than diagnosis refusal), Emitting a portable system from `study`, If the user says "build it" (+14 more)

### Community 23 - "coding-rules-gate.py"
Cohesion: 0.20
Nodes (20): _arch_key(), _bare(), bash_target(), decide_pre(), _drop_data_heredocs(), find_arch(), is_code_write(), main() (+12 more)

### Community 24 - ".generate"
Cohesion: 0.12
Nodes (13): DesignSystemGenerator, _filter_anti_patterns_for_mode(), Drop "avoid dark mode" advice once dark mode is the resolved answer., Generates design system recommendations from aggregated searches., Load reasoning rules from CSV., Execute searches across multiple domains., Find matching reasoning rule for a category., Apply reasoning rules to search results. (+5 more)

### Community 25 - "Web Frameworks"
Cohesion: 0.10
Nodes (19): Angular, Astro, Design Token Output Format, Flutter, HTML + Tailwind CSS, Jetpack Compose, Laravel, Mobile & Native (+11 more)

### Community 26 - "core.py"
Cohesion: 0.16
Nodes (18): detect_domain(), _domain_keywords(), _get_bm25(), _load_csv(), _load_product_keywords(), Load CSV and return list of dicts, with mtime-based caching., Fitted BM25 index for this file+columns, with mtime-based caching., Core search function using BM25. Returns (results, bm25_or_none). (+10 more)

### Community 27 - "PRODUCT.md / ARCHITECTURE.md / DESIGN.md Convention"
Cohesion: 0.11
Nodes (18): ADRs stay separate files, deliberately, Authoring, Command, Contents, Domain glossary: CONTEXT.md, Feature & project planning: `$AODD_PLANS/<feature>/<feature>-architecture.md`, FigJam to Markdown Converter, How skills use these files (+10 more)

### Community 28 - "secret-read-guard.py"
Cohesion: 0.20
Nodes (17): bash_targets(), _benign(), _call_arg(), decide(), deny(), edit_msg(), _expand(), is_secret() (+9 more)

### Community 29 - "Checklist — All Frameworks"
Cohesion: 0.11
Nodes (17): API Design (see `api-design.md`), Architecture, Authentication (see `authentication.md`), Backend Code Review, Checklist — All Frameworks, Database (see `database-design.md`), Django, Docker (see `docker.md`) (+9 more)

### Community 30 - "Part 2: QA — Test Scenario Design + Automation"
Cohesion: 0.11
Nodes (17): Anti-Rationalization (Dev + QA), Automation Patterns (Playwright), Dev Review Checklist, Fixture Structure + Pipeline, Internal Analysis (auto-run when loaded during test scenario design), Minimum Scenarios, Mobile Patterns (Robot Framework), OWASP-Based Test Conditions (+9 more)

### Community 31 - "graphify-guard.py"
Cohesion: 0.26
Nodes (16): changed_since_graph(), decide_pre(), decide_stop(), find_root(), _first_words(), _hso(), is_raw_search(), main() (+8 more)

### Community 32 - "Frontend Development"
Cohesion: 0.12
Nodes (16): Anti-Rationalization Table, Consistency Contract, Frontend Development, ⚠️ Gotchas, Human-in-the-Loop Points, Inline Process, LLM-Friendly Code Comments, Mobile (+8 more)

### Community 33 - "HAR-Based Network Mocking"
Cohesion: 0.12
Nodes (16): 3-Phase Workflow, Auto-fallback: real service → HAR, Basic replay, Error cases — always use page.route() (not HAR), File Structure, HAR-Based Network Mocking, HAR vs page.route() — When to use which, Mock Strategy Decision Table (+8 more)

### Community 34 - "Robot Framework + Flutter via Appium"
Cohesion: 0.12
Nodes (16): Android, Appium Server Setup for Flutter, Build Requirements, Capabilities — Flutter Driver, Common Issues, Context Switching, Flutter Code Preparation (Dev Team), iOS (+8 more)

### Community 35 - "antigravity-hook-adapter.py"
Cohesion: 0.30
Nodes (15): decide_skill_capture(), get_hook(), get_hooks_dir(), handle_post(), handle_pre(), handle_stop(), load_hooks(), _load_module() (+7 more)

### Community 36 - "memory-recall.py"
Cohesion: 0.27
Nodes (15): candidates(), describe(), extract_thai_tokens(), gist(), is_long(), is_machine_or_pasted(), is_recall_extra(), keywords() (+7 more)

### Community 37 - "Coding Principles"
Cohesion: 0.12
Nodes (15): 1. Think Before Coding, 2. Simplicity First, 3. Graph Before & After Edit, 4. Surgical Changes, 5. Goal-Driven Execution, 6. Project Structure, 7. Coding flow (after reading this file), Anti-Monolith & Separation Pattern (Target 300–400 lines) (+7 more)

### Community 38 - "AI-SDLC Progress Spec — Task Breakdown & Progress Tracking"
Cohesion: 0.12
Nodes (15): AI-SDLC Progress Spec — Task Breakdown & Progress Tracking, Artifact locations, Contents, File behavior & master index, Incremental update rule — update in real time, never batch at the end, Lessons learnt, Mock strategy (QA, before writing mock/interceptor tasks), Progress file — required sections (+7 more)

### Community 39 - "React Standards"
Cohesion: 0.12
Nodes (15): Component Design, Critical — Eliminating Waterfalls, Cross-Platform Standards, Folder Structure, High — Bundle Size, Hooks, Medium — Re-render Optimization, Naming (+7 more)

### Community 40 - "Browser Session Management"
Cohesion: 0.12
Nodes (16): A/B Testing Sessions, Attach by channel name, Attach via browser extension, Attach via CDP endpoint, Attaching to a Running Browser, Browser Session Commands, Browser Session Configuration, Browser Session Isolation Properties (+8 more)

### Community 41 - "Appium Testing (Android) — Platform Rules & Capabilities"
Cohesion: 0.13
Nodes (14): 1. Android Capabilities & Lifecycle, 1. Deep Linking (Fast Navigation Gem), 1. 🎯 Locator Strategy (Android DOM Lookup Strategy), 2. ADB Command Integration (Power User Gem), 2. Android Locator Strategy & Actions, 2. 🤖 Android-Specific Actions, 3. Android Expert Gems (Power User), 3. Network Speed Simulation (+6 more)

### Community 42 - "Appium Testing (iOS) — Platform Rules & Capabilities"
Cohesion: 0.13
Nodes (14): 1. iOS Capabilities & Lifecycle, 1. iOS Deep Linking (Fast Navigation Gem), 1. 🎯 Locator Strategy (iOS DOM Lookup Strategy), 2. Biometric Simulation (FaceID/TouchID Gem), 2. iOS Locator Strategy & Actions, 2. 🤖 iOS-Specific Actions, 3. Advanced Predicate String (Performance Gem), 3. iOS Expert Gems (Performance & Bypass) (+6 more)

### Community 43 - "audit.py"
Cohesion: 0.26
Nodes (14): build_prompt(), combine(), git(), main(), pick_auditor(), Path, Final verdict when Codex audits and a Claude Opus verifies (see docstring point, (user messages, worker kind: 'codex' | 'claude-<family>', first timestamp or Non (+6 more)

### Community 44 - "Checklist — All Platforms"
Cohesion: 0.13
Nodes (14): Android (Kotlin / Jetpack Compose), Architecture, Checklist — All Platforms, Environment Config (see `env-config-standards.md`), Error Handling (see `error-handling-standards.md`), Flutter, Frontend Code Review, iOS (Swift / SwiftUI) (+6 more)

### Community 45 - "1. Global Standards & Tooling Facts"
Cohesion: 0.14
Nodes (13): 1. Global Standards & Tooling Facts, 2. Automation & Execution Strategy, 3. Reference Links, Architecture-First for QA, Contents, Environment Configuration, Hybrid Execution Strategy, Locators & Wait Rules (+5 more)

### Community 46 - "API Design"
Cohesion: 0.14
Nodes (13): API Design, Contract-First API Design, Contract-First Checklist, Error Handling, GraphQL (when applicable), gRPC (when applicable), Hyrum's Law, Response Format (+5 more)

### Community 47 - "Test Scenario"
Cohesion: 0.14
Nodes (13): Anti-Rationalization, Batch Skip Guard (fires immediately on any skip signal), Extending to a Specific Tracker (Jira, Azure DevOps, Google Sheets, etc.), Full Workflow (MANDATORY for new feature — execute ALL steps in order), Gotchas, Human-in-the-Loop Points, Red Flags, Requirements Source (before Step 1) (+5 more)

### Community 48 - "Typography"
Cohesion: 0.14
Nodes (13): Accessibility, Choosing Distinctive Fonts, Classic Typography Principles, Fluid Type, Font Selection & Pairing, Modern Web Typography, Modular Scale & Hierarchy, OpenType Features (+5 more)

### Community 49 - "skill-capture-nudge.py"
Cohesion: 0.26
Nodes (12): _codex(), decide(), main(), post_tool(), Path, Codex rollout record {type: response_item, payload}. Returns updated (n, correct, Return the block reason, or None to allow the stop., PostToolUse(Bash): mid-flight reminder right after a fix commit. (+4 more)

### Community 50 - "Agent Memory Subagent Patterns"
Cohesion: 0.15
Nodes (12): 1. `memory-curator`, 2. `memory-bootstrapper`, 3. `knowledge-promoter`, 4. `skill-evolution-checker`, Agent Memory Subagent Patterns, Cost Guidance, Invocation Pattern, Recommended Utility Subagents (+4 more)

### Community 51 - "Project Structure Standard (role-based, stack-agnostic)"
Cohesion: 0.15
Nodes (12): 0. Enforcement: three levels, no optional tier, 1. Roles (fixed vocabulary), 2.1 Project runner (MAY), 2. Root layout (every project), 3. Source layout by size, 4. Dependency direction, 5. Naming, 6. Principles (+4 more)

### Community 52 - "SKILL.md"
Cohesion: 0.21
Nodes (4): Examples, Inspecting Element Attributes, Debugging Playwright Tests, Running Playwright Tests

### Community 53 - "Running Custom Playwright Code"
Cohesion: 0.15
Nodes (13): Clipboard, Complex Workflows, Error Handling, File Downloads, Frames and Iframes, Geolocation, JavaScript Execution, Media Emulation (+5 more)

### Community 54 - "Tracing"
Cohesion: 0.15
Nodes (12): 1. Start Tracing Before the Problem, 2. Clean Up Old Traces, Analyzing Performance, Basic Usage, Best Practices, Capturing Evidence, Debugging Failed Actions, Limitations (+4 more)

### Community 55 - "Accessibility Testing — Playwright + axe-core"
Cohesion: 0.15
Nodes (12): Accessibility Testing — Playwright + axe-core, Basic Accessibility Scan, Best Practices, CI Integration, Common Accessibility Rules to Check, Exclude Known Issues (Temporary), Filter by WCAG Level, Playwright Accessibility Assertions (Built-in) (+4 more)

### Community 56 - "Component Testing — Playwright"
Cohesion: 0.15
Nodes (12): Basic Component Test, Best Practices, Component Testing — Playwright, Config, Run Component Tests, Setup, Testing Forms, Testing Interactions (+4 more)

### Community 57 - "Explore-to-Test Workflow"
Cohesion: 0.15
Nodes (12): Comparison: Explore Tools, Decision Matrix: Which Tool When, Explore-to-Test Workflow, Full Workflow, Integration with Existing Skills, Rules, Step 1: Explore with Chrome DevTools MCP, Step 2: Capture HAR (+4 more)

### Community 58 - "Checklist"
Cohesion: 0.15
Nodes (12): API Tests (if applicable), Checklist, Code Quality, Database (if applicable), Locators (Critical), Performance & Reliability, Playwright Code Review, Review Process (+4 more)

### Community 59 - "8-Step Workflow"
Cohesion: 0.15
Nodes (12): 1. Reproduce in Browser, 2. Inspect Console Errors, 3. Inspect Network Requests/Responses, 4. Inspect DOM and Accessibility Tree, 5. Check Storage/State, 6. Capture Screenshot or Trace, 7. Use Evidence to Fix, 8. Add Regression Test (+4 more)

### Community 60 - "Playwright Workflow"
Cohesion: 0.15
Nodes (12): 1. Code Writer, 2. Code Review, 3. Test Execution, 4. Self-Healing (Reflexion Pattern), Bug Report Template (When QA cannot self-heal), Mock data location, Mock Layer (MANDATORY — TDD Red Phase), Pattern: health check + auto-fallback (+4 more)

### Community 61 - "Robot Framework 7.x New Features"
Cohesion: 0.15
Nodes (12): Best Practices for RF 7.x, Improved Argument Conversion, Inline IF (RF 5+), Listener API v3 (RF 7), Native JSON Support, Robot Framework 7.x New Features, Secret Variables (RF 7.4), Skip Tests Conditionally (+4 more)

### Community 62 - "Checklist"
Cohesion: 0.15
Nodes (12): Appium Configuration, Checklist, Code Quality, Database (if applicable), Expert Gems (Advanced), Keywords Quality, Locators (Critical — Mobile), Review Process (+4 more)

### Community 63 - "Read Mode"
Cohesion: 0.15
Nodes (12): Derive Mode, Edit Mode, How it works, Mode Detection (Step 0), Output per test case, Process, Read Mode, Rules (+4 more)

### Community 64 - "Pre-Delivery Checklist (canonical — the only one)"
Cohesion: 0.15
Nodes (12): Accessibility, Common Rules for Professional UI + Pre-Delivery Checklist, Icons & Visual Elements, Interaction, Interaction (App), Layout, Layout & Spacing, Light/Dark Mode (+4 more)

### Community 65 - "Quick Reference"
Cohesion: 0.15
Nodes (12): 10. Charts & Data (LOW), 1. Accessibility (CRITICAL), 2. Touch & Interaction (CRITICAL), 3. Performance (HIGH), 4. Style Selection (HIGH), 5. Layout & Responsive (HIGH), 6. Typography & Color (MEDIUM), 7. Animation (MEDIUM) (+4 more)

### Community 66 - "BM25"
Cohesion: 0.18
Nodes (8): BM25, _normalize(), Apply synonym substitution before tokenizing., BM25 ranking algorithm for text search, Lowercase, normalize synonyms, split, remove punctuation, filter stopwords, Build BM25 index from documents, Score all documents against query, All indexed terms, for suggestion/typo-recovery purposes.

### Community 67 - "decide"
Cohesion: 0.32
Nodes (11): decide(), git(), main(), new_worktree_repo(), Drop quoted strings and heredoc bodies so prose in a commit message / script nev, (dirty, unmerged): worktrees with uncommitted changes, and branches with commits, Returns (error_msg, is_blocking: bool, additional_context: str | None)., sibling_state() (+3 more)

### Community 68 - "Agent Memory"
Cohesion: 0.17
Nodes (11): Agent Memory, Bootstrap, Context compression, Knowledge capture, Memory structure, Promotion flow, Rules, Self-update (+3 more)

### Community 69 - "agent_ops_gather.py"
Cohesion: 0.29
Nodes (11): agy_dirs(), agy_section(), main(), markers(), Gather the weekly Agent Ops input for every agent tool installed (Claude Code in, (session count, {skill: sessions mentioning it})., Per-session tool calls and skills loaded from Antigravity transcripts; "" when n, recent_files() (+3 more)

### Community 70 - "Step-by-Step Execution Guide"
Cohesion: 0.17
Nodes (11): 5-Phase Lifecycle Overview, AI-SDLC Workflow & Execution Guide, Bugs, Incidents & Git Operations, Collapse Rules (When to Skip Phases), Step 0: Scope & Discovery (Pre-SDLC), Step 1: Clarify & Spec (Phase 1), Step 2: Architect & Slice Tickets (Phase 2), Step 3: Design Test Skeletons in RED (Phase 3) (+3 more)

### Community 71 - "Backend Development"
Cohesion: 0.17
Nodes (11): Backend Development, Code Quality, Core, ⚠️ Gotchas, Human-in-the-Loop Points, Infrastructure, Inline Process, LLM-Friendly Code Comments (+3 more)

### Community 72 - "Next.js 15 — App Router & Server Components"
Cohesion: 0.17
Nodes (11): Caching Strategy, Core Mental Model, Data Fetching, Folder Structure (Production), Middleware, Next.js 15 — App Router & Server Components, React 19 Hooks in Next.js, Route Handlers (API Routes) (+3 more)

### Community 73 - "Playwright Recorder Analyzer"
Cohesion: 0.17
Nodes (11): Extraction Checklist, Form Filling, Hard Waits, Locator priority, Pattern Transformations, Playwright Recorder Analyzer, Process, Record First (+3 more)

### Community 74 - "Visual Regression Testing — Playwright"
Cohesion: 0.17
Nodes (11): Basic Screenshot Comparison, Best Practices, CI Integration, Cross-Browser Visual Testing, Folder Structure, Masking Dynamic Content, Multi-Viewport Testing, Playwright Config for Screenshots (+3 more)

### Community 75 - "Playwright Testing"
Cohesion: 0.17
Nodes (11): Anti-Rationalization, Bug Life Cycle Integration (GUARD state), Gotchas, Human-in-the-Loop Points, Key Rules, Playwright Testing, Red Flags, Required Context (+3 more)

### Community 76 - "Robot Framework Browser Library (Playwright-Powered)"
Cohesion: 0.17
Nodes (11): Assertions, Auto-Wait (Key Advantage over Selenium), Basic Usage, Installation, Locator Strategies, Network Interception (Mock API), Page Object Pattern with Browser Library, Parallel Execution (+3 more)

### Community 77 - "Robot Framework Testing"
Cohesion: 0.17
Nodes (11): Anti-Rationalization Table, Consistency Contract, Human-in-the-Loop Points, Inline Process, Property-based Testing Pattern (Hypothesis), Red Flags, Required Context, Robot Framework Testing (+3 more)

### Community 78 - "Color & Contrast"
Cohesion: 0.17
Nodes (11): Alpha Is A Design Smell, Building Functional Palettes, Color & Contrast, Color Spaces: Use OKLCH, Contrast & Accessibility, Dangerous Combinations, Dark Mode, Palette Structure (+3 more)

### Community 79 - "Spatial Design"
Cohesion: 0.17
Nodes (11): Cards Are Not Required, Container Queries, Depth & Elevation, Grid Systems, Hierarchy Through Multiple Dimensions, Optical Adjustments, Spacing Systems, Spatial Design (+3 more)

### Community 80 - "release.py"
Cohesion: 0.38
Nodes (10): CompletedProcess, find_repo_root(), main(), next_version(), output(), publish(), Path, release_exists() (+2 more)

### Community 81 - "work-log.py"
Cohesion: 0.35
Nodes (10): entry(), log_dir(), main(), project_of(), Path, Project name for a session dir: the main repo of a git worktree, None for temp d, LOG_DIR, or FALLBACK_DIR when an explicit $AODD_WORKLOG points under a folder th, report() (+2 more)

### Community 82 - "Gemini & Antigravity (agy) Prompting Principles"
Cohesion: 0.18
Nodes (10): 1. Mandatory Clarification Triggers, 2. How to Ask Effectively, Core Mandate 1: Grounded Analysis & Zero Hallucination, Core Mandate 2: Ask When in Doubt — Never Assume, Do, Don't, Effective Prompt & Task Structure, Gemini & Antigravity (agy) Prompting Principles (+2 more)

### Community 83 - "Error Handling Standards — Backend (All Languages)"
Cohesion: 0.18
Nodes (10): Error Code Convention, Error Handling Standards — Backend (All Languages), Error Response Format (All Services), HTTP Status Code Mapping, Node.js (Express), Node.js (NestJS), Platform Implementation, Python (Django REST Framework) (+2 more)

### Community 84 - "Environment Config Standards — All Platforms"
Cohesion: 0.18
Nodes (10): Android (Kotlin), Environment Config Standards — All Platforms, Environments, Flutter, iOS (Swift), Key Naming Convention, Platform Implementation, React / Web (+2 more)

### Community 85 - "Performance Bottleneck Triage & Analysis"
Cohesion: 0.18
Nodes (10): 1. Triage Workflow, 2. Backend & Database Triage, 3. Frontend & Network Triage, 4. Mobile Performance Triage, 5. Load Test Result Analysis (k6), API Response Time Profiling, Database Query Analysis, Key Metrics Interpretation (+2 more)

### Community 86 - "Performance Testing"
Cohesion: 0.18
Nodes (10): Anti-Rationalization Table, Consistency Contract, Human-in-the-Loop Points, Inline Process, Performance Testing, Red Flags, Required Context, Self-Update (after every use) (+2 more)

### Community 87 - "Security Scanning in CI/CD"
Cohesion: 0.18
Nodes (10): CodeQL — Static Analysis (SAST), Full DevSecOps Pipeline Pattern, Gitleaks — Secret Detection, Rules, Scanning Types, Security Scanning in CI/CD, Semgrep — Fast SAST (no build needed), Severity Policy (+2 more)

### Community 88 - "@design-system Skill"
Cohesion: 0.18
Nodes (10): 1. Invoke the Skill, 2. Provide Project Context, 3. Get Your Design System, Core Capabilities, @design-system Skill, Directory Structure, Features, Next Steps (Remaining) (+2 more)

### Community 89 - "Interaction Design"
Cohesion: 0.18
Nodes (10): Destructive Actions: Undo > Confirm, Dropdown Positioning, Focus Rings, Form Design, Interaction Design, Keyboard Navigation, Loading States, Modals: The Inert Approach (+2 more)

### Community 90 - "install.sh"
Cohesion: 0.40
Nodes (9): add_mod(), ask(), copy_file(), copy_module(), copy_tree(), found(), has_mod(), register_hooks() (+1 more)

### Community 91 - "Logging Standards — Backend (All Languages)"
Cohesion: 0.20
Nodes (9): Log Levels, Logging Standards — Backend (All Languages), Node.js — Winston, Platform Implementation, Python — structlog / logging, Request ID (Mandatory), Rules, Security Rules (+1 more)

### Community 92 - "Delivery Workflow"
Cohesion: 0.20
Nodes (10): Approval and external effects, Candidate and rollback, Delivery Workflow, Done means, Gates and failures, References, Required in every repo, Stages (+2 more)

### Community 93 - "Platform Implementation"
Cohesion: 0.20
Nodes (9): Android (Compose), Flutter, i18n / multi-language, iOS (SwiftUI), Platform Implementation, React / Web, Rules, Testability Standards — Test Identifier (All Platforms) (+1 more)

### Community 94 - "XCTest — macOS Swift Testing"
Cohesion: 0.20
Nodes (9): Anti-Patterns, Layer Boundary — XCTest vs Robot, Minimal Runnable Check, Reference, Running, Swift 6 Test Patterns, Testability Rule for MyApp Models, Where Tests Live (+1 more)

### Community 95 - "Quick Automation"
Cohesion: 0.20
Nodes (9): Decision Tree, Escalation Message, Full workflow triggers, Phase 1 — File State Check, Phase 2 — Scope Check (read actual code first), Platform Compliance, Process (Quick Mode), Quick Automation (+1 more)

### Community 96 - "Test Data Generation"
Cohesion: 0.20
Nodes (9): Output Format, Process, Rules, Step 1.5: Dependency Analysis, Step 1: Analyze & Collect Data, Step 2: Generate ALL Test Data (single batch), Test Data Generation, Validation Requirements (+1 more)

### Community 97 - "Test Scenario — Design Guidelines & Process"
Cohesion: 0.20
Nodes (9): 1. Scenario Title Convention, 2. Core Structure & Schema (9 Fields), 3. Paired Design & File Separation, 4. Test Design Techniques Selection, 5. 3-Batch Design Process (Human-in-the-Loop), 6. Output Markdown Format, 7. CSV Export Requirements (RFC 4180), Priority & Automation Matrix (+1 more)

### Community 98 - "Figma & UI Analysis"
Cohesion: 0.20
Nodes (9): Figma & UI Analysis, How it works, Output, Step 1: Check for Visual Context, Step 2: Analyze Context, Step 3: Extract Details & Visual Mapping, Visual Error & Edge Simulation, Visual-to-Business Rules Mapping Table (+1 more)

### Community 99 - "Industry Rules (161 Total)"
Cohesion: 0.20
Nodes (9): Anti-Pattern Check, By Industry File, Cross-Industry Pattern, Industry Rules (161 Total), Quick Lookup, Rule Structure, Sectors, Single Industry (+1 more)

### Community 100 - "Self-Review Rubric"
Cohesion: 0.22
Nodes (8): Anti-Patterns, Constraints, Save Rubric (before patching a skill), Self-Review Rubric, Skill Flag Rubric, Skill Improvement Rubric, What to Review, When to Apply This

### Community 101 - "AODD: the operating contract"
Cohesion: 0.22
Nodes (8): AODD: the operating contract, AODD triage: every request passes this gate (silently, no announcement), Audit and Done, Cheap-model delegation, Default model split (don't ask each time), Haiku ops runner, Human as a Judge / Boss Mode, Test-Before-Deliver

### Community 102 - "data-testid Naming Convention"
Cohesion: 0.22
Nodes (8): Contents, data-testid Naming Convention, Mobile (Robot Framework + Appium), Naming Rules, Pattern, Shared Components, Type Abbreviation Table, Usage

### Community 103 - "Playwright Web UI Testing — Rules"
Cohesion: 0.22
Nodes (8): Advanced, Locators, Login / auth, package.json scripts (MANDATORY), Page object design, Playwright Web UI Testing — Rules, Structure, Synchronization and assertions

### Community 104 - "Dev↔QA Design Handoff"
Cohesion: 0.22
Nodes (8): Contents, data-testid handoff (Phase 2, Client Application section), DB seed/verify/cleanup strategy, Dev↔QA Design Handoff, Domain Language (only when the feature touches new/ambiguous domain terms), Schema Consistency Check (Phase 2→3 boundary, both API and DB), Shared fixtures across platforms (API + Web UI + Mobile on one feature), Test environment requirements (Phase 2, before handoff to Phase 3)

### Community 105 - "Dev + QA Pattern — Unified Architectural & Testing Standard"
Cohesion: 0.22
Nodes (8): 1. Tagging: `[LAYER-KIND]`, 2. Dev Pattern — The 5 Structural Layers, 3. Dev Implementation Invariants & Rules, 4. QA Verification Pattern — Dual-Layer Testing, 5. Continuous Architecture Guard (Automated Static Invariants), 6. Anti-Patterns & Traps, 7. Definition of Done Checklist (Dev & QA), Dev + QA Pattern — Unified Architectural & Testing Standard

### Community 106 - "Database Design"
Cohesion: 0.22
Nodes (8): Database Design, Database Types, Indexing, Migrations, Naming, Query Patterns, Schema Design, Tips

### Community 107 - "Environment Config Standards — Backend (All Languages)"
Cohesion: 0.22
Nodes (8): Environment Config Standards — Backend (All Languages), Environments, Key Naming Convention, Node.js, Platform Implementation, Python (FastAPI — pydantic-settings), Rules, What Goes Where

### Community 108 - "Platform Implementation"
Cohesion: 0.22
Nodes (8): Input Validation Standards — Backend (All Languages), Node.js — NestJS (class-validator), Node.js — Zod, Platform Implementation, Python — Django REST Framework, Python — FastAPI (Pydantic), Rules, Validation Rules

### Community 109 - "macOS SwiftUI Skill"
Cohesion: 0.22
Nodes (8): Anti-Patterns, Load Right Reference, macOS SwiftUI Skill, Required Context, Self-Update (after every use), `swift test` gotchas (SPM app with binary frameworks), Trigger, When to Fall Back to AppKit

### Community 110 - "Best Practices"
Cohesion: 0.22
Nodes (9): 1. Use Descriptive Filenames, 2. Record entire hero scripts., 3. Attach the recording to the pull request, Basic Recording, Best Practices, Limitations, Overlay API Summary, Tracing vs Video (+1 more)

### Community 111 - "Playwright Database Writer"
Cohesion: 0.22
Nodes (8): Brownfield DB Strategy, Brownfield rules, Forbidden Patterns, Playwright Database Writer, Problems, Rules, Steps, When to use

### Community 112 - "Diversification Memory"
Cohesion: 0.22
Nodes (8): Append to project memory, Diversification Memory, Schema, Scope, Stamp the output, State file location, The diversification rule (mandatory), Why this exists

### Community 113 - "Extract Flow"
Cohesion: 0.22
Nodes (8): Extract Flow, Never, Step 1: Discover the Design System, Step 2: Identify Patterns, Step 3: Plan Extraction, Step 4: Extract & Enrich, Step 5: Migrate, Step 6: Document

### Community 114 - "Responsive Design"
Cohesion: 0.22
Nodes (8): Breakpoints: Content-Driven, Detect Input Method, Not Just Screen Size, Layout Adaptation, Mobile-First, Responsive Design, Responsive Images, Safe Areas, Testing

### Community 115 - "UX Writing"
Cohesion: 0.22
Nodes (8): Accessibility, Button Labels, Consistency, Empty States, Error Messages, Translation, UX Writing, Voice vs Tone

### Community 116 - "Antigravity Integration (agy)"
Cohesion: 0.25
Nodes (7): Antigravity Integration (agy), Environment variables, How to install, Lifecycle Hook Adapter details, Limits, Safety and Idempotency, What is supported

### Community 117 - "Test structure by design technique"
Cohesion: 0.25
Nodes (7): Base-Choice (1 base E2E + N one-parameter variations), Multiple-Choice / pairwise (data-driven), Security tests, State Transition, Stateful helper requirements, Test structure by design technique, Transition tree / W-method

### Community 119 - "Chief of Staff — one brief in, one report out"
Cohesion: 0.25
Nodes (7): 1. Brief (ask once, all at once), 2. Dispatch (team = existing skill; lead = the skill, members = subagents), 3. Stop and ask the CEO (never decide these yourself), 4. Check, then report, Chief of Staff — one brief in, one report out, Dispatch pitfalls (verified), Self-Update (after every use)

### Community 120 - "Release and Deploy"
Cohesion: 0.25
Nodes (8): 1. Preflight, 2. Candidate and record, 3. Validate the exact commit, 4. Publish (semver release only), 5. Deploy or install, 6. Verify the live target, 7. Report, Release and Deploy

### Community 121 - "K6 Load Testing Standards & CI Gates"
Cohesion: 0.25
Nodes (7): 1. Hard Standards, 2. Standard SLA Thresholds, 3. Production Script Template, 4. CI/CD Performance Gates, Azure DevOps, GitHub Actions, K6 Load Testing Standards & CI Gates

### Community 122 - "Advanced Mocking with run-code"
Cohesion: 0.25
Nodes (8): Advanced Mocking with run-code, CLI Route Commands, Conditional Response Based on Request, Delayed Response, Modify Real Response, Request Mocking, Simulate Network Failures, URL Patterns

### Community 123 - "Robot Framework Workflow"
Cohesion: 0.25
Nodes (7): 1. Code Writer, 2. Code Review, 3. Test Execution, 4. Self-Healing (Reflexion Pattern), 5. Python Database Writer, Robot Framework Workflow, Test Results & Reflexion Log — Write to Audit Trail (MANDATORY)

### Community 124 - "Security"
Cohesion: 0.25
Nodes (7): Load, Related Skills, Required Context, Secret handling in an agent session (verified), Security, Self-Update (after every use), When to Load This Skill

### Community 125 - "The `audit` Trigger — Read-Only Quality Check"
Cohesion: 0.25
Nodes (7): `design-system/<project>/MASTER.md` / `DESIGN.md` audit, Output shape, Stamp-vs-page check, Structural fingerprint check, The `audit` Trigger — Read-Only Quality Check, What `audit` does, When to hand off

### Community 126 - "Industry Rules (161 Total)"
Cohesion: 0.25
Nodes (7): Anti-Pattern Check, Cross-Industry Pattern, Industry Rules (161 Total), Quick Lookup, Rule Structure, Single Industry, Usage

### Community 127 - "Motion Design"
Cohesion: 0.25
Nodes (7): Duration: The 100/300/500 Rule, Easing, Motion Design, Only Animate transform and opacity, Perceived Performance, Reduced Motion (NOT optional), Staggered Animations

### Community 129 - "Working on aodd-aisdlc"
Cohesion: 0.29
Nodes (6): Check your change, Conventions, Layout, Public API (adapters depend on it), Versioning and releases, Working on aodd-aisdlc

### Community 130 - "Playwright API Testing — Rules"
Cohesion: 0.29
Nodes (6): Assertions and concurrency, Fixtures and auth, Mocking, package.json scripts (MANDATORY), Playwright API Testing — Rules, Structure

### Community 131 - "rea_check.py"
Cohesion: 0.62
Nodes (6): fmt(), latest_version(), launcher(), main(), run(), semver()

### Community 132 - "QA Automation Loop — Shared Self-Heal & Reporting Discipline"
Cohesion: 0.29
Nodes (6): Error triage: Environment vs Code, Impact Analysis (mandatory before any fix), QA Automation Loop — Shared Self-Heal & Reporting Discipline, Reflexion Log (every heal attempt, success or fail), Test Execution → Heal escalation, Test Results (every run, appended to the audit trail)

### Community 133 - "Authentication & Authorization"
Cohesion: 0.29
Nodes (6): Authentication & Authorization, Authentication Methods, Authorization Patterns, Security Checklist, Tips, Token Refresh Flow

### Community 134 - "Docker"
Cohesion: 0.29
Nodes (6): Docker, Docker Compose, Dockerfile Best Practices, Environment Variables, Rules, Tips

### Community 135 - "Full Cycle"
Cohesion: 0.29
Nodes (7): 1. Select the cycle, 2. Docs before code, 3. Build, test, Graphify, 4. Commit and merge, 5. Release or skip, 6. Report, Full Cycle

### Community 136 - "SwiftUI macOS UI Components"
Cohesion: 0.29
Nodes (6): Context Menu, Keyboard Shortcuts, List — Hierarchical (File Tree), NavigationSplitView (macOS 13+), SwiftUI macOS UI Components, Toolbar

### Community 137 - "Frontend Performance & Core Web Vitals"
Cohesion: 0.29
Nodes (6): 1. Core Web Vitals Targets, 2. Playwright Tracing & Profiling Pattern, 3. Performance Report Format, 4. Common Frontend Bottlenecks & Fixes, Frontend Performance & Core Web Vitals, Markdown Report Schema

### Community 138 - "Craft Flow"
Cohesion: 0.29
Nodes (6): Craft Flow, Step 1: Shape the Design, Step 2: Load References, Step 3: Build, Step 4: Visual Iteration, Step 5: Present

### Community 139 - "AI-SDLC — Dev/QA Workflow Spine"
Cohesion: 0.33
Nodes (5): AI-SDLC — Dev/QA Workflow Spine, Approval Gates (mandatory on the Requirement path), Core facts (non-negotiable, not model-inferable — everything else is judgment), Phase map — load only the phase you are on, Status

### Community 140 - "Recovery"
Cohesion: 0.33
Nodes (5): 1. Establish the actual state, 2. Choose the narrowest safe step, 3. Never, 4. Report, Recovery

### Community 141 - "Tracing a Delivery Entrypoint"
Cohesion: 0.33
Nodes (6): 1. Follow the full call chain, 2. Write the evidence map, 3. Capability profile, 4. Demonstrate only when reading leaves a question, 5. Decide whether the helper is safe to run as is, Tracing a Delivery Entrypoint

### Community 142 - "Navigation & Deep Link Standards — All Platforms"
Cohesion: 0.33
Nodes (5): Deep Link Scheme, Navigation & Deep Link Standards — All Platforms, Route Naming Convention, Rules, Rules

### Community 143 - "UI States Standards — All Platforms"
Cohesion: 0.33
Nodes (5): Rules, State Model Pattern (All Platforms), Test Identifier Requirements, The 4 Mandatory States, UI States Standards — All Platforms

### Community 144 - "Tailwind CSS v4 Standards"
Cohesion: 0.33
Nodes (5): Best Practices, Design System, Integration, Responsiveness, Tailwind CSS v4 Standards

### Community 145 - "SwiftUI State Management"
Cohesion: 0.33
Nodes (5): @Observable (macOS 14+ / Swift 5.9) — prefer this, @Observable vs ObservableObject, ObservableObject (macOS 11–13 compat), SwiftUI State Management, Wrapper Quick-Pick

### Community 146 - "Project Blueprint: Structure Standard"
Cohesion: 0.33
Nodes (5): Bend a rule, Project Blueprint: Structure Standard, Review (existing project), Scaffold (new project), Self-Update (after every use)

### Community 147 - "Appium Inspector / Session Capabilities"
Cohesion: 0.33
Nodes (5): Android — install-if-missing, launch-if-present, Appium Inspector / Session Capabilities, Before opening Inspector, iOS, `noReset` vs `fullReset` — don't confuse these

### Community 148 - "Python Database Writer"
Cohesion: 0.33
Nodes (5): Forbidden Patterns, Python Database Writer, Rules, Steps, When to use

### Community 149 - "The `redesign` Trigger — Same Content, Different Structural Fingerprint"
Cohesion: 0.33
Nodes (5): Multi-page flow — lock a system first, then redesign each page, Non-destructive implementation rule, Single-page flow, Step 0 — Detect scope first, The `redesign` Trigger — Same Content, Different Structural Fingerprint

### Community 150 - "_palette_is_dark"
Cohesion: 0.33
Nodes (6): _palette_is_dark(), WCAG relative luminance of a #RRGGBB string, or None if unparseable., True when a colors.csv row's Background is a dark surface., Pick the highest-ranked palette matching the resolved mode.      Only the dark c, _relative_luminance(), _select_palette_for_mode()

### Community 151 - "_resolve_color_mode"
Cohesion: 0.33
Nodes (6): _query_wants_dark(), True when a styles.csv row describes itself as dark-first., True when the query explicitly asks for a dark theme., Resolve the mode the rest of the output has to agree with., _resolve_color_mode(), _style_is_dark_primary()

### Community 152 - "install-agy.sh"
Cohesion: 0.70
Nodes (4): copy_file(), copy_tree(), register_hooks(), install-agy.sh script

### Community 153 - "check_agy_proposal.py"
Cohesion: 0.60
Nodes (4): fields(), main(), problems(), {field: value}; a value runs until the next known field (so code blocks may span

### Community 155 - "Agent Ops"
Cohesion: 0.40
Nodes (4): Agent Ops, Pitfalls (verified), Self-Update (after every use), SOP

### Community 157 - "Error Handling Standards — All Platforms"
Cohesion: 0.40
Nodes (4): Error Categories, Error Handling Standards — All Platforms, Response Convention, Rules

### Community 158 - "Logging Standards — All Platforms"
Cohesion: 0.40
Nodes (4): Log Levels, Logging Standards — All Platforms, Rules, Security Rules

### Community 159 - "Hook authoring"
Cohesion: 0.40
Nodes (4): Check it worked, Hook authoring, Rules, Self-Update (after every use)

### Community 160 - "Embedding: AppKit ↔ SwiftUI"
Cohesion: 0.40
Nodes (4): Bridging Actions: SwiftUI → AppKit Host, Embedding: AppKit ↔ SwiftUI, NSHostingView — SwiftUI inside AppKit, NSViewRepresentable — AppKit inside SwiftUI

### Community 161 - "Drag and Drop"
Cohesion: 0.40
Nodes (4): Drag and Drop, Generation 1: NSItemProvider (macOS 11+), Generation 2: Transferable (macOS 13+) — prefer for in-app, UTType Reference

### Community 162 - "Attaching Screenshots and Videos to Pull Requests"
Cohesion: 0.40
Nodes (5): Attaching Screenshots and Videos to Pull Requests, From a local session, From CI, Limits, When to attach

### Community 163 - "memory-write-scan.py"
Cohesion: 0.83
Nodes (3): is_memory_path(), main(), scan()

### Community 164 - "memory_index.py"
Cohesion: 0.83
Nodes (3): block(), rebuild(), title()

### Community 165 - "Agent Memory Index"
Cohesion: 0.50
Nodes (3): Agent Memory Index, Knowledge, Plans

### Community 166 - "Output Format & Workflow Fan-out"
Cohesion: 0.50
Nodes (3): 6. Visual Output: .md vs HTML/Artifact, 7. Workflow Fan-out Pattern Check, Output Format & Workflow Fan-out

### Community 168 - "ai-sdlc"
Cohesion: 0.50
Nodes (3): ai-sdlc, Read before each phase (memory dir from the `agent-memory` skill; open only matching sections), Self-Update (after every use)

### Community 169 - "Commit and Push"
Cohesion: 0.50
Nodes (4): Before committing, Before pushing, Commit and Push, Graphify first

### Community 170 - "Dev / Preview and Test / QA"
Cohesion: 0.50
Nodes (3): Dev / preview, Dev / Preview and Test / QA, Test / QA

### Community 171 - "Verify before destroying"
Cohesion: 0.50
Nodes (3): Check it worked, Self-Update (after every use), Verify before destroying

### Community 172 - "Housekeeping"
Cohesion: 0.50
Nodes (3): Housekeeping, Self-Update (after every use), SOP

### Community 173 - "Best Practices"
Cohesion: 0.50
Nodes (4): 1. Name Browser Sessions Semantically, 2. Always Clean Up, 3. Delete Stale Browser Data, Best Practices

### Community 174 - "Trace Output Files"
Cohesion: 0.50
Nodes (4): `resources/`, Trace Output Files, `trace-{timestamp}.network`, `trace-{timestamp}.trace`

### Community 175 - "Scheduled jobs (cron / launchd)"
Cohesion: 0.50
Nodes (3): Check it worked, Scheduled jobs (cron / launchd), Self-Update (after every use)

### Community 176 - "validate_data.py"
Cohesion: 0.83
Nodes (3): _check_file(), main(), _read_rows()

## Knowledge Gaps
- **1396 isolated node(s):** `changelog`, `git`, `Layout`, `Check your change`, `Conventions` (+1391 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.
- **14 possibly unreachable function(s):** `_size()`, `ask_model()`, `git()`, `housekeeping_scan()`, `job_agent_ops()` (+9 more)
  Not reached from any recognized entry point - could be dead code, or dynamically dispatched/decorator-registered.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `log()` connect `_aodd_paths.py` to `BM25`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `_get_bm25()` connect `core.py` to `BM25`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Why does `BM25` connect `BM25` to `core.py`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **What connects `Translate Antigravity's JSON contract to Claude Code hook payload format.`, `Scan Antigravity or Claude transcript for tool calls and learning signals.`, `Antigravity stop decision for skill-learning nudge (Hermes-style).` to the rest of the system?**
  _1490 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `_aodd_paths.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06521739130434782 - nodes in this community are weakly interconnected._
- **Should `Fix Generated Playwright Files (Postman Migration)` be split into smaller, more focused modules?**
  _Cohesion score 0.041666666666666664 - nodes in this community are weakly interconnected._
- **Should `Changelog` be split into smaller, more focused modules?**
  _Cohesion score 0.0425531914893617 - nodes in this community are weakly interconnected._