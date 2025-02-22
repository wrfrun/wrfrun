Config
######

``wrfrun``'s config file is a YAML file which contains ``wrfrun``'s runtime settings and some WRF basic settings. Here is a config file template, which comes from `wrfrun/res/config.yaml.template <https://github.com/Syize/wrfrun/blob/master/wrfrun/res/config.yaml.template>`_.

.. dropdown:: Click to show full config content

    .. code-block:: yaml

        # The following settings will be used to run WPS and WRF
        wrf:

          # Set your WPS, WRF and WRFDA path here.
          wps_path: '/path/to/your/WPS/folder'
          wrf_path: '/path/to/your/WRF/folder'
          wrfda_path: '/path/to/your/WRFDA/folder'

          # Set your geographical data path here
          # It will be used as "geog_data_path" in namelist.wps
          geog_data_path: '/path/to/your/geog/data'

          # Specify your WPS input data folder path here
          wps_input_data_folder: './data/bg'

          # Specify your Near GOOS data folder path here
          near_goos_data_folder: './data/sst'

          # Your can give your custom namelist files here
          # The value in it will overwrite the default value in wrfrun's namelist template file
          user_wps_namelist: ''
          user_real_namelist: ''
          user_wrf_namelist: ''
          user_wrfda_namelist: ''

          # It is OK to set debug_level larger than 100. You will need to check details is WRF crash.
          # And of course, who cares logs if WRF finished successfully?
          debug_level: 100

          time:
            # Set the start date, end date
            start_date: '2021-03-24 12:00:00'
            end_date: '2021-03-26 00:00:00'
            # Set input data time interval. Unit: seconds
            input_data_interval: 10800
            # Set output data time interval. Unit: minutes
            output_data_interval: 180
            # Note that there are various reasons which could crash wrf,
            # and in most cases you can deal with them by decrease time step.
            # Unit: seconds
            time_step: 120
            # Time ratio to the first domain for each domain
            parent_time_step_ratio: [1, 3, 4]
            # Time interval to write restart file. This help you can restart WRF after it stop.
            # By default it equals to output_data_interval. Unit: minutes.
            restart_interval: -1

          domain:
            # Set domain number
            domain_num: 3
            # It's very hard to process wrf domain settings because it's related to various settings, so I keep it
            # Remember to check area settings with wrfrun function `plot_domain_area` before submit to PBS (May not be completed now)
            # Resolution ratio to the first domain
            parent_grid_ratio : [1, 3, 9]
            # Index of the start point
            i_parent_start : [1, 17, 72]
            j_parent_start : [1, 17, 36]
            # Number of point
            e_we : [120, 250, 1198]
            e_sn : [120, 220, 1297]
            # Resolution of the first domain
            dx : 9000
            dy : 9000
            # Projection
            map_proj :
              name: 'lambert'
              # For lambert projection
              truelat1 : 34.0
              truelat2 : 40.0
            # Central point of the first area
            ref_lat : 37.0
            ref_lon : 120.5
            stand_lon : 120.5

          # This section is used to specify various physics scheme for wrf
          scheme:

            # Here's the option of long wave scheme
            # "off": off,
            # "rrtm": RRTM,
            # "cam": CAM,
            # "rrtmg": RRTMG,
            # "new-goddard": New Goddard,
            # "flg": FLG,
            # "rrtmg-k": RRTMG-K,
            # "held-suarez": Held-Suarez,
            # "gfdl": GFDL
            long_wave_scheme:
              name: 'rrtm'
              # Option contains many other settings related to the scheme.
              # Sometimes some option can only be used for specific scheme.
              # You can check it in online namelist variables: https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/build/html/namelist_variables.html
              # You can set option with its `wrf name` and its `wrf value`
              # For example, `ghg_input=1` works with rrtm scheme. If you want set `ghg_input=1` when using rrtm, set option: {"ghg_input": 1}
              # However, sometimes some options work with various scheme, and some options themselves are schem.
              # Use this carefully.
              # You can set multiple keys in option.
              option: {'icloud': 1}

            # Here's the option of short wave scheme
            # "off": off,
            # "dudhia": Dudhia,
            # "goddard": Goddard,
            # "cam": CAM,
            # "rrtmg": RRTMG,
            # "new-goddard": New Goddard,
            # "flg": FLG,
            # "rrtmg-k": RRTMG-K,
            # "gfdl": GFDL
            short_wave_scheme:
              name: 'rrtmg'
              option: {}

            # Here's the option of cumulus scheme
            # "off": off,
            # "kf": Kain-Fritsch (KF),
            # "bmj": BMJ,
            # "gf": Grell-Freitas,
            # "old-sas": Old SAS,
            # "grell-3": Grell-3,
            # "tiedtke": Tiedtke,
            # "zmf": Zhang-McFarlane,
            # "kf-cup": KF-CuP,
            # "mkf": Multi-scale KF,
            # "kiaps-sas": KIAPS SAS,
            # "nt": New Tiedtke,
            # "gd": Grell-Devenyi,
            # "nsas": NSAS,
            # "old-kf": Old KF
            cumulus_scheme:
              name: 'kf'
              option: {}

            # Here's the option of PBL scheme
            # "off": off,
            # "ysu": YSU,
            # "myj": MYJ,
            # "qe": QNSE-EDMF,
            # "mynn2": MYNN2,
            # "acm2": ACM2,
            # "boulac": BouLac,
            # "uw": UW,
            # "temf": TEMF,
            # "shin-hong": Shin-Hong,
            # "gbm": GBM,
            # "eeps": EEPS,
            # "keps": KEPS,
            # "mrf": MRF
            pbl_scheme:
              name: 'ysu'
              option: {'ysu_topdown_pblmix': 1}

            # Here's the option of land surface model
            # "off": off,
            # "slab": 5-layer thermal diffusion (SLAB),
            # "noah": Noah,
            # "ruc": RUC,
            # "noah-mp": Noah-MP,
            # "clm4": Community Land Model Version 4 (CLM4),
            # "px": Pleim-Xiu,
            # "ssib": Simplified Simple Biosphere (SSiB)
            land_surface_scheme:
              name: 'noah'
              option: {}

            # Here's the option of surface layer scheme
            # "off": off,
            # "mm5": revised MM5 Monin-Obukhov,
            # "mo": Monin-Obukhov (Janjic Eta Similarity),
            # "qnse": QNSE,
            # "mynn": MYNN,
            # "px": Pleim-Xiu; use with Pleim-Xiu surface and ACM2 PBL,
            # "temf": TEMF,
            # "old-mm5": old MM5
            surface_layer_scheme:
              name: 'mo'
              option: {}

        # The following settings are general settings.
        wrfrun:

          # Specify where to save py-wrfrun log file
          log_path: './logs'

          # Specify the socket ip and port to start socket server
          # You can send any message to this server to check if wrfrun is still running,
          # and how much time has been used, running progress of wrfrun.
          socket_host: "localhost"
          # Leave port to 0 to let system determine it.
          # You can get the port number in log file.
          socket_port: 54321

          # Settings for PBS
          PBS:

            # Specify how many nodes you will use
            node_num: 1

            # Specify how many cores each node you will use
            core_num: 36

            # Specify custom environment settings here
            env_settings: {}

            # Specify custom python interpreter here
            python_interpreter: 'python3'

          # Specify your data save path here, all the outputs from WPS, WRF and WRFDA will be copied and saved in it
          output_path: './outputs'

