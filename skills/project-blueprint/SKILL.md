---
name: project-blueprint
description: >
  Project structure: "วางโครงสร้างโปรเจกต์", "จัดระเบียบโปรเจกต์", "project structure", "blueprint", "dashboard architecture"; scaffolding, reviewing or refactoring a layout by role (UI, logic, integration, config, types, data, tests). Repos with an enforced layout keep it.
version: 1.3.0
---

# Project Blueprint: Structure Standard

Full rule: `rules/coding/project-blueprint.md` (roles, root layout, size trees, dependency direction, checklist). Read it first.

## Scaffold (new project)
1. Pick size (§3) and keep the framework's `<source-root>` name.
2. Identify the project's release lifecycle. If it publishes a versioned artifact or deploys to production, read `references/release-profiles.md`, select the closest profile from project evidence, and scaffold the local release entry point, config, and fake-command test required by §2.2. Ask one concise question if the actual production target or its approval boundary is unclear. Do not scaffold production publishing for projects without a release target.
3. Create §2 root files, then only the role dirs the project actually needs.
4. Config/tokens first (§1 Config), then logic, then UI — dependency direction §4.

## Bend a rule
Record `- §<rule> — <why> — <revisit when>` (MUST needs an external constraint; STRONG needs a revisit date) under `## Structure deviations` in the project's ARCHITECTURE.md. Never silently skip.

## Review (existing project)
Run the §7 checklist and, when it has a release/deploy target, map its current pipeline against `references/release-profiles.md`; report PASS/FAIL/WARN/ACCEPTED per line with file evidence (MUST = fail, STRONG = fail unless fixed or recorded with a revisit date, SHOULD = warn, recorded deviation = accepted). Do not refactor without the user's approval; list violations with the smallest fix. Repo with its own enforced layout, or a read-only clone? Stop.
