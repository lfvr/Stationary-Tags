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
        return stops

    def plot_map(self, points: gpd.GeoDataFrame) -> None:
        map = points.hvplot(
            title='Stationary Tags', 
            x='Longitude', y='Latitude',
            geo=True, tiles='OSM',
            color='red'
        )
        # workaround of issue https://github.com/holoviz/hvplot/issues/596
        # kudos: https://stackoverflow.com/questions/67005004/how-can-i-overlay-text-labels-on-a-geographic-hvplot-points-plot
        new_crs = points.to_crs('EPSG:3857').assign(x=lambda points: points.geometry.x, y=lambda points: points.geometry.y)
        id_labels = new_crs.hvplot.labels(text='trackId', x="x", y="y")

        render = map * id_labels.opts(text_baseline='bottom')
        hvplot.save(render, self.moveapps_io.create_artifacts_file('stationary.html'))
        logging.info('Created html map for stationary tags')
        return