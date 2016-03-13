"""
Trilateration Simulation Classes

Copyright: David Petrie (www.davidpetrie.com, @davidcpetrie)
Author: David Petrie, 2016 (me@davidpetrie.com)
"""


import sys
import math
import datetime

# the goal with this is to estimate the distance between a detector and a signal, based
# on readings of the same signal over time.  If we know the location of the detector, and
# have an estimate of the distance to the signal, then we should be able to use trilateration
# to estimate the position of the beacon.... right?
_DEFAULT_IBEACON_POWER = -59
_DEFAULT_MAX_POWER = -72

# max range in meters
_DEFAULT_MAX_RANGE = 10

# Path attenuation estimate
_DEFAULT_PATH_LOSS_ESTIMATE = 2.5



class vec3(object):
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z


    def add(self, b):
        self.x += b.x
        self.y += b.y
        self.z += b.z


    def distance_from(self, b):
        x_dist = abs(self.x - b.x)
        y_dist = abs(self.y - b.y)
        return math.sqrt((x_dist * x_dist) + (y_dist * y_dist))



class beacon_event(object):
    def __init__(self, beacon_id, rssi, path_loss_estimate):
        self.rssi = rssi
        self.path_loss_estimate = path_loss_estimate
        self.beacon_id = beacon_id



# For the detector's current state, log all signals received.
class detector_log_event(object):
    def __init__(self, detector_id, detector_position, timestamp):
        self.detector_id = detector_id
        self.detector_position = vec3(detector_position.x, detector_position.y)
        self.timestamp = timestamp
        self.beacon_signals = {}


    def log_beacon_signal(self, beacon_id, calibrated_power, rssi, path_loss_estimate=_DEFAULT_PATH_LOSS_ESTIMATE):
        signal = beacon_signal(beacon_id, calibrated_power, rssi, path_loss_estimate)
        self.beacon_signals[beacon_id] = signal


    def print_events(self):
        log_header = "[LOG] At {0}, position: {1} {2}, detector \"{3}\" received {4} signals"
        print log_header.format(self.timestamp, self.detector_position.x, self.detector_position.y,
            self.detector_id, len(self.beacon_signals))

        if len(self.beacon_signals) == 0:
            print "\t*** NO SIGNALS DETECTED ***"
            return

        for signal in self.beacon_signals.values():
            estimated_distance = signal.estimate_distance()
            print "\t[{0}] with rssi {1} dBm, distance: {2} m".format(signal.beacon_id, signal.rssi, estimated_distance)


    # Get the intersection points between this log even and another
    def intersects(self, beacon_id, log_event):
        # signals
        signal_0 = self.beacon_signals[beacon_id]
        signal_1 = log_event.beacon_signals[beacon_id]

        a = self.detector_position.x
        b = self.detector_position.y

        c = log_event.detector_position.x
        d = log_event.detector_position.y

        D = math.sqrt( ((c-a) ** 2) + ((d - b) ** 2))

        # radius
        r0 = signal_0.estimate_distance()
        r1 = signal_1.estimate_distance()

        if r0 + r1 <= D:
            return []

        if abs(r0 - r1) > D:
            return []

        delta = 0.25 * math.sqrt((D + r0 + r1) * (D + r0 - r1) * (D - r0 + r1) * (-D + r0 + r1))

        alpha, beta = [0, 0], [0, 0]
        alpha[0] = ((a + c)/2) + (((c - a) * ((r0 ** 2) - (r1 ** 2)))/(2 * (D ** 2))) + (2 * ((b - d)/(D ** 2)) * delta)
        alpha[1] = ((b + d)/2) + (((d - b) * ((r0 ** 2) - (r1 ** 2)))/(2 * (D ** 2))) - (2 * ((a - c)/(D ** 2)) * delta)

        beta[0] = ((a + c)/2) + (((c - a) * ((r0 ** 2) - (r1 ** 2)))/(2 * (D ** 2))) - (2 * ((b - d)/(D ** 2)) * delta)
        beta[1] = ((b + d)/2) + (((d - b) * ((r0 ** 2) - (r1 ** 2)))/(2 * (D ** 2))) + (2 * ((a - c)/(D ** 2)) * delta)

        return [alpha, beta]


