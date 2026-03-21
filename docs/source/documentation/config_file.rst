Configuration File
##################

``wrfrun`` uses TOML format for configuration files, which contains runtime settings and model-specific configurations. wrfrun adopts a layered configuration design: the main configuration file defines global settings, while specific configurations for each model are placed in separate files and imported via the ``include`` field.

Configuration file templates are located in the ``wrfrun/res/config/`` directory of the project source code, including the main configuration template, and various model configuration templates.

.. dropdown:: Click to view full main configuration file template
    :icon: file-code

    .. code-block:: toml
        :caption: config.toml

        # Config template of wrfrun.

        # Work directory.
        # By setting work directory, you can let wrfrun work and save runtime files in a single directory.
        # You can also set work_dir="" to let wrfrun work in the standard path.
        work_dir = "./.wrfrun"


        # Path of the directory which contains input data.
        input_data_path = ""

        # Path of the directory to store all outputs.
        output_path = "./outputs"
        log_path = "./logs"

        # wrfrun can launch a socket server during NWP execution to report simulation progress.
        # To enable the server, you need to configure the IP address and port on which it will listen to.
        server_host = "localhost"
        server_port = 54321

        # How many cores you will use.
        # Note that if you use a job scheduler (like PBS), this value means the number of cores each node you use.
        core_num = 36


        [job_scheduler]
        # Job scheduler settings.
        # Which job scheduler you want to use
        # wrfrun supports following job schedulers:
        # 1. PBS: "pbs"
        # 2. LSF: "lsf"
        # 3. Slurm: "slurm"
        job_scheduler = "pbs"

        # Which queue should the task be submited to
        queue_name = ""

        # How many nodes you will use.
        node_num = 1

        # Custom environment settings
        env_settings = {}

        # Path of the python interpreter that will be used to run wrfrun.
        # You can also give its name only.
        python_interpreter = "/usr/bin/python3"     # or just "python3"


        [model]

        [model.wrf]
        # If you want to use WRF model, set use to true.
        use = false
        # Import configurations from another toml file.
        # You can give both absolute and relative path.
        # The relative path is resolved based on this configuration file.
        include = "./configs/wrf.toml"

        [model.palm]
        # If you want to use PALM model, set use to true.
        use = false
        # Import configurations from another toml file.
        # You can give both absolute and relative path.
        # The relative path is resolved based on this configuration file.
        include = "./configs/palm.toml"

.. dropdown:: Click to view full WRF model configuration template
    :icon: file-code

    .. code-block:: toml
        :caption: wrf.toml

        # Config for WRF model.
        # WRF model path.
        wps_path = '/path/to/your/WPS/folder'
        wrf_path = '/path/to/your/WRF/folder'
        # WRFDA is optional.
        wrfda_path = ''

        # static geographic data path
        geog_data_path = '/path/to/your/geog/data'

        # Namelist template.
        # If None, will use built-in namelist template.
        wps_namelist_template = ''
        wrf_namelist_template = ''
        wrfda_namelist_template = ''

        # Your can give your custom namelist files here.
        # The value in it will overwrite the default value in the namelist template file.
        user_wps_namelist = ''
        user_real_namelist = ''
        user_wrf_namelist = ''
        user_wrfda_namelist = ''

        # If you make a restart run?
        restart_mode = false

        # debug level for WRF model
        debug_level = 100

        [time]
        # Advance time config for WRF
        # Set the start and end date. It will be used for all domains.
        # You can also provide all the dates as a list, with each date for the corresponding domain.
        start_date = 2021-03-24T12:00:00Z   # or [2021-03-24T12:00:00Z, 2021-03-24T12:00:00Z]
        end_date = 2021-03-26T00:00:00Z     # or [2021-03-26T00:00:00Z, 2021-03-24T12:00:00Z]

        # Set input data time interval. Unit: seconds
        input_data_interval = 10800

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
        restart_interval = -1


        [domain]
        # Advance domain config for WRF.
        # Set domain number.
        domain_num = 3

        # It's very hard to process wrf domain settings because it's related to various settings, so I keep it.
        # The resolution ratio to the first domain.
        parent_grid_ratio = [1, 3, 9]

        # Index of the start point.
        i_parent_start = [1, 17, 72]
        j_parent_start = [1, 17, 36]

        # Number of points.
        e_we = [120, 250, 1198]
        e_sn = [120, 220, 1297]

        # Resolution of the first domain.
        dx = 9000
        dy = 9000

        # Projection.
        map_proj = 'lambert'
        truelat1 = 34.0
        truelat2 = 40.0

        # Central point of the first area.
        ref_lat = 37.0
        ref_lon = 120.5
        stand_lon = 120.5


        [scheme]
        # Advance physics scheme config for WRF.
        # To look up the nickname for all physics schemes, please see: https://wrfrun.syize.cn.
        # Option contains many other settings related to the scheme.
        # Sometimes some option can only be used for a specific scheme.
        # You can check it in online namelist variables: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/namelist_variables.html
        # You can set option with its `wrf name` and its `wrf value`.
        # For example, `ghg_input=1` works with rrtm scheme. If you want to set `ghg_input=1` when using rrtm, set option: {"ghg_input": 1}
        # However, sometimes some options work with various schemes, and some options themselves are scheme.
        # Use this carefully.
        # You can set multiple keys in option.
        long_wave_scheme = { name = "rrtm", option = {} }
        short_wave_scheme = { name = "rrtmg", option = {} }
        cumulus_scheme = { name = "kf", option = {} }
        pbl_scheme = { name = "ysu", option = { ysu_topdown_pblmix = 1} }
        land_surface_scheme = { name = "noah", option = {} }
        surface_layer_scheme = { name = "mm5", option = {} }

