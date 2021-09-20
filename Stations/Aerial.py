from Stations.Station import Station
from SimEngine import SimEngine
import Utils.ChannelModel as CM
import math


class Aerial(Station):
    def __init__(self):
        Station.__init__(self)
        self.temp = None
        self.bandwidth = None
        self.carrierfreq = None
        self.noise = None
        self.s_n_r = None
        self.rice_param = None
        self.g_3 = None
        self.receive_power = None
        self.id = "Aerial"

    def ultime(self, task):
        ultime = 1
        if self.dist > 0:
            ultime = int(
                (task.input_size * SimEngine.the_engine().data_fact) / (self.ul * SimEngine.the_engine().datarate_fact))
            ultime = ultime * SimEngine.the_engine().timeres
            ultime += int((self.dist / SimEngine.the_engine().c) * SimEngine.the_engine().timeres)
        return task.start_time + ultime

    def calculate_dltime(self, task):
        dltime = 1
        if self.dist > 0:
            dltime = int((task.output_size * SimEngine.the_engine().data_fact) / (
                        self.ul * SimEngine.the_engine().datarate_fact))
            dltime = dltime * SimEngine.the_engine().timeres
            dltime += int((self.dist / SimEngine.the_engine().c) * SimEngine.the_engine().timeres)
        return task.dltime + dltime

    @staticmethod
    def generate_station(conf):
        tst = Aerial()

        tst.proc = conf["stations"]["aerial"]["proc"]
        tst.opmean = conf["stations"]["aerial"]["opmean"]
        tst.opdev = conf["stations"]["aerial"]["opdev"]
        tst.dist = conf["stations"]["aerial"]["dist"]
        tst.temp = conf["stations"]["aerial"]["temp"] + 273.15
        tst.bandwidth = conf["stations"]["aerial"]["bandwidth"]
        tst.carrierfreq = conf["stations"]["aerial"]["carrierfreq"]
        tst.noise = conf["stations"]["aerial"]["noise"] * 10 ** -23
        tst.rice_param = conf["stations"]["aerial"]["rice_param"]
        tst.receive_power = conf["stations"]["aerial"]["receive_power"]

        tst.s_n_r = CM.calculate_params(tst)

        raw_rate = (tst.bandwidth * math.log2(1 + 10 ** (tst.s_n_r / 10))) / 10 ** 6
        rates = [7, 14.1, 21.1, 31.7, 42.3, 64.3, 85.7, 161.9]
        for i in range(len(rates)):
            if rates[i] > raw_rate and i > 0:
                tst.ul = tst.dl = rates[i - 1]
            elif rates[i] > raw_rate and i == 0:
                tst.ul = tst.dl = 0
        if raw_rate > rates[-1]:
            tst.ul = tst.dl = rate[-1]

        return tst
