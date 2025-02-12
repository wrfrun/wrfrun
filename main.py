from wrfrun.model.run import geogrid, ungrib, metgrid, real, wrf
from wrfrun.run import WRFRun

if __name__ == "__main__":
    # define config path here
    config_path = "./config.yaml"

    # enter WRFRun context
    with WRFRun(
        config_path, init_workspace=True, start_server=True, pbs_mode=True,
    ):
        # run geogrid
        geogrid()

        # run ungrib
        ungrib()

        # run metgrid
        metgrid()

        # run real
        real()

        # run wrf
        wrf()
