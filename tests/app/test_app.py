from dataclasses import dataclass
from datetime import datetime
import os
import unittest
import geopandas as gpd
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

    def test_app_returns_input(self):
        # prepare
        expected: mpd.TrajectoryCollection = pd.read_pickle(os.path.join(ROOT_DIR, 'tests/resources/app/input2.pickle'))
        config: dict = {"stop_duration": 12, "distance_tolerance": 100}

        # execute
        actual = self.sut.execute(data=expected, config=config)

        # verify
        self.assertEqual(expected, actual)

    def test_find_stops(self):

        @dataclass
        class Testcase:
            def __init__(self, name: str, traj: mpd.Trajectory, config: dict, expect: tuple[bool, Point]):
                self.name = name
                self.traj = traj
                self.config = config
                self.expect = expect

        default_config = {
            "stop_duration": 12,
            "distance_tolerance": 100,
        }
        testcases = [
            Testcase(
                "stop_at_end", 
                traj=mpd.Trajectory(gpd.GeoDataFrame(pd.DataFrame([
                {'geometry': Point(0,0), 't': datetime(2023, 1, 1, 1, 0, 0)},
                {'geometry': Point(2, 2), 't': datetime(2023,1,1,7,0,0)},
                {'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 13, 0, 0)},
                {'geometry': Point(2, 2), 't': datetime(2023, 1, 1, 20, 0, 0)}
                ]).set_index('t'), crs=4326), 1),
                config=default_config, 
                expect=[True, Point(2, 2)])
        ]
        for test in testcases:
            stationary, location = self.sut.find_stops(test.traj, test.config)
            self.assertEqual(stationary, test.expect[0])
            self.assertEqual(location, test.expect[1])