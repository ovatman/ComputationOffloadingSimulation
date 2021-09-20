from Utils import Distributions
from SimEngine import SimEngine
import random


class Task:
    def __init__(self, job, i):
        self.job = job
        self.id = i
        self.input_size = None
        self.output_size = None
        self.process_size = None
        self.offload_to = None
        self.start_time = None
        self.ultime = None
        self.proctime = None
        self.dltime = None
        self.endtime = None
        self.station = None
        self.characteristic = None

    def reset(self):
        self.start_time = None
        self.ultime = None
        self.proctime = None
        self.dltime = None
        self.endtime = None
        self.station = None

    def assign_characteristic(self):
        self.characteristic = ""
        if self.input_size < 10000:
            self.characteristic += "0"
        else:
            self.characteristic += "1"

        if self.output_size < 10000:
            self.characteristic += "0"
        else:
            self.characteristic += "1"

        if self.process_size < 100000:
            self.characteristic += "0"
        else:
            self.characteristic += "1"

    def start(self):
        SimEngine.the_engine().deregister(SimEngine.the_engine().curtick, (self, self.start))
        if self.offload_to == "Terrestrial":
            self.station = SimEngine.the_engine().terrestrial
        elif self.offload_to == "Local":
            self.station = SimEngine.the_engine().local
        else:
            self.station = SimEngine.the_engine().aerial

        SimEngine.the_engine().register(self.start_time, (self, self.submit_start))

    def submit_start(self):
        SimEngine.the_engine().deregister(SimEngine.the_engine().curtick, (self, self.submit_start))
        self.ultime = self.station.ultime(self)
        SimEngine.the_engine().register(self.ultime, (self, self.submit_end))

    def submit_end(self):
        SimEngine.the_engine().deregister(SimEngine.the_engine().curtick, (self, self.submit_end))
        self.proctime = self.station.optime(self)
        SimEngine.the_engine().register(self.proctime, (self, self.process_start))

    def process_start(self):
        SimEngine.the_engine().deregister(SimEngine.the_engine().curtick, (self, self.process_start))
        self.station.proctime(self)

    def receive_start(self):
        SimEngine.the_engine().deregister(SimEngine.the_engine().curtick, (self, self.receive_start))
        self.endtime = self.station.dltime(self)
        SimEngine.the_engine().register(self.endtime, (self, self.receive_end))

    def receive_end(self):
        SimEngine.the_engine().deregister(self.endtime, (self, self.receive_end))

    def get_times(self):
        return [(self.ultime - self.start_time) / SimEngine.the_engine().timeres,
                (self.proctime - self.ultime) / SimEngine.the_engine().timeres,
                (self.dltime - self.proctime) / SimEngine.the_engine().timeres,
                (self.endtime - self.dltime) / SimEngine.the_engine().timeres]

    @staticmethod
    def generate_tasks_conf(conf, job):
        tasks = []

        inps = Distributions.get_distribution(conf["jobs"]["tasks"]["input"]["type"],
                                              conf["jobs"]["tasks"]["input"]["distparam"], job.num_of_tasks)
        outs = Distributions.get_distribution(conf["jobs"]["tasks"]["output"]["type"],
                                              conf["jobs"]["tasks"]["output"]["distparam"], job.num_of_tasks)
        num_of_small_tasks = int(job.num_of_tasks * conf["jobs"]["tasks"]["psmall"]["mixratio"])
        num_of_large_tasks = job.num_of_tasks - num_of_small_tasks
        procs = Distributions.get_distribution(conf["jobs"]["tasks"]["psmall"]["type"],
                                               conf["jobs"]["tasks"]["psmall"]["distparam"], num_of_small_tasks) \
                + Distributions.get_distribution(conf["jobs"]["tasks"]["plarge"]["type"],
                                                 conf["jobs"]["tasks"]["plarge"]["distparam"], num_of_large_tasks)
        random.shuffle(procs)

        for i in range(job.num_of_tasks):
            tasks.append(Task(job, i))
            ins = int(inps[i])
            os = int(outs[i])
            ps = int(procs[i] * 10 ** 6)
            tasks[i].input_size = 1 * 10 ** 6 if ins > 1 * 10 ** 6 else ins
            tasks[i].output_size = 1 * 10 ** 6 if os > 1 * 10 ** 6 else os
            tasks[i].process_size = 10 ** 11 if ps > 10 ** 11 else ps
            tasks[i].assign_characteristic()

        return tasks