.. dropdown:: Click to view full PALM model configuration template
    :icon: file-code

    .. code-block:: toml
        :caption: palm.toml

        # Config for PALM model.
        # PALM model path.
        palm_path = "/path/to/your/PALM/folder"

        # Place data here.
        data_dir_path = "/path/to/your/data/folder"

        # Set PALM config identifier here.
        # If you want to use a config identifier you never used before,
        # make sure palm can build successfully.
        config_identifier = "default"

        # Set job name (aka run identifier in PALM) here.
        job_name = "wrfrun"

        # Set simulation type here (the value passed to "-a" of palmrun)
        # Available values:
        #   - "d3#"
        #   - "d3r"
        #   - "pcr"
        simulation_type = "d3#"

        # PALM config file.
        # If empty, use the default config from PALM.
        # You can get a file from PALM_INSTALL_DIR/.palm.config.default
        config_file_path = ""

        # You can provide topography file here.
        topography_file = '/path/to/your/topography/file'

        # You need to give your namelist file,
        # cause wrfrun hasn't supported more options in toml config file yet.
        user_namelist = '/path/to/your/namelist/file'

Configuration Structure
***********************

The configuration file is divided into three main sections: global configuration, job scheduler configuration, and model configuration.

Global Configuration
====================

The global configuration defines the basic operating parameters of wrfrun:

.. code-block:: toml

    # Working directory where wrfrun saves all runtime files
    work_dir = "./.wrfrun"

    # Path to directory containing input data
    input_data_path = ""

    # Paths for output files and log files
    output_path = "./outputs"
    log_path = "./logs"

    # Progress report server configuration
    server_host = "localhost"
    server_port = 54321

    # Number of CPU cores to use
    # When using a job scheduler, this value represents the number of cores per node
    core_num = 36

Job Scheduler Configuration
===========================

The ``[job_scheduler]`` section defines job submission related configurations:

.. code-block:: toml

    [job_scheduler]
    # Job scheduler type, supports "pbs", "lsf", "slurm"
    job_scheduler = "pbs"

    # Job queue name
    queue_name = ""

    # Number of nodes to use
    node_num = 1

    # Custom environment variable settings
    env_settings = {}

    # Python interpreter path
    python_interpreter = "/usr/bin/python3"

Model Configuration
===================

The ``[model]`` section defines the numerical models to use and their configurations:

.. code-block:: toml

    [model]

    [model.wrf]
    # Whether to enable WRF model
    use = false
    # Path to WRF model configuration file, can be absolute or relative
    include = "./configs/wrf.toml"

    [model.palm]
    # Whether to enable PALM model
    use = false
    # Path to PALM model configuration file
    include = "./configs/palm.toml"

