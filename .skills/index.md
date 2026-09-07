# Development skills

## Shared implementation principles

Keep implementations direct, readable, and no more complex than the current
contract requires.

- Rely on validation already performed by the framework or the immediate I/O
  operation. Do not add a second preflight check unless it changes the error,
  prevents an unsafe mutation, or establishes a boundary the lower layer
  cannot enforce.
- Introduce a helper only when it captures a meaningful domain concept or
  removes substantial repetition. Keep a short operation at its call site
  when a helper would merely hide one or two lines of control flow.
- Prefer the smallest complete implementation over speculative branches,
  abstractions, and future-facing options. Add complexity only when a current,
  observable requirement needs it.
- Do not pursue generality before the simple implementation meets the current
  requirement. Extend it only after a concrete need is established.
- Before changing an implementation, discuss the proposed plan with the user
  and begin editing only after the plan is confirmed.
- Unless the user explicitly asks to change a target, keep the work read-only:
  inspect, analyze, and report findings without editing code, configuration, or
  documentation.

## Current runtime architecture

Use this architecture for new or refactored code. The older ``WRFRUN`` proxy,
``WRFRUNURI``, ``ExecutableDB``, and modules under ``wrfrun/workspace/`` are
compatibility code, not templates for new work.

- ``WRFRunContext`` creates a session on entry. Access runtime services through
  ``WRFRUN_NEW`` only while that session is active.
- ``ConfigService`` loads enabled model plugins. A model plugin registers its
  executable classes, workspace init/check hooks, and model resource providers
  into the active session.
- Use ``ResourceRef`` to represent a resource. Resolve package and filesystem
  resources with ``WRFRUN_NEW.resource`` immediately before the operation that
  needs a ``Path``.
- ``ExecutableRegistry`` is session-local and is also used by replay. Register
  executable classes from the model plugin rather than at module import time.

| File | Purpose |
| --- | --- |
| [Executables.md](Executables.md) | Implement or modify `wrfrun` external-program executables, including input staging, command execution, output collection, recording, replay, registration, and wrappers. |
| [Documentation.md](Documentation.md) | Synchronize user-facing and contributor documentation with public APIs, configuration, workflows, workspaces, and package resources. |
| [Resources.md](Resources.md) | Add or modify static package resources, including templates, scripts, generated resource constants, URI use, and install wiring. |
| [Workspace.md](Workspace.md) | Add or modify model workspaces, including URI-backed paths, static runtime-resource staging, preparation, validation, and safe cleanup. |
