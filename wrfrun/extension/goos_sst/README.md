# GOOS SST extension

This extension can replace SKT (SKin Temperature) values in ERA5 reanalysis data with the SST (Sea Surface Temperature) from GOOS (Global Ocean Observing System). A new GRIB file will be generated so you can input it to WRF through `ungrib.exe` and `metgrid.exe`.

A [Vtable file](res/Vtable.ERA_GOOS_SST) is also provided for `ungrib.exe`.

## Features

- Replace SKT in ERA5 data with GOOS SST and write new data to a GRIB file.
- While only ERA5 data is tested, data from other sources is supported theoretically.