wrfrun supports configuring multiple models simultaneously.

WRF Model Configuration Details
*******************************

The WRF model configuration file contains all parameters required for WRF runs, divided into the following sections:

Basic Configuration
===================

.. code-block:: toml

    # Installation paths for WPS, WRF and WRFDA
    wps_path = '/path/to/your/WPS/folder'
    wrf_path = '/path/to/your/WRF/folder'
    wrfda_path = ''  # Optional

    # Geographic data path
    geog_data_path = '/path/to/your/geog/data'

    # Custom namelist template paths
    wps_namelist_template = ''
    wrf_namelist_template = ''
    wrfda_namelist_template = ''

    # User custom namelist files, will override default values in templates
    user_wps_namelist = ''
    user_real_namelist = ''
    user_wrf_namelist = ''
    user_wrfda_namelist = ''

    # Whether this is a restart run
    restart_mode = false

    # WRF debug level
    debug_level = 100

Time Configuration
==================

The ``[time]`` section defines simulation time related parameters:

.. code-block:: toml

    [time]
    # Simulation start and end times, supports ISO 8601 format
    # You can also specify different times for each domain, e.g. [2021-03-24T12:00:00Z, 2021-03-24T12:00:00Z]
    start_date = 2021-03-24T12:00:00Z
    end_date = 2021-03-26T00:00:00Z

    # Input data time interval in seconds
    input_data_interval = 10800

    # Output data time interval in minutes
    output_data_interval = 180

    # Integration time step in seconds
    time_step = 120

    # Time step ratio for each nested domain relative to the outermost domain
    parent_time_step_ratio = [1, 3, 4]

    # Restart file writing interval in minutes
    # -1 means same as output interval
    restart_interval = -1

Domain Configuration
====================

The ``[domain]`` section defines simulation domain related parameters:

.. code-block:: toml

    [domain]
    # Total number of nested domains
    domain_num = 3

    # Resolution ratio for each nested domain relative to the outermost domain
    parent_grid_ratio = [1, 3, 9]

    # Starting point indices for each nested domain
    i_parent_start = [1, 17, 72]
    j_parent_start = [1, 17, 36]

    # Number of grid points for each nested domain
    e_we = [120, 250, 1198]
    e_sn = [120, 220, 1297]

    # Resolution of the outermost domain in meters
    dx = 9000
    dy = 9000

    # Projection method and parameters
    map_proj = 'lambert'
    truelat1 = 34.0
    truelat2 = 40.0

    # Center point coordinates of the domain
    ref_lat = 37.0
    ref_lon = 120.5
    stand_lon = 120.5

Physics Scheme Configuration
============================

The ``[scheme]`` section defines the physical parameterization schemes used by WRF:

.. code-block:: toml

    [scheme]
    # Longwave radiation scheme
    long_wave_scheme = { name = "rrtm", option = {} }
    # Shortwave radiation scheme
    short_wave_scheme = { name = "rrtmg", option = {} }
    # Cumulus convection scheme
    cumulus_scheme = { name = "kf", option = {} }
    # Planetary boundary layer scheme
    pbl_scheme = { name = "ysu", option = { ysu_topdown_pblmix = 1} }
    # Land surface model scheme
    land_surface_scheme = { name = "noah", option = {} }
    # Surface layer scheme
    surface_layer_scheme = { name = "mm5", option = {} }

Each physics scheme contains two fields: ``name`` and ``option``:

- ``name``: The name of the scheme, wrfrun has built-in aliases for all commonly used schemes, see :doc:`/api/model.wrf.scheme` for the complete list of available schemes.
- ``option``: Additional configuration options for this scheme, which will be written directly to the namelist

You can view all available physics schemes and parameters in the `official WRF documentation <https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/namelist_variables.html>`_.

PALM Model Configuration Details
********************************

The PALM model configuration file contains parameters required for PALM runs:

.. code-block:: toml

    # PALM model installation path
    palm_path = "/path/to/your/PALM/folder"

    # Data directory path
    data_dir_path = "/path/to/your/data/folder"

    # PALM configuration identifier
    config_identifier = "default"

    # Job name (run identifier in PALM)
    job_name = "wrfrun"
