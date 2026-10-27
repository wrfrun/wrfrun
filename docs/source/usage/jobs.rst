Jobs
====

``wrfrun jobs`` lists active runs recorded by the current project's
``status.json`` files:

.. code-block:: console

   $ wrfrun jobs

Use a different main configuration file when the project uses a non-default
location:

.. code-block:: console

   $ wrfrun jobs --config /path/to/project/config.toml

Follow the standard output of the command currently running in one run:

.. code-block:: console

   $ wrfrun jobs --follow 20261026T143012-a1b2c3d4

Use ``--stream stderr`` to follow standard error instead. Following stops
after the run reaches a terminal state.

Following starts with at most the latest 100 complete lines. New output is
read in 64 KiB blocks and prints at most 1 MiB per polling cycle. If more than
16 MiB accumulates while the terminal is behind, ``wrfrun`` skips that backlog
and reports its size before continuing from the newest output.
