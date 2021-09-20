from Stations.Station import Station


class Local(Station):
    def __init__(self):
        Station.__init__(self)
        self.dist = 0
        self.id = "Local"

    def ultime(self, task):
        return task.start_time + 1

    def calculate_dltime(self, task):
        return task.dltime + 1

    @staticmethod
    def generate_station(conf):
        lcl = Local()

        lcl.proc = lcl.curproc = conf["stations"]["local"]["proc"]
        lcl.opmean = conf["stations"]["local"]["opmean"]
        lcl.opdev = conf["stations"]["local"]["opdev"]

        return lcl
