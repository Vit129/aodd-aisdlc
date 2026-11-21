# Swift adapter

**Status: examples NOT compiled; no Swift toolchain run for this document.**

## SwiftPM target graph
Put headless logic in its own targets. The first guard checks the target graph: a headless target must not depend on a UI target, including transitively. In a test, run `swift package dump-package`, parse its JSON, and walk target dependencies from every mapped headless target; fail with the offending path and tell the developer to move the dependency behind a core port. Resolve conditional dependencies conservatively. Fixtures should include a graph with a forbidden dependency and assert the guard fails.

## Source scan
As a second check, scan mapped headless target folders for `import SwiftUI`, `import AppKit` and `import UIKit`, accounting for supported import forms. Scan UI-only folders for process-spawning APIs and report each occurrence with a fix: move process access to an io boundary. Maintain a project-specific list of APIs and cover it with a negative-control fixture. Test that every forbidden framework and process API is detected and that the guard fails on the fixture. A source scan cannot establish purity by itself.

## Literal policy
If the project chooses colour literals as a restricted kind, permit occurrences such as `Color(red:` only in the single mapped design-token file. Scan the UI folder and report all other occurrences; include a known-bad fixture. Account for syntax variations supported by the project.

## Optional warnings as errors
For headless targets, optionally pass `-warnings-as-errors` through the Swift compiler configuration, for example via SwiftPM target settings. This can make new compiler or dependency warnings break builds and does not itself prove layer purity; validate it on the supported toolchain.
