from datetime import timedelta
import geopandas as gpd
import logging
import matplotlib.pyplot as plt
import movingpandas as mpd
from shapely.geometry import Point
from sdk.moveapps_spec import hook_impl

class App(object):

    def __init__(self, moveapps_io):
        self.moveapps_io = moveapps_io
        self.id_column = 'trackId'

    @hook_impl
    def execute(self, data: mpd.TrajectoryCollection, config: dict) -> mpd.TrajectoryCollection:
        logging.info(f'Starting stationarity detection')
        stops = self.stops_gdf(data, config)
        if not stops.empty:
            self.plot_map(stops)
        return data
    
    def stopped(self, data: mpd.Trajectory, config: dict) -> bool:
        earliest_time = data.get_end_time() - timedelta(hours=config["stop_duration"])
        try:
            segment = data.get_segment_between(earliest_time, data.get_end_time())
        except ValueError:
            logging.error(f'Fewer than 2 entries for {data.id}, unable to make stationarity determination')
            return False
            
        if segment.get_length() <= config["distance_tolerance"]:
            return True

        return False

    def stops_gdf(self, data: mpd.TrajectoryCollection, config: dict) -> gpd.GeoDataFrame:
        ids: list[str] = []
        for traj in data:
            if self.stopped(traj, config):
                ids.append(traj.id)
        stops = data.filter(self.id_column, ids).get_end_locations()
        if not stops.empty:
            stops.set_crs(data.to_traj_gdf().crs, inplace=True)
        return stops

    def plot_map(self, points: gpd.GeoDataFrame) -> None:
        # the percentage distance betweeen the axis boundary and the outermost point   
        margin = 0.05
        # TODO: this dataset is deprecated and will be removed from GeoPandas v1.0 - find alternative
        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        _, gax = plt.subplots(figsize=(10,10))
        world.plot(ax=gax, edgecolor='blue',color='white')
        gax.set_xlabel('longitude')
        gax.set_ylabel('latitude')

        # get the bounds of the data to limit the map size
        bounds = points.total_bounds
        x_margin = (bounds[2] - bounds[0]) * margin
        y_margin = (bounds[3] - bounds[1]) * margin
        plt.xlim(bounds[0] - x_margin, bounds[2] + x_margin)
        plt.ylim(bounds[1] - y_margin, bounds[3] + y_margin)

        # ensure map outlines go up to the axis boundaries
        gax.spines['top'].set_visible(False)
        gax.spines['right'].set_visible(False)

        # plot the points
        points.plot(ax=gax, color='red', alpha = 0.5)
        for x, y, label in zip(points['geometry'].x, points['geometry'].y, points[self.id_column]):
            gax.annotate(f'{label}: {x,y}', xy=(x,y), xytext=(4,4), textcoords='offset points')
        path = self.moveapps_io.create_artifacts_file('stationarity.png')
        plt.savefig(path)
        plt.close()