# from sdk.moveapps_spec import hook_impl
from pickle import load
from datetime import timedelta
import logging
# import geoviews
import movingpandas as mpd
# import pandas as pd
# from holoviews import opts


class App(object):

    def __init__(self, moveapps_io):
        self.moveapps_io = moveapps_io

    # @hook_impl
    def execute(self, data: mpd.TrajectoryCollection, config: dict) -> mpd.TrajectoryCollection:
        logging.info(f'Welcome to the {config}')

        detector = mpd.TrajectoryStopDetector(data)
        self.create_map(data)
        stop_points = detector.get_stop_points(min_duration=timedelta(hours=config["stop_duration"]), max_diameter=config["distance_tolerance"])
        print(stop_points)

        
        return data

    def create_map(self, data: mpd.TrajectoryCollection):
        plot = data.trajectories[0].plot(
            linewidth=5,
            capstyle='round',
        )
        print(plot)
        

if __name__ == '__main__':
    app = App(None)
    data: mpd.TrajectoryCollection
    with (open("/Users/lauren/Documents/CS/emac23/data/buffalo.pickle", "rb")) as openfile:
        try:
            data = load(openfile)
        except EOFError:
            exit()
    print(data)
    app.execute(data, {"stop_duration": 12, "distance_tolerance": 100})