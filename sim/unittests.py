"""
Test Data, return test data for both training and testing data.

Copyright: David Petrie (www.davidpetrie.com, @davidcpetrie)
Author: David Petrie, 2016 (me@davidpetrie.com)
"""

import datetime
import unittest
import trilat
import math

_FIRST_BEACON_ID = "a"
_SECOND_BEACON_ID = "b"

_FIRST_BEACON_FIXED_DISTANCE = 3
_SECOND_BEACON_FIXED_DISTANCE = 4

_FIXED_RSSI_FOR_TESTING = 0
_PATH_LOSS_ESTIMATE = 1

class test_trilateration(unittest.TestCase):
    def setUp(self):
        self.log_event_a = trilat.detector_log_event(_FIRST_BEACON_ID, trilat.vec3(1, 2, 0), 0)
        self.log_event_b = trilat.detector_log_event(_FIRST_BEACON_ID, trilat.vec3(3, -1, 0), 0)

        # We want to force the estimated signal strength value of the beacon.
        # These are the values we need to plug into log_beacon_signal so we can test
        # receive required values for the estimate_distance function.
        calibrated_power_a = (math.log10(_FIRST_BEACON_FIXED_DISTANCE ** 2)) * -10
        calibrated_power_b = (math.log10(_SECOND_BEACON_FIXED_DISTANCE ** 2)) * -10

        rssi_a, rssi_b = 0, 0

        self.log_event_a.log_beacon_signal(_FIRST_BEACON_ID, calibrated_power_a, rssi_a, _PATH_LOSS_ESTIMATE)
        self.log_event_b.log_beacon_signal(_FIRST_BEACON_ID, calibrated_power_b, rssi_b, _PATH_LOSS_ESTIMATE)



    def test_estimate_distance(self):
        signal_0 = self.log_event_a.beacon_signals[_FIRST_BEACON_ID]
        signal_1 = self.log_event_b.beacon_signals[_FIRST_BEACON_ID]

        self.assertEqual(_FIRST_BEACON_FIXED_DISTANCE, signal_0.estimate_distance())
        self.assertEqual(_SECOND_BEACON_FIXED_DISTANCE, signal_1.estimate_distance())


    def test_transform_data(self):
        trilateration_result = self.log_event_a.intersects(_FIRST_BEACON_ID, self.log_event_b)

        print trilateration_result

        self.assertEqual(1, 1)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(test_trilateration)
    unittest.TextTestRunner(verbosity=2).run(suite)
