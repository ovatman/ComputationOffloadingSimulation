import math
from JobsnTasks import Task
from Utils import Distributions
import networkx as nx
import operator
from SimEngine import SimEngine


class Job:
    def __init__(self, i):
        self.id = i
        self.num_of_tasks = None
        self.tasks = []
        self.deps = []
        self.arrv_tick = None
        self.task_graph = None
        self.clusters = []
        self.proc_x = None
        self.io_x = None
        self.mode = None

    def reset(self):
        for t in self.tasks:
            t.reset()

    def import_graph(self):
        adj_list = nx.generate_adjlist(self.task_graph)

        for i in range(self.num_of_tasks):
            self.deps.append(self.num_of_tasks * [0])

        for line in adj_list:
            nodes = line.split(" ")
            src = int(nodes[0])
            for node in nodes[1:]:
                dst = int(node)
                self.deps[src][dst] = self.deps[dst][src] = 1

        for cc in nx.connected_components(self.task_graph):
            self.clusters.append(list(map(int, str(cc).replace("{", "").replace("}", "").replace(",", "").split(" "))))

    def start_job(self):
        SimEngine.the_engine().deregister(SimEngine.the_engine().curtick, (self, self.start_job))
        for cluster in self.clusters:
            offload_to = self.decide_offload(cluster)
            for id in cluster:
                self.tasks[id].offload_to = offload_to

        for task in self.tasks:
            task.start_time = self.arrv_tick
            SimEngine.the_engine().register(task.start_time, (task, task.start))

    def total_proc(self, cluster):
        tot_proc = 0
        for id in cluster:
            tot_proc += self.tasks[id].process_size
        return tot_proc / len(cluster)

    def total_io(self, cluster):
        tot_io = 0
        for id in cluster:
            tot_io += self.tasks[id].output_size
            tot_io += self.tasks[id].input_size
        return tot_io / (2 * len(cluster))

    def decide_offload(self, cluster):
        count = {"000": 0, "001": 0, "010": 0, "011": 0, "100": 0, "101": 0, "110": 0, "111": 0}
        for id in cluster:
            count[self.tasks[id].characteristic] += 1

        maxbin = max(count.items(), key=operator.itemgetter(1))[0]
        if self.mode == "Mixed":
            alpha = self.total_proc(cluster) / self.total_io(cluster)
            if 0.1 < alpha <= 50:
                if maxbin[2] == "0":
                    return "Local"
                elif maxbin[2] == "1" and (maxbin[0] == "1" or maxbin[1] == "1"):
                    return "Terrestrial"
                return "Aerial"
            elif alpha <= 0.1:
                return "Local"
            else:
                return "Aerial"
        else:
            return self.mode

    @staticmethod
    def generate_jobs_conf(conf):
        jobs = []

        arrvs = Distributions.get_distribution(conf["jobs"]["interarrival"]["type"],
                                               conf["jobs"]["interarrival"]["distparam"], conf["jobs"]["count"])
        tasknums = Distributions.get_distribution(conf["jobs"]["tasks"]["type"], conf["jobs"]["tasks"]["distparam"],
                                                  conf["jobs"]["count"])

        for i in range(conf["jobs"]["count"]):
            jobs.append(Job(i))
            jobs[i].num_of_tasks = int(math.ceil(tasknums[i]))
            jobs[i].arrv_tick = int(arrvs[i] * SimEngine.the_engine().timeres)
            jobs[i].tasks = Task.Task.generate_tasks_conf(conf, jobs[i])
            jobs[i].task_graph = nx.erdos_renyi_graph(jobs[i].num_of_tasks, conf["jobs"]["density"])
            jobs[i].import_graph()

        return jobs
