# Project Release Profiles

Use these profiles when scaffolding or reviewing a project's release/deployment workflow. They describe lifecycle differences, not hosting vendors. Select the closest profile from the project's actual stack and target; keep provider commands in the project-local adapter.

## Profile selection

| Profile | Typical artifact and gates | Target-specific adapter work |
|---|---|---|
| `web-public` | Versioned static/server build; unit/build checks; source revision included in deploy metadata | Public host deployment and a live URL/revision smoke check |
| `web-private` | Same web checks plus access-control/config validation; no secrets in the artifact | Private hosting target, authenticated smoke check, and environment/secret handling |
| `mobile` | Platform version/build number; test/analyze; signed platform bundles; store validation | Flutter or native build/signing; store upload/submission stays behind an explicit human approval gate |
| `desktop` | App version; platform build/package; signing/notarization and updater-feed checks where applicable | OS-specific archive/package and release channel, such as a macOS app release |
| `game` | Game/build version; engine tests and exports for declared platforms; artifact integrity check | Distribution channel and platform export/import smoke test |
| `plugin` | Plugin manifest version, supported-host compatibility matrix, package/install test | Marketplace or GitHub release; validate the package in a clean host fixture before publish |
| `none` | No production release or versioned artifact | No release/deploy script; document the reason only if future distribution is expected |

A project may combine artifact and host characteristics (for example, `web-public` with GitHub Pages). Do not create a profile per repository name. Split a new profile only when its release lifecycle has different artifacts, gates, approval boundaries, or verification needs.

When the target is known from project requirements or existing configuration, use it without asking again. If public/private visibility, store submission, signing ownership, or production approval is unknown, ask before generating a live publish step.

## Project-local contract

For every publishable profile, create or adapt a local entry point, a profile/config, and a test that uses fake commands or a dry-run adapter. The entry point uses the project's native tools and records the selected profile and its concrete commands; AODD does not inject provider commands into arbitrary repositories.

Record at least: profile name; version source/format; source and shared dependency identity; test/build/package steps; artifact location; release channel; deploy target; verification method; credential environment variable names; and which steps require human approval. Keep command arguments as structured project-native configuration where practical; never store credentials in the profile.

The local workflow must:

1. **Plan first:** show the version, source commit, dependency/shared-repo revisions, artifact, release channel, and deployment target before side effects. Support a non-interactive dry-run.
2. **Validate the source:** require the project's chosen protected release branch to be clean and synchronized; pin or verify external/shared inputs. Run required tests, security checks, build, signing, and packaging before publishing.
3. **Use one release identity:** keep the app/package version, changelog, tag, hosted release, built artifact, and deployed revision tied to the same source and dependency commits. Build once and promote that artifact when the host supports it.
4. **Separate release from deploy:** allow deploy-only only for an identified released artifact. A development snapshot must have a distinct preview/staging route and must not silently replace production.
5. **Resume safely:** detect which commit, version, tag, hosted release, and deployment already succeeded. Retry the missing step for the same version; never bump to the next version just because a later step failed. Preserve ambiguous dirty user changes and report exact recovery steps.
6. **Gate external actions:** store signing and deployment credentials outside the repo. Require human approval for store submissions, production changes, paid services, or other irreversible actions as required by AODD.
7. **Verify and record:** check the live URL, installed package, store artifact, update feed, or host fixture against the expected version/source. Append a concise project-local deployment record with target, version, source/dependency revisions, time, outcome, and recovery notes.

## Acceptance checks

- `--dry-run` reports the complete release plan and changes no files or remote state.
- Tests prove version planning and retry selection without contacting a real host or store.
- A failed preflight cannot tag, publish, or deploy.
- A simulated failure after tagging resumes that same version.
- A production deploy rejects dirty/uncommitted inputs and verifies its resulting revision.
- A store submission or other irreversible step remains behind explicit human approval.