class beacon_signal(object):
    def __init__(self, beacon_id, calibrated_power, rssi, path_loss_estimate=_DEFAULT_PATH_LOSS_ESTIMATE):
        self.beacon_id = beacon_id
        self.calibrated_power = calibrated_power
        self.rssi = rssi
        self.path_loss_estimate = path_loss_estimate


    # rssi is the signal strength received at the position
    # some debate as to valid values for the path_loss_estimate:
    # - free space: 2
    # we could just pick a constant of 3 and go from there.
    def estimate_distance(self):
        exp = (self.calibrated_power - self.rssi) / (-10 * self.path_loss_estimate)
        return math.sqrt(math.pow(10, exp))


class abstract_signal_finder(object):
    def __init__(self):
        pass

    def detect_beacon_signals(self, location):
        return []



class dummy_beacon(object):
    def __init__(self, id, position, max_range=_DEFAULT_MAX_RANGE, max_power=_DEFAULT_MAX_POWER, calibrated_power=_DEFAULT_IBEACON_POWER):
        self.id = id
        self.position = position
        self.max_range = max_range
        self.max_power = max_power
        self.calibrated_power = calibrated_power


    def dummy_rssi(self, distance):
        if (self.max_range < 0):
            return 0

        if distance > self.max_range:
            return 0

        return self.calibrated_power + ((10 * _DEFAULT_PATH_LOSS_ESTIMATE) * math.log10(distance * distance))


        #linear_ratio = ((self.max_range - distance) / self.max_range)
        #if linear_ratio > 0:
        #    return linear_ratio * self.max_power
        #else:
        #    return 0


# contains several test signals.  we use this to test the signal detector.
#
# at the given location, return beacon_signal info -- we can determine the exact
# distance here, and thus we can return specific rssi's back.
class dummy_signal_finder(abstract_signal_finder):
    def __init__(self):
        abstract_signal_finder.__init__(self)
        self.dummy_beacons = []


    def add_beacon(self, id, position):
        beacon = dummy_beacon(id, position)
        self.dummy_beacons.append(beacon)


    def detect_beacon_signals(self, location):
        signals = []
        for beacon in self.dummy_beacons:
            distance = beacon.position.distance_from(location)
            if distance <= beacon.max_range:
                rssi = beacon.dummy_rssi(distance)
                calibrated_power = beacon.calibrated_power
                signal = beacon_signal(beacon.id, calibrated_power, rssi)
                signals.append(signal)
        return signals



class detector(object):
    def __init__(self, id, start_position, signal_finder):
        self.id = id
        self.start_position = start_position
        self.current_position = start_position
        self.signal_finder = signal_finder
        self.log = []


    # at the current position, for the current timestamp log all the signals detected.
    def check_signals(self):
        pos = self.current_position
        log_entry = detector_log_event(self.id, pos, datetime.datetime.now())
        beacon_signals = self.signal_finder.detect_beacon_signals(self.current_position)

        for signal in beacon_signals:
            log_entry.log_beacon_signal(signal.beacon_id, signal.calibrated_power, signal.rssi)

        self.log.append(log_entry)


    def next_position(self, displacement):
        self.current_position.add(displacement)


    def dump_log(self):
        for log_event in self.log:
            log_event.print_events()



def create_signal(x, y, radius):
    _DEFAULT_Z = 0
    pos = vec3(x, y, _DEFAULT_Z)
    return signal(pos, radius)


def create_detector(x, y, radius):
    _DEFAULT_Z = 0
    pos = vec3(x, y, _DEFAULT_Z)
    return detector(pos, radius)


def signal_distance(signal_a, signal_b):
    return signal_a.position.distance(signal_b.position)


# Signal a is at position 1, 5, radius 7
# Signal b is at position 8, 3, radius 10
# Detector c is at 4, 2, radius 15
def main():
    signal_finder = dummy_signal_finder()
    signal_finder.add_beacon("tango", vec3(1, 5))
    signal_finder.add_beacon("foxtrot", vec3(8, 3))
    test_detector = detector("backpack", vec3(-10,-10), signal_finder)

    n = 0
    while n < 30:
        test_detector.check_signals()
        test_detector.next_position(vec3(1,1))
        n = n+1

    test_detector.dump_log()


if __name__ == "__main__":
    main()
