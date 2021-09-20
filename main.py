import json
import sys
from JobsnTasks import Job
from Stations import Local, Terrestrial, Aerial
from SimEngine import SimEngine


def get_completions(jobs):
    all_tasks = []

    for ajob in jobs:
        all_tasks += ajob.tasks

    all_times = []
    end_times = []

    for atask in all_tasks:
        all_times.append(atask.endtime - atask.start_time)
        end_times.append(atask.endtime)

    return sum(all_times) / (len(all_tasks) * SimEngine.the_engine().timeres), max(end_times) / SimEngine.the_engine().timeres


if __name__ == "__main__":
    with open(sys.argv[1]) as conffile:
        conf = json.load(conffile)

    results = {"Local": [], "Terrestrial": [], "Aerial": [], "Mixed": []}

    SimEngine.the_engine().jobs = Job.Job.generate_jobs_conf(conf)
    SimEngine.the_engine().terrestrial = Terrestrial.Terrestrial.generate_station(conf)
    SimEngine.the_engine().local = Local.Local.generate_station(conf)
    SimEngine.the_engine().aerial = Aerial.Aerial.generate_station(conf)

    for m in results.keys():
        SimEngine.the_engine().reset()
        SimEngine.the_engine().set_mode(m)

        for ajob in SimEngine.the_engine().jobs:
            SimEngine.the_engine().register(ajob.arrv_tick, (ajob, ajob.start_job))

        success = SimEngine.the_engine().start()
        if success:
            out = get_completions(SimEngine.the_engine().jobs)
            results[m].append(str(out[0]))

    print(results)

