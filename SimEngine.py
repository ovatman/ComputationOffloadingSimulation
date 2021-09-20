from sortedcontainers import SortedDict
import time


class SimEngine:
    __instance = None

    def __init__(self):
        self.timeline = SortedDict()
        self.curtick = 0
        self.jobs = None
        self.local = None
        self.terrestrial = None
        self.aerial = None
        self.timeres = 10 ** 6
        self.inst_fact = 10 ** 6
        self.datarate_fact = (10 ** 6) / 8
        self.data_fact = 10 ** 3
        self.dist_fact = 1
        self.c = 3 * 10 ** 8
        SimEngine.__instance = self

    def register(self, tick, pair):
        if tick not in self.timeline:
            self.timeline[tick] = []
        if pair not in self.timeline[tick]:
            self.timeline[tick].append(pair)
        for atick in self.timeline.keys():
            if pair in self.timeline[atick] and atick != tick:
                self.timeline[atick].remove(pair)

    def deregister(self, tick, pair):
        if tick in self.timeline:
            for pairs in self.timeline[tick]:
                if pairs[0] is pair[0] and pairs[1] is pair[1]:
                    self.timeline[tick].remove(pairs)

    def start(self):
        num_of_events = 0
        start = time.time()
        timeout = False
        while (len(self.timeline.keys()) > 0 and not timeout):
            tick = min(self.timeline.keys())
            if tick > self.curtick:
                self.curtick = tick
                for event in self.timeline[tick]:
                    event[1]()
                    num_of_events += 1
                    if num_of_events % 10 ** 2 == 0:
                        passed = time.time() - start
                        if passed > 30:
                            timeout = True
                            break
                del self.timeline[tick]

        return not timeout

    @staticmethod
    def the_engine():
        if SimEngine.__instance == None:
            SimEngine()
        return SimEngine.__instance

    def reset(self):
        self.timeline.clear()
        self.curtick = 0
        if self.jobs is not None:
            for j in self.jobs:
                j.reset()

    def set_mode(self, m):
        if self.jobs is not None:
            for j in self.jobs:
                j.mode = m
