# wrfrun: A toolkit to control WRF

##  What is wrfrun？

Using and managing WRF can be a tedious task. WRF's configuration file contains a large number of settings, which generally need to be configured separately for each simulation case, and the user usually needs to rely on other tools or scripts to manage the simulation of different cases, which causes a lot of inconvenience. In addition, the whole process of running the WRF model involves running many programs, which is very time-consuming to run manually and requires the use of scripts to automate certain processes.

`wrfrun` is a comprehensive toolkit for managing and using WRF. `wrfrun` wraps the WRF model so that the user only needs to call the corresponding Python function to run the corresponding part of the model. `wrfrun` avoids cluttering up the user's working directory with a lot of useless files by creating a temporary directory in which the WRF model would be run. `wrfrun` automatically saves mode configurations and wrfrun configurations, which makes it easier to manage the simulation and reproduction of different cases. `wrfrun` also provides more features through extensions, which help users to do related research better.

## Main Features

The following are the main features that wrfrun wants to achieve. These features have been basically realized, and are still under continuous improvement.

- Isolate the WRF runtime directory in a separate temporary directory.
- Automatic saving of mode output, logs and configurations.
- Provide an interface to run any part of the WRF model.
- Real-time parsing of WRF logs, feedback on simulation progress.
- Support for adding more functionality through extensions.

## Installation

Install using pip:

```bash
pip install wrfrun
```

## Documentation

Please check [Wiki](https://github.com/Syize/wrfrun/wiki).