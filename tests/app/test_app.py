from dataclasses import dataclass
from datetime import datetime
import os
import unittest
import geopandas as gpd
from geopandas.testing import assert_geodataframe_equal
from matplotlib.testing.compare import compare_images
import movingpandas as mpd
import pandas as pd
from shapely.geometry import Point
from tests.config.definitions import ROOT_DIR
from app.app import App
from sdk.moveapps_io import MoveAppsIo

class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        os.environ['APP_ARTIFACTS_DIR'] = os.path.join(ROOT_DIR, 'tests/resources/output')
        self.sut = App(moveapps_io=MoveAppsIo())

    def test_app_returns_input(self) -> None:
        # prepare
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        config: dict = {"stop_duration": 15, "distance_tolerance": 100}

        # execute
        actual = self.sut.execute(data=expected, config=config)

        # verify
        self.assertEqual(expected, actual)

    def test_full_app_flow(self) -> None:
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/rhino_edited.pickle'))
        config: dict = {"stop_duration": 10, "distance_tolerance": 100}
        actual = self.sut.execute(data=expected, config=config)
        self.assertEqual(expected, actual)

    def test_stopped(self) -> None:

        @dataclass
        class Testcase:
            def __init__(self, name: str, traj: mpd.Trajectory, config: dict, expect: bool):
                self.name = name
                self.traj = traj
                self.config = config
                self.expect = expect

        default_config = {
            "stop_duration": 2,
            "distance_tolerance": 100,
        }
        testcases = [
            Testcase(
                "stop_at_end_returns_True", 
                traj=mpd.Trajectory(gpd.GeoDataFrame(pd.DataFrame([
                {'id': 1, 'geometry': Point(0,0), 't': datetime(2023, 1, 1, 1, 0, 0)},
                {'id': 1, 'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 2, 0, 0)},
                {'id': 1, 'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 3, 0, 0)},
                {'id': 1, 'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 4, 0, 0)}
                ]).set_index('t'), crs=4326), 1),
                config=default_config, 
                expect=True
            ),
            Testcase(
                "no_stop_returns_False", 
                traj=mpd.Trajectory(gpd.GeoDataFrame(pd.DataFrame([
                {'geometry': Point(0,0), 't': datetime(2023, 1, 1, 1, 0, 0)},
                {'geometry': Point(1, 1), 't': datetime(2023, 1, 1, 3, 0, 0)},
                {'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 5, 0, 0)},
                {'geometry': Point(3, 3), 't': datetime(2023, 1, 1, 7, 0, 0)}
                ]).set_index('t'), crs=4326), 1),
                config=default_config, 
                expect=False,
            ),
            Testcase(
                "stop_in_middle_returns_False", 
                traj=mpd.Trajectory(gpd.GeoDataFrame(pd.DataFrame([
                {'geometry': Point(0,0), 't': datetime(2023, 1, 1, 1, 0, 0)},
                {'geometry': Point(1, 1), 't': datetime(2023, 1, 1, 3, 0, 0)},
                {'geometry': Point(1, 1), 't': datetime(2023, 1, 1, 5, 0, 0)},
                {'geometry': Point(3, 3), 't': datetime(2023, 1, 1, 7, 0, 0)}
                ]).set_index('t'), crs=4326), 1),
                config=default_config, 
                expect=False,
            ),
        ]
        for test in testcases:
            location = self.sut.stopped(test.traj, test.config)
            self.assertEqual(location, test.expect, f'{{test.name}} location value expect {{test.expect}} got {{location}}')
    
    def test_stops_gdf(self) -> None:
        @dataclass
        class Testcase:
            def __init__(self, name: str, traj: mpd.TrajectoryCollection, config: dict, expect: gpd.GeoDataFrame):
                self.name = name
                self.traj = traj
                self.config = config
                self.expect = expect

        default_config = {"stop_duration": 2, "distance_tolerance": 100}
        traj_1 = mpd.Trajectory(gpd.GeoDataFrame(pd.DataFrame([
                {'trackId': 1, 'geometry': Point(0,0), 't': datetime(2023, 1, 1, 1, 0, 0)},
                {'trackId': 1, 'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 2, 0, 0)},
                {'trackId': 1, 'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 3, 0, 0)},
                {'trackId': 1, 'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 4, 0, 0)}
                ]).set_index('t'), crs=4326), traj_id=1)
        traj_2 = mpd.Trajectory(gpd.GeoDataFrame(pd.DataFrame([
                {'trackId': 2, 'geometry': Point(0,0), 't': datetime(2023, 1, 1, 1, 0, 0)},
                {'trackId': 2, 'geometry': Point(1, 1), 't': datetime(2023, 1, 1, 3, 0, 0)},
                {'trackId': 2, 'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 5, 0, 0)},
                {'trackId': 2, 'geometry': Point(3, 3), 't': datetime(2023, 1, 1, 7, 0, 0)}
                ]).set_index('t'), crs=4326), traj_id=2)
        traj_3 = mpd.Trajectory(gpd.GeoDataFrame(pd.DataFrame([
                {'trackId': 3, 'geometry': Point(0,0), 't': datetime(2023, 1, 1, 1, 0, 0)},
                {'trackId': 3, 'geometry': Point(1, 1), 't': datetime(2023, 1, 1, 3, 0, 0)},
                {'trackId': 3, 'geometry': Point(1, 1), 't': datetime(2023, 1, 1, 5, 0, 0)},
                {'trackId': 3, 'geometry': Point(3, 3), 't': datetime(2023, 1, 1, 7, 0, 0)}
                ]).set_index('t'), crs=4326), traj_id=3)
        traj_4 = mpd.Trajectory(gpd.GeoDataFrame(pd.DataFrame([
                {'trackId': 4, 'geometry': Point(0,0), 't': datetime(2023, 1, 1, 1, 0, 0)},
                {'trackId': 4, 'geometry': Point(3, 3), 't': datetime(2023, 1, 1, 2, 0, 0)},
                {'trackId': 4, 'geometry': Point(3, 3), 't': datetime(2023, 1, 1, 3, 0, 0)},
                {'trackId': 4, 'geometry': Point(3, 3), 't': datetime(2023, 1, 1, 4, 0, 0)}
                ]).set_index('t'), crs=4326), traj_id=4)
        testcases = [
            Testcase(
                "single_stopped", 
                traj=mpd.TrajectoryCollection([traj_1, traj_2, traj_3]),
                config=default_config, 
                expect=gpd.GeoDataFrame({'trackId': [1], 'geometry': [Point(2, 2)]}, crs=4326)
            ),
            Testcase(
                "no_stops",
                traj=mpd.TrajectoryCollection([traj_2, traj_3]),
                config=default_config,
                expect=gpd.GeoDataFrame(),
            ),
            Testcase(
                "multiple_stopped",
                traj=mpd.TrajectoryCollection([traj_1, traj_2, traj_3, traj_4]),
                config=default_config,
                expect=gpd.GeoDataFrame({'trackId': [1, 4], 'geometry': [Point(2, 2), Point(3, 3)]}, crs=4326)
            ),
        ]
        for test in testcases:
            got = self.sut.stops_gdf(test.traj, test.config)
            # gdf compare dataframes doesn't work on empty
            if got.empty and test.expect.empty:
                continue
            assert_geodataframe_equal(got, test.expect, check_dtype=False)
