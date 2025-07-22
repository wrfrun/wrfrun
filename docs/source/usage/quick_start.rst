Quick start
###########

We will simulate Hurricane Matthew with a single domain in this section. You can check the corresponding tutorial page in `WRF–ARW Online Tutorial <https://www2.mmm.ucar.edu/wrf/OnLineTutorial/CASES/SingleDomain/index.php>`_ to learn more about this case and WRF model.

Prerequisite
************

Environment
===========

You need to have WRF installed. `WRF-Install-Script <https://github.com/bakamotokatas/WRF-Install-Script>`_ can help you install WPS and WRF on Ubuntu based Linux operating systems conveniently.

Also make sure you have installed ``wrfrun``.

Data
====

Download the `Matthew case study data <https://www2.mmm.ucar.edu/wrf/TUTORIAL_DATA/matthew_1deg.tar.gz>`_, unpack the tar file and place all data in ``data/matthew/bg`` (``bg`` means background).

Prepare config file
*******************

The config file is a TOML file which contains configurations for ``wrfrun``, plus some basic settings for WRF. For more information about the config file, please see :doc:`../documentation/config_file`.

By specifying a non-existent file path and just entering ``WRFRun`` context without doing anything, ``wrfrun`` will copy the template config file to the corresponding path.

.. code-block:: Python
    :caption: main.py

    from wrfrun import WRFRun

    with WRFRun("config.toml") as server:
        pass

.. code-block::

    ERROR    wrfrun :: Config file doesn't exist, copy template config to /home/syize/Documents/Python/WRF/wrfrun-test/config.toml
    ERROR    wrfrun :: Please modify it.

You need to change following settings:

* ``input_data_path``: Path of the directory in which places the data you just download, should be ``data/matthew/bg``.
* ``output_path``: Path of the directory in which stores all outputs from WRF model.
* ``core_num``: How many cores ``wrfrun`` will use to run WRF.
* ``wps_path``: Path of the top directory of your installed WPS (the directory contains ``configure`` and ``compile``).
* ``wrf_path``: Path of the top directory of your installed WRF (the directory contains ``configure`` and ``compile``).
* ``geog_data_path``: Path of the directory in which places the static geographic data.

We will change other settings later.

Preprocess of input data
************************

We already downloaded `Matthew case study data <https://www2.mmm.ucar.edu/wrf/TUTORIAL_DATA/matthew_1deg.tar.gz>`_, we will use WPS to process them and generate background data which can input to WRF directly.

We need to change the following settings to match with the input data and configure simulation domain:

.. code-block:: toml

    # Set the start date, end date
    start_date = 2016-10-06T00:00:00Z
    end_date = 2016-10-08T00:00:00Z
    # Set input data time interval. Unit: seconds
    input_data_interval = 21600
    # Set domain number.
    domain_num = 1

You can check full config here.

.. dropdown:: Click to show full config

    .. code-block:: toml
        :caption: config.toml

        # Config template of wrfrun.
        # Path of the directory which contains input data.
        input_data_path = "./data/matthew/bg"

        # Path of the directory to store all outputs.
        output_path = "./outputs/Hurricane-Matthew"
        log_path = "./logs"

        # wrfrun can launch a socket server during NWP execution to report simulation progress.
        # To enable the server, you need to configure the IP address and port on which it will listen to.
        server_host = "0.0.0.0"
        server_port = 54321

        # How many cores you will use.
        # Note that if you use a job scheduler (like PBS), this value means the number of cores each node you use.
        core_num = 16


        [job_scheduler]
        # Job scheduler settings.
        # How many nodes you will use.
        node_num = 1

        # Custom environment settings
        env_settings = {}

        # Path of the python interpreter that will be used to run wrfrun.
        # You can also give its name only.
        python_interpreter = "/usr/bin/python3" # or just "python3"


        [model]
        # Model debug level
        debug_level = 100

        # ################################################### Only settings above is necessary ###########################################


        # ####################################### You can give more settings about the NWP you will use ##################################

        [model.wrf]
        # Config for WRF
        # WRF model path
        wps_path = '/home/syize/Apps/WPS'
        wrf_path = '/home/syize/Apps/WRF'
        # WRFDA is optional.
        wrfda_path = ''

        # static geographic data path
        geog_data_path = '/home/syize/Apps/geog_data'

        # Your can give your custom namelist files here.
        # The value in it will overwrite the default value in the namelist template file.
        user_wps_namelist = ''
        user_real_namelist = ''
        user_wrf_namelist = ''
        user_wrfda_namelist = ''

        # If you make a restart run?
        restart_mode = false


        [model.wrf.time]
        # Advance time config for WRF
        # Set the start date, end date
        start_date = 2016-10-06T00:00:00Z
        end_date = 2016-10-08T00:00:00Z

        # Set input data time interval. Unit: seconds
        input_data_interval = 21600

        # Set output data time interval. Unit: minutes
        output_data_interval = 180

        # Note that there are various reasons which could crash wrf,
        # and in most cases you can deal with them by decrease time step.
        # Unit: seconds
        time_step = 120

        # Time ratio to the first domain for each domain
        parent_time_step_ratio = [1, 3, 4]

        # Time interval to write restart files.
        # This help you can restart WRF after it stops.
        # By default, it equals to output_data_interval. Unit: minutes.
        restart_interval = 1440


        [model.wrf.domain]
        # Advance domain config for WRF.
        # Set domain number.
        domain_num = 1

        # It's very hard to process wrf domain settings because it's related to various settings, so I keep it.
        # The resolution ratio to the first domain.
        parent_grid_ratio = [1, 3, 9]

        # Index of the start point.
        i_parent_start = [1, 17, 72]
        j_parent_start = [1, 17, 36]

        # Number of points.
        e_we = [91, 250, 1198]
        e_sn = [100, 220, 1297]

        # Resolution of the first domain.
        dx = 27000
        dy = 27000

        # Projection.
        map_proj = { name = 'mercator', truelat1 = 30.0, truelat2 = 60.0 }

        # Central point of the first area.
        ref_lat = 28.0
        ref_lon = -75.0
        stand_lon = -75.0


        [model.wrf.scheme]
        # Advance physics scheme config for WRF.
        # To loop up the nickname for all physics schemes, please see: https://wrfrun.syize.cn.
        # Option contains many other settings related to the scheme.
        # Sometimes some option can only be used for a specific scheme.
        # You can check it in online namelist variables: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/namelist_variables.html
        # You can set option with its `wrf name` and its `wrf value`.
        # For example, `ghg_input=1` works with rrtm scheme. If you want to set `ghg_input=1` when using rrtm, set option: {"ghg_input": 1}
        # However, sometimes some options work with various schemes, and some options themselves are schem.
        # Use this carefully.
        # You can set multiple keys in option.
        long_wave_scheme = { name = "rrtm", option = {} }
        short_wave_scheme = { name = "rrtmg", option = {} }
        cumulus_scheme = { name = "kf", option = {} }
        pbl_scheme = { name = "ysu", option = { ysu_topdown_pblmix = 1 } }
        land_surface_scheme = { name = "noah", option = {} }
        surface_layer_scheme = { name = "mm5", option = {} }

