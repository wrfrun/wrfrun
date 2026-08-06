# Manage `wrfrun` Resources

Use this guide when adding, removing, or changing static files distributed with `wrfrun`, including configuration templates, namelist templates, scheduler templates, extension scripts, and CLI project templates. Treat `wrfrun/res/`, its `name_map.json` files, and the matching `meson.build` files as the source of truth.

## Keep resource ownership clear

Store package-distributed, static files under `wrfrun/res/`:

- `config/`: main and model TOML templates.
- `extension/`: non-Python extension scripts.
- `namelist/`: built-in namelist and parameter-table templates.
- `scheduler/`: job-scheduler templates.
- The resource root: shared templates such as the run-script template and Git ignore rules.

Do not place model installation files, user input data, or per-run generated files in `wrfrun/res/`. Workspace preparation owns installation-derived runtime resources; executable lifecycle code owns generated configuration, run-specific inputs, and outputs.

## Use generated constants and resource URIs

Import resource constants from `wrfrun.res` instead of hard-coding repository or installation paths. Generated constants contain URIs such as `:WRFRUN_RESOURCE_PATH:/config/config.template.toml`.

Before passing a resource URI to any filesystem API, resolve it with `WRFRUN.uri.parse_resource_uri(...)`. `WRFRUN.config.parse_resource_uri(...)` remains a compatibility interface, but new code should use `WRFRUN.uri`.

Importing `wrfrun.res` registers `WRFRUN_RESOURCE_PATH`. Do not create an additional URI namespace for an ordinary resource file.

## Declare resources in `name_map.json`

Each resource directory must declare its direct children in `name_map.json`:

```json
{
    "physical-file-name": {
        "name": "UPPER_SNAKE_CASE_NAME",
        "type": "file"
    }
}
```

Use a unique, descriptive `UPPER_SNAKE_CASE` value for `name`. Set `type` to `file` for a file and `dir` for a child directory.

For a new directory:

1. Add its own `name_map.json` describing its direct children.
2. Add the directory to its parent's map with `type: "dir"`.
3. Repeat through every parent to `wrfrun/res/name_map.json`.

`generate_init.py` only exports declared resources and only descends into entries marked as directories. It does not discover undeclared files.

## Regenerate and install resources

Do not edit `wrfrun/res/__init__.py` manually. Regenerate it after changing a resource or any name map:

```bash
python wrfrun/res/generate_init.py -o wrfrun/res/__init__.py
```

`build.sh` also runs this command before packaging.

Update the relevant `meson.build` `py3.install_sources(...)` list whenever adding or removing a resource file. For a new top-level resource directory, add its subdirectory declaration in `wrfrun/res/meson.build`. A generated constant can resolve in the source tree while still referring to a missing file in an installed package if the build wiring is absent.

## Add a model TOML template

Use model TOML templates for concise, high-value settings; do not use them to replace a model's full namelist or parameter-table interface. Keep complex or uncommon settings in user-provided model configuration.

The precise merge order is model-specific. Prefer this order unless the model contract requires otherwise:

1. Read the base template.
2. Apply settings derived from the model TOML configuration.
3. Apply the user-provided namelist or parameter table last.

Verify the actual model initialization code before documenting or relying on that order.

When adding a model TOML template:

1. Add `<model>.template.toml` in `wrfrun/res/config/`.
2. Add its mapping to `wrfrun/res/config/name_map.json` and regenerate `wrfrun/res/__init__.py`.
3. Add the file to `wrfrun/res/config/meson.build`.
4. Add the model's `use` and `include` entry to `wrfrun/res/config/config.template.toml`.
5. If `wrfrun init --models ...` or `wrfrun add ...` should support the model, import and register the generated constant in `wrfrun/cli.py`'s `MODEL_MAP`.
6. Keep template keys synchronized with the model, workspace, executable, and documentation consumers that implement them.

## Validate the change

Before handing off a resource change:

1. Validate each modified `name_map.json` and verify every declared path exists.
2. Regenerate `wrfrun/res/__init__.py` and confirm the new constant is exported through `__all__`.
3. Initialize the URI manager and verify `WRFRUN.uri.parse_resource_uri(...)` resolves the new constant to an existing file.
4. For a TOML template, verify its main-config include, model loading behavior, and downstream consumers use the same keys.
5. Run the relevant package-install or build validation to confirm every new resource is installed, not merely present in the source tree.
