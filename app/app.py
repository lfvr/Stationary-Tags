import logging
from datetime import timedelta

import geopandas as gpd
import hvplot
import hvplot.pandas  # noqa
import movingpandas as mpd
from sdk.moveapps_spec import hook_impl


class App(object):

    def __init__(self, moveapps_io):
        self.moveapps_io = moveapps_io
        self.id_column = 'trackId'

    @hook_impl
    def execute(self, data: mpd.TrajectoryCollection, config: dict) -> mpd.TrajectoryCollection:
        logging.info('Starting stationarity detection')
        stops = self.stops_gdf(data, config)
        if stops.empty:
            logging.info('No stationary tags found')
            return data
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
            # Temporary while crs is set incorrectly in import. Update to commented out code once fixed.
            # stops.set_crs(data.to_traj_gdf().crs, inplace=True)
            stops.set_crs("epsg:4326", inplace=True)
        logging.info('Created csv file for stationary tags')
        stops.to_csv(self.moveapps_io.create_artifacts_file('stationary.csv'))
        return stops

    def plot_map(self, points: gpd.GeoDataFrame) -> None:
        map = points.hvplot(
            title='Stationary Tags',
            xlabel='Longitude', ylabel='Latitude',
            hover_cols=['Longitude', 'Latitude', 'timestamps', 'trackId'],
            width=1280, height=600,
            geo=True, tiles='OSM',
            color='red'
        )
        if len(points) == 1:
            # holoviz can't automatically calculate smart limits when there is only one point to plot - add them manually
            bounds = points.total_bounds
            map = points.hvplot(
                title='Stationary Tags',
                xlim=(bounds[0] - 1, bounds[2] + 1),
                ylim=(bounds[1] - 1, bounds[3] + 1),
                xlabel='Longitude', ylabel='Latitude',
                hover_cols=['Longitude', 'Latitude', 'timestamps', 'trackId'],
                geo=True, tiles='OSM',
                color='red'
            )
        render = map
        hvplot.save(render, self.moveapps_io.create_artifacts_file('stationary.html'))
        logging.info('Created html map for stationary tags')
        return