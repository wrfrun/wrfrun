Runtime Services and Session Development
########################################

Runtime services are created for one simulation session. They must not retain
state from a previous experiment or run, and they must not require a model
package to be imported before the session is configured.

Service ownership
*****************

:func:`create_wrfrun_session <wrfrun.core.core.create_wrfrun_session>` assembles two groups of services:

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Group
     - Services
   * - Runtime
     - I/O, resources, executable registry, replay, command runner, workspace
       coordination, and run status.
   * - State
     - Loaded configuration, loaded namelists, and mutable execution flags.

The session is held in a ``ContextVar``. :data:`WRFRUN <wrfrun.core.core.WRFRUN>`
is a port to the session, not a process-wide store. Accessing it without an
active :class:`~wrfrun.run.WRFRunContext` raises :class:`WRFRunContextError <wrfrun.core.error.WRFRunContextError>`.

Resource paths and run identity
*******************************

:class:`~wrfrun.core.runtime.resource.RunLayout` gives one run its experiment,
run ID, input directory, output archive, latest-results directory, log
directory, workspace, replay directory, and temporary directory. It is
created after configuration and before plugins register model-specific
resources.

Represent a resource with :class:`~wrfrun.core.type.ResourceRef`; resolve it
only immediately before an operation needs a real :class:`pathlib.Path`.

.. code-block:: python

   from wrfrun.core import ResourceRef, WRFRUN

   table = ResourceRef("workspace_my_model", "tables/physics.tbl")
   table_path = WRFRUN.resource.get_custom_resource(table)

Use :meth:`get_package_resource <wrfrun.core.runtime.resource.ResourceCatalog.get_package_resource>` for a bundled package resource and
:meth:`get_custom_resource <wrfrun.core.runtime.resource.ResourceCatalog.get_custom_resource>` for a project or runtime filesystem resource. Do not
store machine-specific absolute paths in a module-level variable.

Workspace hooks
***************

The core workspace service owns common run directories and invokes hooks
registered by enabled model plugins. A model hook owns only static,
installation-derived runtime files such as a linked binary or immutable table.
An executable owns generated namelists, run-specific inputs, and outputs.

Register hooks and a model provider in the plugin:

.. code-block:: python

   from wrfrun.core import WRFRUN

   def register(self):
       WRFRUN.workspace.register_init_func("my_model", prepare_my_model_workspace)
       WRFRUN.workspace.register_check_func("my_model", check_my_model_workspace)
       WRFRUN.resource.register_provider(
           "workspace_my_model",
           WRFRUN.resource.WORKSPACE_DIR / "my_model",
       )

The hooks must be repeatable and must not modify the model installation,
project input data, or output archive.

Commands, status, and replay
****************************

:class:`~wrfrun.core.runtime.runner.RunnerService` accepts a
:class:`~wrfrun.core.runtime.runner.Command` with an argument vector, working
directory, standard streams, environment, and optional timeout. It does not
use a shell. ``ExecutableBase`` normally owns command construction and sends
stdout and stderr to the executable log archive.

:class:`~wrfrun.core.runtime.status.RunStatusService` writes ``status.json``
beside the active run workspace. Job-management clients use it to locate the
current executable and log streams.

:class:`~wrfrun.core.runtime.record.ReplayService` records exported executable
configuration and can optionally package input data. Replay looks up classes
through the session-local executable registry, so the relevant model plugin
must be enabled before replay begins.

Adding a runtime service
************************

When a new shared service is justified:

1. Give it explicit dependencies through its constructor.
2. Add it to ``RuntimeService`` or ``StatesService``.
3. Construct it in :func:`create_wrfrun_session <wrfrun.core.core.create_wrfrun_session>` and expose it through ``WRFRUN``
   only if callers outside the session assembly need it.
4. Test a fresh session, a second independent session, and failure cleanup.
5. Do not make a service decide model-specific filenames, data formats, or
   namelist policy.

See :doc:`core development <develop_guide_core>` for the component map and
:doc:`executable development <develop_guide_executable>` for the lifecycle
that consumes these services.
