``wrfrun.res`` Development Guide
#################################

:doc:`wrfrun.res </api/res>` contains static files bundled with the Python
package. These files are installed with ``wrfrun`` and are independent of a
particular project, experiment, run, or model installation. The resource
system gives them stable Python references without hard-coding the package's
installation path.

Bundled resource types
**********************

The resource root is ``wrfrun/res/``.

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Location
     - Contents
   * - ``config/``
     - Main, experiment, and model TOML templates copied into a project by
       project operations.
   * - ``scheduler/``
     - Built-in scheduler submission-script templates.
   * - ``extension/``
     - Static scripts used by optional extensions.
   * - Resource root
     - Shared files such as the run-script template and Git ignore rules.

Do not put model installations, user input data, project namelist templates,
or files generated during a simulation in this package. Static installed model
resources belong to model workspace preparation; run-specific configuration,
inputs, and outputs belong to an executable lifecycle. See
:doc:`model development <develop_guide_model>` and
:doc:`executable development <develop_guide_executable>` for those boundaries.

Declaring a resource
********************

Every resource directory has a ``name_map.json`` that declares its direct
children. A file entry creates one exported constant; a directory entry allows
the generator to descend into that directory.

.. code-block:: json
   :caption: ``wrfrun/res/name_map.json``

   {
       "config": {
           "name": "CONFIG",
           "type": "dir"
       },
       "run.template.sh": {
           "name": "RUN_SH_TEMPLATE",
           "type": "file"
       }
   }

The ``name`` value must be descriptive and use ``UPPER_SNAKE_CASE``. The
``type`` value is either ``"file"`` or ``"dir"``. A new nested directory must
have its own map and must be declared as a directory by every parent map up to
the resource root.

.. important::

   ``name_map.json`` is parsed as strict JSON. Do not use comments, trailing
   commas, or notation such as ``"file" | "dir"`` inside it. An undeclared file
   may exist in the source tree but is not exported by the generator.

Generating Python references
****************************

``wrfrun/res/generate_init.py`` recursively reads the name maps and writes
``wrfrun/res/__init__.py``. Each generated constant is a
:class:`wrfrun.core.type.ResourceRef` whose provider is ``"core"``. Its name
combines the directory prefixes and the mapped name. For example,
``config/config.template.toml`` becomes ``CONFIG_MAIN_TOML_TEMPLATE``.

Generated constants are portable references, not absolute paths and not legacy
URI strings. The generated ``__init__.py`` is a build artifact; change the
resource file and maps, then regenerate it instead of editing a constant by
hand.

.. code-block:: console

   $ python wrfrun/res/generate_init.py -o wrfrun/res/__init__.py

``build.sh`` runs the same command before packaging. Regenerate explicitly
during development so the source tree and its exported ``__all__`` stay in
sync.

Loading a bundled resource
**************************

The active :class:`~wrfrun.core.runtime.resource.ResourceCatalog` registers
the ``core`` provider for the :doc:`wrfrun.res </api/res>` package. Resolve a
generated reference through the active session only when an operation needs a
real path:

.. code-block:: python

   from wrfrun.core import WRFRUN
   from wrfrun.res import CONFIG_MAIN_TOML_TEMPLATE

   template_path = WRFRUN.resource.get_package_resource(CONFIG_MAIN_TOML_TEMPLATE)
   text = template_path.read_text()

Use :meth:`~wrfrun.core.runtime.resource.ResourceCatalog.get_package_resource`
for a bundled resource. Use
:meth:`~wrfrun.core.runtime.resource.ResourceCatalog.get_custom_resource` for
a project or runtime filesystem resource. Do not reintroduce string URI
parsing or resolve a package path at module import time.

For the provider model, run layout, and ``ResourceRef`` behavior, see
:doc:`runtime services <develop_guide_runtime>`.

Adding or changing a resource
*****************************

Follow this sequence:

1. Add, rename, or remove the file under the appropriate ``wrfrun/res``
   directory.
2. Update that directory's ``name_map.json``. For a new directory, add its
   map and declare it as ``"dir"`` in its parent map.
3. Update the relevant ``meson.build`` so the file is installed in built
   distributions. For a new top-level directory, add its ``subdir(...)`` call
   to ``wrfrun/res/meson.build``.
4. Regenerate ``wrfrun/res/__init__.py`` and inspect the constant and
   ``__all__`` entry.
5. Update each consumer to import the generated constant, not a source-tree
   path.
6. Validate both a source checkout and an installed build when package layout
   changes.

.. important::

   A generated constant only proves that a name was declared. It does not prove
   that Meson installs the file. Keep ``name_map.json`` and ``meson.build`` in
   sync, or an installed package can be missing a resource that works in a
   source checkout.

Model TOML templates
********************

Model TOML templates are a special bundled resource because project operations
copy them when a model is enabled. Adding one requires more than placing a file
in ``res/config``:

1. Add ``<model>.template.toml`` under ``wrfrun/res/config/``.
2. Declare it in ``wrfrun/res/config/name_map.json`` and add it to
   ``wrfrun/res/config/meson.build``.
3. Regenerate :doc:`wrfrun.res </api/res>`.
4. Add the model's ``use`` and ``include`` entry to
   ``config.template.toml``.
5. Add the generated constant to ``MODEL_MAP`` in
   :doc:`wrfrun.core.operations.project </api/core.operations.project>`.
6. Keep its settings synchronized with the model plugin and executable
   consumers.

The template supplies concise model settings; it does not replace the complete
user-controlled namelist-template hierarchy. The model plugin owns creation of
that hierarchy. See :doc:`model development <develop_guide_model>`.

Validation
**********

For every resource change:

1. Parse each modified ``name_map.json`` and verify every declared file or
   directory exists.
2. Regenerate ``wrfrun/res/__init__.py`` and verify the expected
   :class:`~wrfrun.core.type.ResourceRef` is exported.
3. In an active session, resolve the constant with
   :meth:`~wrfrun.core.runtime.resource.ResourceCatalog.get_package_resource`.
4. Build an installed distribution and verify the same lookup finds the file.
5. Update the corresponding model, scheduler, CLI, and user documentation when
   the resource changes a public workflow.

Further reading
***************

- :doc:`Core architecture <develop_guide_core>` explains the session boundary.
- :doc:`Runtime services <develop_guide_runtime>` explains providers and
  resource resolution.
- :doc:`Model development <develop_guide_model>` explains model TOML and
  project-file integration.
- :doc:`API reference for wrfrun.res </api/res>` lists generated constants.
