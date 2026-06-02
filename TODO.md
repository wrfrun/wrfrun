# wrfrun Roadmap

## Positioning

`wrfrun` should evolve toward a research infrastructure with two priorities:

1. Reproducible and stable numerical simulation workflows.
2. A lower entry barrier for new users learning how to run numerical models.

This means the core should optimize for correctness, traceability, and recovery, while the user-facing layer should optimize for guided usage, good defaults, and smooth first success.

## Current Assessment

Based on the current codebase, `wrfrun` already has a solid foundation:

- Unified execution abstraction via `ExecutableBase`
- Context-based orchestration via `WRFRun`
- Workspace preparation and output organization
- Scheduler integration for PBS, Slurm, and LSF
- Record and replay support
- Initial documentation and configuration templates
- Partial support for multiple models

The project is no longer in the "add basic features as fast as possible" stage. The next phase should focus on turning existing capabilities into a more trustworthy and easier-to-adopt system.

## Guiding Principles

- Prefer reliability improvements over scattered new features.
- Prefer better onboarding over more configuration surface.
- Turn personal workflow experience into explicit product behavior.
- Keep extensibility, but provide stronger defaults and recommended paths.
- Do not rebuild the architecture without a clear operational payoff.

## Phase 1: Make The Core More Trustworthy

Goal: strengthen `wrfrun` as a reproducible and stable research infrastructure.

- [ ] Audit critical runtime paths and remove fragile behavior in context setup, workspace preparation, scheduler submission, and replay flow.
- [ ] Improve preflight validation so common configuration and environment problems fail before a run starts.
- [ ] Standardize error messages so they answer three questions: what failed, why it failed, and what the user should do next.
- [ ] Record more execution metadata for reproducibility:
  - Python version
  - wrfrun version
  - host and scheduler environment
  - model paths and key runtime settings
- [ ] Define a clearer reproducibility contract for `.replay` files:
  - what is guaranteed to be reproduced
  - what depends on external environment
  - what is intentionally excluded
- [ ] Strengthen log organization and output indexing so a finished run is easier to inspect after the fact.
- [ ] Review recovery behavior for interrupted runs and clarify what can be resumed safely.
- [ ] Add regression tests for config loading, workspace preparation, scheduler script generation, and replay behavior.

## Phase 2: Improve The First-Run Experience

Goal: make `wrfrun` much easier for new users to adopt successfully.

- [ ] Design a "first successful run" path and make it the primary beginner workflow.
- [ ] Provide a minimal runnable example project with:
  - a clear directory layout
  - ready-to-edit config files
  - a short script showing the normal execution path
- [ ] Add a project initialization command or helper that creates:
  - `config.toml`
  - model config files
  - recommended directory structure
  - optional example script
- [ ] Improve template configuration files with beginner-friendly comments and safer defaults.
- [ ] Add a validation command such as a dry-run or doctor mode to check environment, paths, and core config before execution.
- [ ] Reduce hidden behavior where possible; when behavior is automatic, document it clearly in logs and docs.
- [ ] Write a short "How wrfrun works" guide aimed at new users:
  - workspace
  - config layering
  - executable lifecycle
  - outputs and logs
  - replay basics

## Phase 3: Turn Documentation Into Guided Learning

Goal: make `wrfrun` useful not only as a tool, but also as an entry point for learning numerical-model workflows.

- [ ] Reorganize docs into three paths:
  - beginner path
  - daily-use path
  - developer/extender path
- [ ] Create a step-by-step beginner tutorial that explains not only what to run, but why each step exists.
- [ ] Add troubleshooting pages for the most common failure cases:
  - bad paths
  - missing executables
  - invalid namelist settings
  - scheduler submission problems
  - replay misunderstandings
- [ ] Add "mental model" documentation for core concepts instead of only API descriptions.
- [ ] Add more examples that reflect real workflows rather than isolated functions.
- [ ] Make docs consistently show the recommended path first, advanced flexibility second.

## Phase 4: Make Extensibility More Explicit

Goal: preserve architectural flexibility while making the framework easier to extend correctly.

- [ ] Define a clearer extension story for:
  - new models
  - new preprocessing steps
  - new scheduler backends
  - custom executables
- [ ] Review current registration points and document them as public extension surfaces vs internal implementation details.
- [x] Create a minimal "add your own executable/model" tutorial based on the current architecture.
- [ ] Add tests or validation helpers for extension authors so integrations fail earlier.
- [ ] Clarify which APIs are stable and which are still experimental.

## Phase 5: Expand Carefully, Not Broadly

Goal: continue capability growth without returning to feature sprawl.

- [ ] Finish the most important missing pieces in WRF support before broadening too far.
- [ ] Expand model coverage only when the integration can meet the same standards for reproducibility, logging, and usability.
- [ ] Treat dashboard or visualization features as secondary until core reliability and onboarding improve.
- [ ] Prefer deeper support for fewer workflows over shallow support for many workflows.

## Near-Term Priorities

These should be the highest-priority items.

- [ ] Review current failure points in `WRFRun`, workspace preparation, scheduler submission, and replay.
- [ ] Add a preflight validation command or equivalent check flow.
- [ ] Define and document the reproducibility contract for replay files.
- [ ] Create one minimal, beginner-oriented runnable example.
- [ ] Rework config templates and quick-start docs around the first-run experience.

## Mid-Term Priorities

- [ ] Build a stronger testing baseline for infrastructure behavior.
- [ ] Improve recovery and resume semantics.
- [ ] Reorganize documentation into guided learning paths.
- [ ] Clarify extension APIs and write extension-oriented tutorials.
- [ ] Complete the most important missing support in WRF workflows.

## Explicit Non-Priorities For Now

To avoid drifting back into low-leverage work, the following should not be the main focus right now.

- [ ] Do not redesign the whole framework around a new abstraction unless it clearly improves reliability or onboarding.
- [ ] Do not broaden model support aggressively before the current core is more trustworthy.
- [ ] Do not spend major effort on dashboards before logs, validation, and recovery behavior are stronger.
- [ ] Do not add advanced options for every edge case before the recommended beginner path is polished.

## Success Criteria

This roadmap is working if, over time, the project moves toward the following outcomes:

- A new user can complete a first run with less confusion and fewer hidden steps.
- An experienced user can trust that runs are easier to reproduce, audit, and recover.
- Extension authors can tell which parts of the framework are intended to be extended.
- The project grows in depth and quality, not just in surface area.
