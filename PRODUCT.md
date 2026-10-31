# Product

## Purpose

AODD and ai-sdlc are installable agent-workflow packages. They provide operating rules, skills, hooks, scripts, and optional modules for Claude Code and OpenAI Codex. AODD keeps the human responsible for decisions and requires evidence and independent review before a medium or large task is reported complete. ai-sdlc defines the gated design, QA, implementation, and verification flow.

## Users and interface

The users are people configuring coding agents. The product interface is the installed command-line agent environment: prompts, skills, hooks, and installer options. This repository does not ship a graphical application.

## Supported delivery

- Preview installation changes with `./install.sh --dry-run --all --codex` using temporary agent-home paths.
- Run the repository checks with `make start`.
- Install into an agent home only by explicitly running the installer with the intended target and options.

## Out of scope

The package does not make product decisions, publish releases, or install optional schedules unless the user explicitly chooses those actions.
