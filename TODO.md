# Runtime Hardening Plan

This plan is derived from a read-through of the current `wrfrun` runtime path, with focus on context setup, workspace preparation, scheduler submission, and replay flow.

## Goals

- Make startup and submission behavior deterministic.
- Reduce destructive or stale filesystem behavior.
- Make replay mode and scheduler integration safe to fail.
- Preserve the current public API where practical, but prefer correctness over accidental behavior.

## Phase 1: Fix correctness bugs on the critical path

- [x] Fix `wrfrun.workspace.core.check_workspace()` to return the computed `flag` instead of always returning `True`.
- [x] Add coverage for broken workspace detection:
  - [x] missing workspace root
  - [x] missing replay workspace
  - [x] missing output path
  - [x] missing model-specific workspace
- [x] Make scheduler submission dispatch by configured backend instead of always calling `qsub`.
- [x] Add an explicit scheduler submit layer, for example:
  - [x] `pbs -> qsub`
  - [x] `slurm -> sbatch`
  - [x] `lsf -> bsub < run.sh` or equivalent non-interactive form
- [x] Ensure scheduler mismatch fails early with a clear error message.
- [x] Make replay mode cleanup exception-safe:
  - wrap `IS_IN_REPLAY = True` / reset in `try/finally`
  - do this for both `replay_simulation()` and `replay_executables()`
- [x] Review whether `WRFRUN.config.IS_RECORDING` also needs symmetric reset when recording ends.

## Phase 2: Make workspace preparation safer

- [x] Validate rebuild prerequisites before destructive cleanup in `prepare_workspace()` where possible.
- [x] Avoid deleting the entire workspace root before model-specific checks succeed.
- [x] Decide on one safe strategy for workspace rebuild:
  - preflight validation, then delete and rebuild
  - build into a temporary directory, then swap into place
- [x] Expand model-specific workspace validation coverage:
  - [x] add PALM checker
  - [x] add ROMS checker if ROMS runtime depends on prepared directories (skip ROMS for now)
- [x] (Diffcult to check files)Review whether `check_wrf_workspace()` should verify expected links/files, not just directory existence.
- [x] Make re-init behavior visible in logs so users can distinguish:
  - clean run
  - forced rebuild
  - partial/broken previous workspace

## Phase 3: Reduce filesystem fragility in model setup

- [x] Audit all symlink-heavy setup paths for failure behavior and idempotency.
- [x] In WRF workspace setup, verify required source subpaths before creating any links.
- [x] Decide how to handle pre-existing targets:
  - fail clearly
  - replace explicitly
  - skip when already correct
- [x] Rework PALM `JOBS` handling to avoid mutating the user installation in a surprising way.
- [x] If PALM still requires installation mutation, add:
  - explicit warning in docs
  - rollback/restore strategy
  - stronger guardrails around deleting backup dirs

## Phase 4: Harden subprocess and shell boundaries

- [x] Replace `subprocess.run(" ".join(command), shell=True, ...)` with argument-safe execution where possible.
- [x] Quote or avoid shell interpolation for:
  - [x] executable paths
  - [x] `python_interpreter`
  - [x] entry script path
  - [x] scheduler env values
- [x] Review generated `run.sh` for path safety when directories contain spaces or shell metacharacters.
- [x] Decide which scheduler-specific commands truly require shell behavior and isolate that logic to a small boundary.
- [x] Preserve useful stdout/stderr logging while improving command safety.

## Phase 5: Make replay flow isolated and deterministic

- [ ] Stop unpacking every replay archive into one shared replay directory.
- [ ] Choose a replay workspace strategy:
  - per-replay temp directory
  - unique run-id subdirectory under replay workspace
- [ ] Clear or isolate extracted replay state before reading `config.json`.
- [ ] Ensure stale files from an older replay cannot satisfy a new replay load.
- [ ] Decide whether replay should clean extracted files after success/failure.
- [ ] Add failure cases for:
  - invalid archive
  - missing `config.json`
  - partial unpack
  - replay file name collisions

## Phase 6: Revisit global runtime state

- [ ] Review the impact of process-global `WRFRUN` state on:
  - nested contexts
  - repeated runs in one interpreter
  - tests
  - future parallel execution
- [ ] Review whether `ExecutableBase.__new__()` singleton behavior is intentional for each executable class.
- [ ] If singleton behavior is not required, remove it.
- [ ] If singleton behavior must remain, document the invariants and reset mutable per-run state explicitly.
- [ ] Confirm replay does not inherit stale `input_file_config`, `output_file_config`, or custom config from prior calls unintentionally.

## Phase 7: Fix config bootstrap inconsistencies

- [ ] Reconcile `WRFRunConfig.from_config_file()` with `load_wrfrun_config()` so missing-config bootstrap works as documented.
- [ ] Decide how first-run config creation should obtain `work_dir` before the config exists.
- [ ] Ensure error messages match actual behavior for:
  - missing main config
  - missing included model config
  - invalid include path

## Phase 8: Add targeted tests around runtime behavior

- [ ] Add tests for context entry/exit behavior around:
  - normal execution
  - scheduler submit path
  - replay failure
  - replay generator early exit
- [ ] Add tests for scheduler script generation and scheduler submit command selection.
- [ ] Add tests for workspace rebuild behavior when directories are partially missing.
- [ ] Add tests for replay extraction isolation and stale-file resistance.
- [ ] Add tests for subprocess invocation with paths containing spaces.

## Open design questions

- Q: Should `submit_job=True` submit and `exit(0)`, or should submission be exposed as a more explicit operation?
  A: Submit and `exit(0)` for now.
- Q: Should replay require a clean workspace, or be allowed to overlay an existing one?
  A: Clean workspace.
- Q: Should PALM workspace prep ever mutate the installation tree, or should `wrfrun` require a user-managed runtime copy?
  A: Require a copy is better, but we can mutate the installation tree for now.
- Q: Is preserving backward-compatible behavior around global singletons worth the runtime risk?
  A: Preserving backward-compatible behavior around global singletons for now, postpone redesign.

## Recommended implementation order

1. Fix Phase 1 first. These are correctness bugs in the main runtime path.
2. Then do Phases 2 and 5 together, because workspace and replay isolation are tightly related.
3. Then do Phase 4, since safer subprocess handling reduces hidden scheduler/runtime failures.
4. After that, decide the larger architectural direction in Phases 6 and 7.
5. Keep Phase 8 running alongside each change rather than leaving it all to the end.