As you can see, the contents of the configuration file are divided into two main sections, ``wrf`` and ``wrfrun``. The ``wrf`` block contains the most commonly used configuration options for WRF, and the ``wrfrun`` block is used to set the save path of ``wrfrun``'s log and WRF output files, job scheduler settings and so on. They will be explained in detail in the following documentation.

wrf
***

The ``wrf`` block are divided into two main parts, too. Most of the first several options won't be passed to WRF actually. They are used to inform ``wrfrun`` essential information to run WRF. Here are options and their explanations.

.. code-block:: yaml

    # The absolute path to installation directories of WPS, WRF and WRFDA.
    # wps_path and wrf_path is mandatory, wrfda_path is optional.
    # If you don't use WRFDA, you can leave it empty.
    wps_path: '/path/to/your/WPS/folder'
    wrf_path: '/path/to/your/WRF/folder'
    wrfda_path: '/path/to/your/WRFDA/folder'

    # The absolute path to the directory contains geographical data.
    # It will be used as "geog_data_path" in namelist.wps
    geog_data_path: '/path/to/your/geog/data'

    # The absolute path to the directory contains WPS input data.
    wps_input_data_folder: './data/bg'

    # The absolute path to the directory contains NEAR-GOOS data.
    # If you don't use NEAR-GOOS SST data, leave it empty.
    near_goos_data_folder: './data/sst'

    # Your can give your custom namelist files here.
    # The value in it will overwrite the default value in wrfrun's namelist template file.
    user_wps_namelist: ''
    user_real_namelist: ''
    user_wrf_namelist: ''
    user_wrfda_namelist: ''

User custom namelist
====================

Although ``wrfrun`` attempts to simplify the process of configuring WRF, it is almost impossible to fully rewrite all namelist options into another more understandable format due to the large number of options in the WRF namelist, while researchers sometimes add their additional options. Therefore, ``wrfrun`` allows users to provide their custom namelist files, which can either include the complete WRF configurations or only the options that need to be changed. Before running WRF, ``wrfrun`` will read these files and update the corresponding options to apply the user's configurations.

For example, the default option of ``io_form_geogrid`` in ``wrfrun`` is ``2``, which means the output format of ``geogrid.exe`` is ``NetCDF``. If you want to change the value of it to ``3`` (because ``wrfrun`` doesn't provide any function to change ``io_form_geogrid``'s value), you can write a custom namelist like this

.. code-block::
    :caption: custom_wps_namelist

    &share
        io_form_geogrid = 3
    /

It looks like a simplified version of WRF namelist, but it still works for ``wrfrun``. Change ``user_wps_namelist``'s value to ``custom_wps_namelist``'s path, for example, ``./namelist/custom_wps_namelist``, ``wrfrun`` will read it and overwrite the default value with your configurations.

.. code-block:: yaml

    user_wps_namelist: './namelist/custom_wps_namelist'

You can use the function ``write_namelist`` to write namelist settings a to file to check it.

.. code-block:: python

    from wrfrun import WRFRun, write_namelist

    with WRFRun("./config.yaml", init_workspace=False, start_server=False, pbs_mode=False) as server:
        write_namelist("./test_namelist", "wps")

wrfrun
******
