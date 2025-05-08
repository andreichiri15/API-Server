from queue import Queue, Empty
from threading import Thread, Event
import os
import json
import math

class ThreadPool:
    '''ThreadPool class to manage a pool of threads for executing tasks concurrently.'''
    def __init__(self, data, dataIngestor):
        if "TP_NUM_OF_THREADS" in os.environ:
            self.num_threads = int(os.environ["TP_NUM_OF_THREADS"])
        else:
            self.num_threads = os.cpu_count()

        self.task_queue = Queue()
        self.threads = []
        self.shutdown_event = Event()
        self.jobs_dict = {}
        self.res_dict = {}
        self.data = data
        self.dataIngestor = dataIngestor

        for i in range(self.num_threads):
            self.threads.append(TaskRunner(self.task_queue, self.shutdown_event, self.jobs_dict,
                                           self.res_dict, self.data, self.dataIngestor))
            self.threads[i].start()

    def add_task(self, task):
        '''Add task to the thread pool queue'''
        self.task_queue.put(task)

    def shutdown(self):
        '''Shutdown the thread pool by setting the shutdown event and joining all threads.'''
        self.shutdown_event.set()
        print(self.num_threads)
        for thread in self.threads:
            print("Shutdown thread")
            thread.join()

    def is_queue_empty(self):
        '''Check if the task queue is empty.'''
        return self.task_queue.empty()

