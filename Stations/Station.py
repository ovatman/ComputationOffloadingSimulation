import math

from SimEngine import SimEngine


class Station:
    def __init__(self):
        self.proc = None
        self.curproc = None
        self.opmean = None
        self.opdev = None
        self.ul = None
        self.dl = None
        self.dist = None
        self.id = None
        self.tasks = {}

    def optime(self, task):
        return task.ultime + 1

    def proctime(self, task):
        self.update_rem_procs()
        self.tasks[task] = (SimEngine.the_engine().curtick, task.process_size * SimEngine.the_engine().inst_fact)
        self.curproc = int(self.proc / len(self.tasks.keys()))
        self.calculate_finish_times()

    def dltime(self, task):
        if task in self.tasks:
            self.tasks.pop(task)
            self.update_rem_procs()
            self.curproc = int(self.proc / len(self.tasks.keys())) if len(self.tasks.keys()) > 1 else self.proc
            self.calculate_finish_times()
            return self.calculate_dltime(task)
        return SimEngine.the_engine().curtick

    def update_rem_procs(self):
        for task in self.tasks.keys():
            passed_time = SimEngine.the_engine().curtick - self.tasks[task][0]
            passed_ins = (self.curproc * SimEngine.the_engine().inst_fact) * (
                    passed_time / SimEngine.the_engine().timeres)
            self.tasks[task] = (SimEngine.the_engine().curtick, max(0, (self.tasks[task][1]) - passed_ins))
            SimEngine.the_engine().deregister(task.dltime, (task, task.receive_start))

    def calculate_finish_times(self):
        for task in self.tasks.keys():
            task.dltime = SimEngine.the_engine().curtick + max(0, int(math.ceil(SimEngine.the_engine().timeres * (
                    self.tasks[task][1] / (self.curproc * SimEngine.the_engine().inst_fact)))))
            SimEngine.the_engine().register(task.dltime, (task, task.receive_start))