Then call ``ungrib`` under the ``WRFRun``. We can tell ``ungrib`` to use GFS Vtable file by passing ``VtableFiles.GFS`` to it.

.. code-block:: Python
    :caption: main.py

    from wrfrun import WRFRun
    from wrfrun.model.wrf import ungrib, VtableFiles

    with WRFRun("config.toml") as server:
        ungrib(vtable_file=VtableFiles.GFS)

Execute ``main.py``, ``wrfrun`` will ask you if the domain is right, you can ignore it and just type ``y`` because we will set domain area later. You can find the outputs start with ``FILE`` in output directory after the execution finishes, and ``wrfrun`` command line output like:

.. code-block::

    INFO     wrfrun :: Enter wrfrun context
    INFO     wrfrun :: Running `./link_grib.csh ./input_grib_data_dir/* .` ...
    INFO     wrfrun :: Running `./ungrib.exe` ...
    INFO     wrfrun :: All ungrib output files have been copied to /home/syize/Documents/Python/WRF/wrfrun-test/outputs/ungrib
    INFO     wrfrun :: Exit wrfrun context

If you don't know whether the domain setting is set properly, just run the script again and ``wrfrun`` will draw the simulation domain using the built-in NCL script.

.. code-block::

    INFO     wrfrun :: The image of domain area has been saved to /home/liurw/Documents/WRF/2021-03-25/outputs/wps_show_dom.png
    WARNING  wrfrun :: Check the domain image, is it right?
    Is it right? [y/N]:

.. image:: quick_start/wps_show_dom.png

If the simulation domain is incorrect, just press the ``Enter`` button, ``wrfrun`` will exit to let you change the domain setting.

.. code-block::

    ERROR    wrfrun :: Change your domain setting and run again

If the region is set correctly, you can type ``y`` to continue.

Download input data
*******************

``wrfrun`` only supports using ``cdsapi`` to download the ERA5 data from `Climate Data Store <https://cds.climate.copernicus.eu/datasets>`_. If you want to use data from other sources, you will need to download it manually and put it in the corresponding directory.

If you want to use wrfrun to download data, you need to configure the `cdsapi token <https://cds.climate.copernicus.eu/how-to-api>`_ settings in advance. By setting the ``prepare_wps_data`` and ``wps_data_area`` parameters in ``WRFRun``, you can make wrfrun automatically download the required data.

.. code-block:: Python
    :caption: main.py

    from wrfrun import WRFRun

    # data area: 90°E - 180°E, 10°N - 70°N
    with WRFRun("./config.yaml", init_workspace=False, start_server=False,
                pbs_mode=False, prepare_wps_data=True, wps_data_area=(90, 180, 10, 70)) as server:
        pass

Running WPS
***********

Running WPS can be accomplished by calling the ``geogrid``, ``ungrib`` and ``metgrid`` function.

.. code-block:: Python
    :caption: main.py

    from wrfrun import WRFRun
    from wrfrun.model import geogrid, ungrib, metgrid

    with WRFRun("./config.yaml", init_workspace=False, start_server=False, pbs_mode=False) as server:
        geogrid()
        ungrib()
        metgrid()

After that, you can find all the logs and outputs of WPS in the directory ``outputs``, in which they are stored in separate subdirectories.

Running WRF
***********

Running WRF can be accomplished by calling the ``real`` and ``wrf`` function.

.. code-block:: Python
    :caption: main.py

    from wrfrun import WRFRun
    from wrfrun.model import real, wrf

    with WRFRun("./config.yaml", init_workspace=False, start_server=False, pbs_mode=False) as server:
        real()
        wrf()

After that, you can also find all the logs and outputs of WRF in the directory ``outputs``, in which they are stored in separate subdirectories.
