Executable Development
######################

An :class:`~wrfrun.core.base.ExecutableBase` subclass adapts one external
program to the shared ``wrfrun`` lifecycle. It owns model-specific input
staging, generated configuration, command arguments, and output discovery;
core owns generic file operations, command execution, status updates,
recording, and result publication.

Lifecycle
*********

Calling an executable performs these steps:

1. ``before_exec`` stages registered inputs into its workspace.
2. ``exec`` runs the command through ``RunnerService`` and archives stdout and
   stderr in the executable log directory.
3. ``after_exec`` copies registered outputs to the output archive and publishes
   the latest result for that executable.

The base implementation also saves final namelists and command details after a
failed command. Prefer this lifecycle over a custom ``__call__`` method.

Minimal shape
*************

.. code-block:: python

   from wrfrun.core import ExecutableBase, ResourceRef, WRFRUN

   class MyProgram(ExecutableBase):
       def __init__(self, input_file: ResourceRef):
           super().__init__(
               name="my_program",
               cmd=["./my_program"],
               work_path=ResourceRef("workspace_my_model", "my_program"),
           )
           self.input_file = input_file
           self.class_config["class_args"] = (input_file,)

       def before_exec(self):
           self.add_input_files(self.input_file)
           WRFRUN.namelist.write_namelist(self.work_path / "my_program.nml", "my_program")
           super().before_exec()

       def after_exec(self):
           self.add_output_files(startswith="output_")
           super().after_exec()

``work_path`` is a :class:`ResourceRef <wrfrun.core.type.ResourceRef>`. The plugin must register its provider
before an instance is created. Register all inputs before calling
``super().before_exec()`` and all output patterns before calling
``super().after_exec()``.

Input and output handoffs
*************************

Use :meth:`add_input_files <wrfrun.core.base.ExecutableBase.add_input_files>` to declare each source and destination. The base
lifecycle links those inputs into the workspace. Resolve upstream output
sources explicitly; do not rely on an implicit search of a previous workspace.
Use :class:`~wrfrun.core.type.ResultSource` when a handoff needs a particular
executable, experiment, or run ID.

Use :meth:`add_output_files <wrfrun.core.base.ExecutableBase.add_output_files>` with narrow ``filenames``, ``startswith``, or
``endswith`` selectors. The base class archives these files below the active
output directory and atomically publishes ``results/<executable>`` as the
latest result. Do not register automatically captured stdout and stderr again.

Recording and replay
********************

Store constructor arguments needed to recreate the class in
:attr:`self.class_config <wrfrun.core.base.ExecutableBase.class_config>`. When additional state is needed, implement both
:meth:`generate_custom_config <wrfrun.core.base.ExecutableBase.generate_custom_config>` and :meth:`load_custom_config <wrfrun.core.base.ExecutableBase.load_custom_config>` to save and restore
:attr:`self.custom_config <wrfrun.core.base.ExecutableBase.custom_config>`. Replay uses the executable name to look up the class
in the session registry.

Register the class from the model plugin:

.. code-block:: python

   def register(self):
       WRFRUN.registry.register_exec("my_program", MyProgram)

Use the same stable identifier for the registry and :attr:`ExecutableBase.name <wrfrun.core.base.ExecutableBase.name>`.

Validation
**********

Test the smallest complete contract:

1. Required inputs appear at the expected workspace paths.
2. The command receives an argument vector, working directory, streams, and
   standard input exactly as intended.
3. Outputs, stdout, stderr, and final namelists reach the expected archive.
4. A failed command leaves failure artifacts in the executable log directory.
5. A recorded run can recreate the class after its model plugin is loaded.

See :doc:`runtime services <develop_guide_runtime>` for workspace providers and
session paths, and :doc:`model development <develop_guide_model>` for model
plugin integration.