class TaskRunner(Thread):
    '''TaskRunner class to execute tasks from the task queue.'''
    def __init__(self, task_queue, shutdown_event, jobs_dict, res_dict, data, dataIngestor):
        super().__init__()

        self.task_queue = task_queue
        self.shutdown_event = shutdown_event
        self.jobs_dict = jobs_dict
        self.res_dict = res_dict
        self.data = data
        self.dataIngestor = dataIngestor

    def run(self):
        while True:
            if self.task_queue.empty() and self.shutdown_event.is_set():
                break

            try:
                task = self.task_queue.get(timeout=0.1)
            except Empty:
                continue

            job_id = task[0]
            job_type = task[1]
            job_data = task[2]

            self.jobs_dict[job_id] = "running"

            res = None

            # Execute the task based on the job_type
            match job_type:
                case "state_mean":
                    state = job_data["state"]
                    question = job_data["question"]
                    res = self.find_state_mean(state, question)

                case "states_mean":
                    question = job_data["question"]
                    res = self.find_states_mean(question)

                case "best5":
                    question = job_data["question"]
                    res = self.find_best5(question)

                case "worst5":
                    question = job_data["question"]
                    res = self.find_worst5(question)

                case "global_mean":
                    question = job_data["question"]
                    res = self.find_global_mean(question)

                case "diff_from_mean":
                    question = job_data["question"]
                    res = self.find_diff_from_mean(question)

                case "state_diff_from_mean":
                    question = job_data["question"]
                    state = job_data["state"]
                    res = self.find_state_diff_from_mean(state, question)

                case "mean_by_category":
                    question = job_data["question"]
                    res = self.find_mean_by_category(question)

                case "state_mean_by_category":
                    question = job_data["question"]
                    state = job_data["state"]
                    res = self.find_state_mean_by_category(state, question)

                case _:
                    res = None

            # Save the result to the file corresponding to the job_id
            if res:
                with open(f"results/{job_id}.json", "w") as f:
                    json.dump(res, f)

            self.jobs_dict[job_id] = "done"

    def find_state_mean(self, state, question):
        '''Find the mean of a specific state for a given question.'''
        sum = 0
        count = 0

        dict_list = self.find_rows_for_question(question)

        for row in dict_list:
            if row["LocationDesc"] == state:
                sum += row["Data_Value"]
                count += 1
        if count == 0:
            return 0

        return {state: sum / count}

    def find_states_mean(self, question):
        '''Find the mean of all states for a given question.'''
        dict_list = self.find_rows_for_question(question)
        res = {}

        for row in dict_list:
            if row["LocationDesc"] not in res:
                res[row["LocationDesc"]] = {"sum": 0, "count": 0}
            res[row["LocationDesc"]]["sum"] += row["Data_Value"]
            res[row["LocationDesc"]]["count"] += 1

        new_res = {}

        for location in res:
            res[location]["mean"] = res[location]["sum"] / res[location]["count"]
            new_res[location] = res[location]["mean"]

        sorted_res = dict(sorted(new_res.items(), key=lambda x: x[1]))

        return sorted_res

    def find_rows_for_question(self, question):
        '''Find rows in data dictionary for a specific question.'''
        dict_list = []

        for row in self.data:
            if row["Question"] == question:
                dict_list.append(row)
        return dict_list

    def find_best5(self, question):
        '''Find the best 5 states for a given question.'''
        mean_states = self.find_states_mean(question)

        mean_states_list = list(mean_states.items())

        if question in self.dataIngestor.questions_best_is_min:
            return dict(mean_states_list[:5])

        return dict(mean_states_list[-5:])

    def find_worst5(self, question):
        '''Find the worst 5 states for a given question.'''
        mean_states = self.find_states_mean(question)

        mean_states_list = list(mean_states.items())

        if question in self.dataIngestor.questions_best_is_min:
            return dict(reversed(mean_states_list[-5:]))

        return dict(reversed(mean_states_list[:5]))

    def find_global_mean(self, question):
        '''Find the global mean for a given question.'''
        dict_list = self.find_rows_for_question(question)
        sum = 0
        count = 0

        for row in dict_list:
            sum += row["Data_Value"]
            count += 1

        if count == 0:
            return 0
        
        return {"global_mean": sum / count}

    def find_diff_from_mean(self, question):
        '''Find the difference from the mean for all states for a given question.'''
        states_mean = self.find_states_mean(question)

        global_mean = self.find_global_mean(question)["global_mean"]

        res = {}

        for state in states_mean:
            res[state] = global_mean - states_mean[state]
        return res

    def find_state_diff_from_mean(self, state, question):
        '''Find the difference from the mean for a specific state for a given question.'''
        state_mean = self.find_state_mean(state, question)

        global_mean = self.find_global_mean(question)

        return {state: global_mean["global_mean"] - state_mean[state]}

    def find_mean_by_category(self, question):
        '''Find the mean by category for a given question.'''
        dict_list = self.find_rows_for_question(question)
        res = {}

        for row in dict_list:
            if any(
                val is None or (isinstance(val, float) and math.isnan(val))
                for val in [row["StratificationCategory1"], row["Stratification1"]]
            ):
                continue
            new_key = [row["LocationDesc"], row["StratificationCategory1"], row["Stratification1"]]
            new_key = tuple(new_key)
            if new_key not in res:
                res[new_key] = {"sum": 0, "count": 0}
            res[new_key]["sum"] += row["Data_Value"]
            res[new_key]["count"] += 1

        new_res = {}

        for key in res:
            str_key = str(key)
            new_res[str_key] = res[key]["sum"] / res[key]["count"]

        sorted_res = dict(sorted(new_res.items(), key=lambda x: x[0]))

        return sorted_res

    def find_state_mean_by_category(self, state, question):
        '''Find the mean by category for a specific state for a given question.'''
        dict_list = self.find_rows_for_question(question)
        res = {}

        for row in dict_list:
            if row["LocationDesc"] == state:
                new_key = [row["StratificationCategory1"], row["Stratification1"]]
                new_key = tuple(new_key)
                if new_key not in res:
                    res[new_key] = {"sum": 0, "count": 0}
                res[new_key]["sum"] += row["Data_Value"]
                res[new_key]["count"] += 1

        new_res = {}

        for key in res:
            str_key = str(key)  # convert the tuple to a string
            new_res[str_key] = res[key]["sum"] / res[key]["count"]

        sorted_res = dict(sorted(new_res.items(), key=lambda x: x[0]))

        return {state: sorted_res}
