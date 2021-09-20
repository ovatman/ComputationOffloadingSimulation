from Stations.Station import Station
from SimEngine import SimEngine


class Terrestrial(Station):
    def __init__(self):
        Station.__init__(self)
        self.id = "Terrestrial"

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
        tst = Terrestrial()

        tst.proc = conf["stations"]["terrestrial"]["proc"]
        tst.opmean = conf["stations"]["terrestrial"]["opmean"]
        tst.opdev = conf["stations"]["terrestrial"]["opdev"]
        tst.ul = conf["stations"]["terrestrial"]["ul"]
        tst.dl = conf["stations"]["terrestrial"]["dl"]
        tst.dist = conf["stations"]["terrestrial"]["dist"]

        return tst
