# Implement `wrfrun` Executables

Use this guide when adding or changing an `ExecutableBase` subclass, its replay registration, or its convenience wrapper. Treat `wrfrun/core/base.py` as the source of truth when this guide and the implementation differ.

## Preserve the execution contract

Model an external program through three explicit parts:

- **Input**: configuration, data, and any content supplied through standard input.
- **Command**: the program and its command-line arguments.
- **Output**: model-generated result files and logs.

Inherit from `ExecutableBase` and call `super().__init__` with:

- `name`: a stable identifier for the executable.
- `cmd`: the command to execute.
- `work_path`: the directory in which to run it.

Pass `mpi_use`, `mpi_cmd`, `mpi_core_num`, and `stdin_file` only when the executable needs them. Prefer a list of command arguments for non-MPI commands. Do not depend on shell expansion, pipes, or redirection: commands run with `shell=False`. In the current implementation, an MPI command must be provided as a string.

Choose a stable, flow-unique `name`, normally based on the external program. The default archive directory is `<output_path>/<name>`, so the name determines the output and log location.

## Prepare inputs correctly

In `before_exec`:

1. Validate the active `wrfrun` context and set the appropriate work status when the model requires it.
2. Register existing input files with `add_input_files`.
3. Generate configuration files and other dynamic inputs in the required working directory.
4. Call `super().before_exec()` after registering all files so the base class creates their symbolic links.

`add_input_files` links files into the specified directory; it does not copy files or generate content. Provide a complete file configuration when the destination filename or destination directory must differ from the source.

For standard input, generate or locate a file first and pass its path through `stdin_file` in the parent constructor. Do not put `< input-file` in `cmd`; the base class opens the file and supplies it to the subprocess directly.

## Collect outputs correctly

In `after_exec`:

1. Register model-generated result files and any extra log files with `add_output_files`.
2. Use `filenames`, `startswith`, or `endswith` narrowly enough to avoid collecting unrelated workspace files.
3. Call `super().after_exec()` to move the registered files to their archive paths.
4. Emit a completion log only after the parent call succeeds.

The base `exec` method automatically saves command output as `<name>.stdout` and `<name>.stderr` under the executable log directory. Do not register those streams again with `add_output_files`.

## Support recording and replay

When state outside the base configuration is required to reproduce a run, implement both methods:

- Put the state into `self.custom_config` in `generate_custom_config`.
- Restore that state in `load_custom_config`.

Save constructor arguments that are required to construct the class during replay in `self.class_config["class_args"]` or `self.class_config["class_kwargs"]`.

Register replayable classes with `ExecutableDB` during module import. Use the same ID as the instance `name`; replay resolves the class by the recorded name.

```python
def _exec_register_func(exec_db: ExecutableDB):
    if not exec_db.is_registered("my_program"):
        exec_db.register_exec("my_program", MyProgram)


WRFRUN.set_exec_db_register_func(_exec_register_func)
```

Only override `replay` when loading the recorded configuration and invoking the instance is insufficient.

## Keep framework hooks intact

Do not override `export_config`, `load_config`, `add_input_files`, or `add_output_files` for ordinary model integration. They preserve the shared recording and file-handling contract.

Prefer the inherited `exec` and `__call__` methods. Override either only when the execution mechanism or order genuinely differs, and preserve return-code checking, stdout/stderr logging, fake-simulation behavior, recording, and replay semantics. For example, `UnGrib` overrides `__call__` to run `link_grib` before its main command.

Use `before_exec_debug`, `exec_debug`, and `after_exec_debug` only for diagnostics that belong at those lifecycle points.

## Define upstream and downstream handoffs explicitly

Do not assume that `wrfrun` automatically finds outputs from a preceding executable. Define each handoff explicitly:

- Identify the required files, their source directory, and their destination in the new executable workspace.
- Check the active workspace first.
- If it is empty and a documented fallback is appropriate, check the specific upstream archive directory.
- Verify at least one required file rather than treating an existing directory as valid input.
- Raise an actionable error when no valid input is available.

Use `MetGrid` as the reference pattern for a WRF `geogrid`/`ungrib` handoff, but do not copy its filenames or fallback rules into unrelated executables.

## Provide a wrapper when it improves the public API

Add a function wrapper for commonly used executables. Expose meaningful business parameters, apply project defaults, document the lookup behavior for `None`, and construct and invoke the executable in one place.

```python
def my_program(input_path: str | None = None):
    MyProgram(input_path=input_path)()
```

Keep wrappers thin: lifecycle preparation, file staging, and output collection belong in the executable class.

## Validate the change

Before handing off an executable change:

1. Check that every required source file is linked to the intended workspace name.
2. Run the executable or a focused substitute and verify result files, stdout, and stderr reach their expected archive paths.
3. When recording is supported, record one run and replay it to verify constructor arguments, custom configuration, and `ExecutableDB` registration.
4. Test MPI behavior only with the intended launcher; do not assume Open-MPI-specific flags work with every launcher.
