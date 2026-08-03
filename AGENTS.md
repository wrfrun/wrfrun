# wrfrun Agent Instructions

These instructions apply to the entire repository.

## Development Skills

Repository-specific development skills are stored in `.skills/`. Consult `.skills/index.md` when a task matches one of the listed workflows, and follow the linked skill before changing the associated implementation. Keep `.skills/` documentation aligned with the current code when its documented contract changes.

## Commit Messages

When you are asked to create a git commit, use one of the following two commit message styles.

Do not invent a different format unless the user explicitly asks for it.

### 1. Single-target change

Use this format when the commit is for one specific purpose, such as:

- updating the version
- fixing one bug
- updating one focused part of the docs

Format:

```text
Update version to vX.Y.Z
```

or

```text
Bug fix: short description
```

Other short imperative titles like `Update development docs.` are also acceptable when the change is clearly narrow and focused.

Guidelines:

- Keep the title short.
- Describe the main target directly.
- Do not add a long body unless the user asks for one.

### 2. Detailed multi-file change log

Use this format when multiple files are changed and the commit needs a structured summary.

The commit title should be:

```text
change log
```

If needed, a short note may appear on the same title line after `change log`, as seen in project history, but plain `change log` is the default.

Recommended body structure:

```text
Changes:

    path/or/group: summary

New Files:

    path: summary

Renamed:

    old/path -> new/path

Deleted:

    path: summary
```

Guidelines:

- Only include sections that are relevant to the commit.
- Keep section names exactly as:
  - `Changes`
  - `New Files`
  - `Renamed`
  - `Deleted`
- Leave a blank line after each section title.
- Indent body entries with four spaces.
- Group related file paths when that makes the summary clearer, for example `docs/*` or `wrfrun/workspace/*`.
- In `Renamed`, prefer the form `old/path -> new/path`.
- In `Changes`, use either:
  - one summary line per file or file group, or
  - a short numbered list under one file path when several related edits happened in the same file

### Examples

Short single-target commit:

```text
Update version to v0.3.3
```

Bug-fix commit:

```text
Bug fix: Scheduler script not generated properly
```

Detailed multi-file commit:

```text
change log
Changes:

    wrfrun/workspace/*: Add new function to check PALM workspace.

    wrfrun/scheduler/*: Add new function to provide unified submit interface.

Renamed:

    docs/source/api/scheduler.script.rst -> docs/source/api/scheduler.core.rst

    wrfrun/scheduler/script.py -> wrfrun/scheduler/core.py
```

## Workflow Note

Do not create commits unless the user explicitly asks for a commit.

If the user asks for a commit, choose the commit message format above based on the scope of the change.
