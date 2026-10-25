Profiles
========

Profiles save a project's model configuration and namelist settings so that a
new project can start from the same experiment on this or another machine.
They also include custom scheduler scripts under ``configs/scheduler/`` and
the selected experiment directory. They do not include model installations,
input data, outputs, logs, or run workspaces.

Save and list profiles
----------------------

Save the ``v01`` experiment in the local profile library:

.. code-block:: console

   $ wrfrun save --experiment v01 --global ideal-building

The library follows the operating system's standard user configuration
location. List its saved profiles with:

.. code-block:: console

   $ wrfrun save --list

Remove a profile from the same library with:

.. code-block:: console

   $ wrfrun save --remove ideal-building

To transfer a profile to another machine, save it to a ZIP file instead:

.. code-block:: console

   $ wrfrun save --experiment v01 ideal-building.zip

Load a profile
--------------

``load`` always creates a new project directory and refuses to use an existing
one:

.. code-block:: console

   $ wrfrun load --global ideal-building --path ./ideal-building-case
   $ wrfrun load ideal-building.zip --path ./ideal-building-case

After loading on another machine, update installation paths, geography data
paths, and input data for that machine before running the project.
