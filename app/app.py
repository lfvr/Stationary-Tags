from datetime import timedelta
import logging
import movingpandas as mpd
from shapely.geometry import Point
from sdk.moveapps_spec import hook_impl

class App(object):

    def __init__(self, moveapps_io):
        self.moveapps_io = moveapps_io

    @hook_impl
    def execute(self, data: mpd.TrajectoryCollection, config: dict) -> mpd.TrajectoryCollection:
        logging.info(f'Starting stationarity detection')
        for traj in data:
            stopped, location = self.find_stops(traj, config)
            if stopped:
                logging.info(f'{traj.id} stopped at {location}')
                print(f'{traj.id} stopped at {location}')
        return data
    
    def find_stops(self, data: mpd.Trajectory, config: dict) -> tuple[bool, Point]:
        earliest_time = data.get_end_time() - timedelta(hours=config["stop_duration"])
        try:
            segment = data.get_segment_between(earliest_time, data.get_end_time())
        except ValueError:
            logging.error(f'Fewer than 2 entries for {data.id}, unable to make stationarity determination')
            return False, None
            
        if segment.get_length() <= config["stop_duration"]:
            return True, data.get_end_location()
        return False, None