# 🌀 wrfrun

> A modern, unified framework for running and managing numerical models.
>
> Designed for researchers who want to focus on science — not on the details of model execution.

## 📖 Introduction

`wrfrun` is a Python package that provides a general-purpose, reproducible, and extensible framework for running numerical models.

It automates the tedious parts of model execution — preparing input data, handling `namelist` configurations, organizing logs, and submitting jobs — so that you can spend your time on research, not on managing model runs.

## ⚡ Quick Installation

```bash
pip install wrfrun
```

## 📖 Documentation

Check [https://wrfrun.syize.cn](https://wrfrun.syize.cn/).

## 🌟 Core Features

### 🧩 Unified Interface Architecture

`wrfrun` enforces a unified interface specification for all numerical models. Specifically, each model interface must inherit from a provided base class, ensuring a consistent structure and behavior across different models.

This design makes model execution intuitive — any supported model can be launched simply by calling a Python function or class method, while `wrfrun` automatically handles all background tasks such as data preparation and configuration file management.

```python
from wrfrun import WRFRun
from wrfrun.model.wrf import geogrid, metgrid, real, ungrib, wrf

# wrfrun will prepare input data, generate namelist file, 
# save outputs and logs automatically.
with WRFRun("./config.toml", init_workspace=True) as wrf_run:
    geogrid()
    ungrib()
    metgrid()
    real()
    wrf()
```

### 🪶 Record & Replay

Every simulation can be fully recorded and later reproduced from a single `.replay` file — ensuring total reproducibility.

```python
from wrfrun import WRFRun
from wrfrun.model.wrf import geogrid, ungrib, metgrid, real, wrf


# 1. Record simulation with method `record_simulation`.
with WRFRun("./config.toml", init_workspace=True) as wrf_run:
    wrf_run.record_simulation(output_path="./outputs/example.replay")

    geogrid()
    ungrib()
    metgrid()
    real()
    wrf()

# 2. Replay the simulation in a different directory or on a different machine.
with WRFRun("./config.toml", init_workspace=True) as wrf_run:
    wrf_run.replay_simulation("./example.replay")
```

### ⚙️ Simplified Configuration

Manage all simulation settings in TOML files: A main config file, and model config files.

For more information about the configuration file, check [config](wrfrun/res/config).

```toml
# main config file: config.toml
work_dir = "./.wrfrun"

input_data_path = ""
output_path = "./outputs"
log_path = "./logs"

server_host = "localhost"
server_port = 54321

core_num = 36

[job_scheduler]
job_scheduler = "pbs"

queue_name = ""
node_num = 1
env_settings = {}
python_interpreter = "/usr/bin/python3"     # or just "python3"

[model]
[model.wrf]
use = false
include = "./configs/wrf.toml"
```

`wrfrun` remains compatible with original `namelist` inputs, just set namelist file path in the model config.

```toml
# WRF model config file: wrf.toml
wps_path = '/path/to/your/WPS/folder'
wrf_path = '/path/to/your/WRF/folder'
wrfda_path = ''		# WRFDA is optional.
geog_data_path = '/path/to/your/geog/data'
user_wps_namelist = ''		# set your own namelist file here
user_real_namelist = ''		# set your own namelist file here
user_wrf_namelist = ''		# set your own namelist file here
user_wrfda_namelist = ''	# set your own namelist file here
restart_mode = false
debug_level = 100

[time]
start_date = 2021-03-24T12:00:00Z   # or [2021-03-24T12:00:00Z, 2021-03-24T12:00:00Z]
end_date = 2021-03-26T00:00:00Z     # or [2021-03-26T00:00:00Z, 2021-03-24T12:00:00Z]
input_data_interval = 10800
output_data_interval = 180
time_step = 120
parent_time_step_ratio = [1, 3, 4]
restart_interval = -1


[domain]
domain_num = 3
parent_grid_ratio = [1, 3, 9]
i_parent_start = [1, 17, 72]
j_parent_start = [1, 17, 36]
e_we = [120, 250, 1198]
e_sn = [120, 220, 1297]
dx = 9000
dy = 9000
map_proj = 'lambert'
truelat1 = 34.0
truelat2 = 40.0
ref_lat = 37.0
ref_lon = 120.5
stand_lon = 120.5


[scheme]
long_wave_scheme = { name = "rrtm", option = {} }
short_wave_scheme = { name = "rrtmg", option = {} }
cumulus_scheme = { name = "kf", option = {} }
pbl_scheme = { name = "ysu", option = { ysu_topdown_pblmix = 1} }
land_surface_scheme = { name = "noah", option = {} }
surface_layer_scheme = { name = "mm5", option = {} }
```

### 💻 Job Scheduling Integration

Automatically submit jobs to supported schedulers:

- PBS
- Slurm
- LSF

`wrfrun` takes care of resource requests and queue management automatically.

```python
from wrfrun import WRFRun
from wrfrun.model.wrf import geogrid, metgrid, real, ungrib, wrf

# just set submit_job=True
with WRFRun("./config.toml", init_workspace=True, submit_job=True) as wrf_run:
    geogrid()
    ungrib()
    metgrid()
    real()
    wrf()
```

### 📡 Real-time Monitoring

`wrfrun` can parse model log files and start a lightweight socket server to report simulation progress.

```python
from wrfrun import WRFRun
from wrfrun.model.wrf import geogrid, metgrid, real, ungrib, wrf

# just set start_server=True
with WRFRun("./config.toml", init_workspace=True, start_server=True) as wrf_run:
    geogrid()
    ungrib()
    metgrid()
    real()
    wrf()
```

## 🌍 Current Capabilities

- Automated ERA5 data download (requires `cdsapi` authentication)
- Real-time progress reporting via socket interface
- Partial WRF support:
  - Full support for WPS
  - Wrapped execution for `real` and `wrf`
- Job submission on PBS, Slurm, and LSF
- `record` / `replay` reproducibility for all compliant interfaces

## 🧭 TODO

- [ ] Full WRF model integration.
- [ ] Broaden model support.
- [ ] Enhanced progress visualization dashboard.

## 🤝 Contributing

This project is currently for personal and research use. If you have ideas or feature requests, feel free to open an issue.