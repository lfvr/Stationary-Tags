from dataclasses import dataclass
from datetime import datetime
import os
import unittest
import geopandas as gpd
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

    def test_find_stopped(self) -> None:

        @dataclass
        class Testcase:
            def __init__(self, name: str, traj: mpd.Trajectory, config: dict, expect: gpd.GeoSeries):
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
            location = self.sut.find_stopped(test.traj, test.config)
            self.assertEqual(location, test.expect, f'{{test.name}} location value expect {{test.expect}} got {{location}}')
    
    def test_plot_map(self) -> None:
        
        @dataclass
        class Testcase:
            def __init__(self, name: str, points: list[Point], expect: str):
                self.name = name
                self.points = points
                self.expect = expect
        
        testcases = [
            Testcase(
                name="stop_at_end_returns_point", 
                points=gpd.GeoDataFrame(pd.DataFrame([
                {'index': 1, 'geometry': Point(-58.66, -34.58)},
                {'index': 2, 'geometry': Point(-47.91, -15.78)},
                ]).set_index('index'), crs=4326),
                expect='test_1.png'),
            ]

        for test in testcases:
            self.sut.plot_map(test.points)
            result = compare_images(self.sut.moveapps_io.create_artifacts_file(test.expect), self.sut.moveapps_io.create_artifacts_file('stationarity.png'), tol=5)
            self.assertIsNone(result, result)
