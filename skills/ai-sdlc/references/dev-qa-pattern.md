# Dev + QA Pattern — layer/kind tags for scenarios and tests

Applies to every project and every stack (web, mobile, game, tooling). Load when naming a
scenario, test, or task, or when deciding which kind of test a behaviour needs.

## 1. Tag: `[LAYER-KIND]`

| Part | Value | Meaning |
|---|---|---|
| Layer | `BE` | Logic and data with no UI: services, APIs, domain rules, pure game maths |
| | `FE` | What the user sees or touches: screens, components, game actors/shaders |
| Kind | `BL` | Business Logic: one rule, possibly several steps, inside one module |
| | `UT` | Unit Test: one function, known input → known output (parity/golden-value checks are UT) |
| | `IT` | Integration Test: two or more modules, persistence, or a real boundary (API + DB, state + save/load) |

Combine freely: `[BE-BL]`, `[BE-UT]`, `[BE-IT]`, `[FE-IT]`. Rule of thumb: one function → `UT`; one rule across a few
steps → `BL`; two or more modules or persistence → `IT`.

Scenario title: `[LAYER-KIND][Success|Alternative|Edge|Security] verb + object + context`. Where the
scenario tool's `[UI]/[API]/[Mobile]` TestType is also useful, put it first: `[API][BE-BL][Success] …`.
The scenario/test ID (`[TS-…]`/`[TC-…]`, per `rules/ai-sdlc-workflow.md`) is unchanged; the tag is in addition to it.

## 2. Dev rules
1. Rules live in the BE layer; FE calls them and never computes a rule itself.
2. Check what exists before adding (Existing Asset Scan / Reuse Table: `skills/ai-sdlc/phases/phase2-existing-asset-scan.md`, `skills/ai-sdlc/phases/phase2-reuse-table.md`).
3. Extending a shared function: additive and backward compatible, then re-run its callers' tests.
4. Anything that must equal another implementation (a port, a reference) is checked against values generated
   from that implementation, never hand-typed numbers.
5. Match the file you edit; no drive-by refactors.

## 3. QA rules
1. Three batches (Success, Alternative, Edge), approved one by one, then test data, then the scenario table.
2. Skeleton RED first, at an agreed seam; no test at a seam nobody agreed to.
3. A parity/comparison harness needs a negative control: break one reference value and the run must FAIL.
4. No fixed delays; one fix attempt on a failing test, then root-cause debugging.
5. FE behaviour that is visual is verified with a real screenshot against a reference, not by mirroring the formula.

## 4. Per-project mapping
Each project says which folders are BE and FE in its own docs (e.g. a `DEV_QA_PATTERN.md` next to the project's code), not here.
