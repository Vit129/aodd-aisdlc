# Design

## Interface model

This is a command-line and agent-configuration product. Its interaction surfaces are Markdown instructions, agent skill prompts, hook messages, installer flags, and command output. There is no graphical user interface; visual layout specifications do not apply.

## Interaction principles

- Keep the human in control of consequential decisions and external actions.
- Make stage boundaries and approval points explicit.
- Show evidence for completion claims and preserve failed checks as failures.
- Keep optional modules opt-in and core behavior usable without them.
- Keep previews isolated from real agent homes and production state.

## Preview

Use the installer's dry-run mode with temporary home paths. It prints the planned file operations without installing the package. `make start` runs this preview after tests and syntax checks.

## Release gate

The release script runs `make start` on the versioned release commit before it creates or pushes the tag. A failed check stops publication.
