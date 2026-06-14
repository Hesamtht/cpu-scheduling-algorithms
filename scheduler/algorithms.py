import heapq
from collections import deque
from random import randint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class ProcessData:
    def __init__(self, num, pid, a_time, b_time, priority):
        self.num = num
        self.pid = pid
        self.a_time = a_time
        self.b_time = b_time
        self.priority = priority
        self.f_time = 0
        self.r_time = b_time
        self.w_time = 0
        self.s_time = 0
        self.res_time = 0

def idsort(x):
    return x.pid

def arrivalsort(x):
    return (x.a_time, x.priority, x.pid)

def numsort(x):
    return x.num

class Compare:
    def __init__(self, process):
        self.process = process

    def __lt__(self, other):
        if self.process.priority > other.process.priority:
            return True
        elif self.process.priority < other.process.priority:
            return False
        if self.process.pid > other.process.pid:
            return True
        return False

def insert_process_data(n, process_list):
    input_data = []

    for i in range(n):
        pid, a_time, b_time, priority = process_list[i]
        temp = ProcessData(i + 1, pid, a_time, b_time, priority)
        input_data.append(temp)

    return input_data

# ---------------------------------------------------------------------------
# Shared scheduling helpers.
#
# Every scheduler produces a per-tick CPU timeline (timeline[t] = the process
# name running during tick t, or None when the CPU is idle).  A single summary
# routine then derives every metric and the Gantt chart from that timeline, so
# the reported numbers are always consistent with the real execution order.
# ---------------------------------------------------------------------------
def _normalize(processes):
    """Accept rows shaped [name, arrival, burst, ...] -> (name, arrival, burst)."""
    return [(p[0], p[1], p[2]) for p in processes]


def _summarize(timeline, procs):
    """timeline: list of names (or None for idle) per time tick.
    procs: list of (name, arrival, burst).
    Returns (result, avg_wt, avg_tat, gantt)."""
    first_run = {}
    last_run = {}
    for t, name in enumerate(timeline):
        if name is None:
            continue
        first_run.setdefault(name, t)
        last_run[name] = t

    result = []
    total_wt = 0
    total_tat = 0
    for name, arrival, burst in procs:
        start = first_run.get(name, arrival)
        completion = last_run.get(name, arrival - 1) + 1
        turn_around = completion - arrival
        waiting = turn_around - burst
        response = start - arrival
        total_wt += waiting
        total_tat += turn_around
        result.append({
            'name': name,
            'arrival_time': arrival,
            'burst_time': burst,
            'completion_time': completion,
            'turn_around_time': turn_around,
            'waiting_time': waiting,
            'response_time': response,
        })

    # merge consecutive equal ticks (including idle) into Gantt segments
    gantt = []
    for t, name in enumerate(timeline):
        label = name if name is not None else 'idle'
        if gantt and gantt[-1]['name'] == label and gantt[-1]['end'] == t:
            gantt[-1]['end'] = t + 1
        else:
            gantt.append({'name': label, 'start': t, 'end': t + 1})

    n = len(procs)
    avg_wt = total_wt / n if n else 0
    avg_tat = total_tat / n if n else 0
    return result, avg_wt, avg_tat, gantt


def _fcfs_timeline(procs):
    timeline = []
    t = 0
    for name, arrival, burst in sorted(procs, key=lambda p: (p[1], p[0])):
        if t < arrival:                       # idle until this process arrives
            timeline.extend([None] * (arrival - t))
            t = arrival
        timeline.extend([name] * burst)
        t += burst
    return timeline


def _sjf_timeline(procs):
    rem = {p[0]: p[2] for p in procs}
    arrival = {p[0]: p[1] for p in procs}
    done = set()
    t = 0
    timeline = []
    while len(done) < len(procs):
        ready = [name for name in rem if arrival[name] <= t and name not in done]
        if not ready:
            timeline.append(None)
            t += 1
            continue
        name = min(ready, key=lambda x: (rem[x], arrival[x], x))
        timeline.extend([name] * rem[name])   # non-preemptive: run to completion
        t += rem[name]
        done.add(name)
    return timeline


def _srtf_timeline(procs):
    rem = {p[0]: p[2] for p in procs}
    arrival = {p[0]: p[1] for p in procs}
    done = 0
    t = 0
    timeline = []
    while done < len(procs):
        ready = [name for name in rem if arrival[name] <= t and rem[name] > 0]
        if not ready:
            timeline.append(None)
            t += 1
            continue
        name = min(ready, key=lambda x: (rem[x], arrival[x], x))
        timeline.append(name)
        rem[name] -= 1
        t += 1
        if rem[name] == 0:
            done += 1
    return timeline


def _rr_timeline(procs, quantum):
    order = sorted(procs, key=lambda p: (p[1], p[0]))
    rem = {p[0]: p[2] for p in procs}
    timeline = []
    queue = deque()
    n = len(order)
    idx = 0
    t = 0
    if order and order[0][1] > 0:             # idle until the first arrival
        timeline.extend([None] * order[0][1])
        t = order[0][1]
    while idx < n and order[idx][1] <= t:
        queue.append(order[idx][0])
        idx += 1
    while queue:
        name = queue.popleft()
        run = min(quantum, rem[name]) if quantum > 0 else rem[name]
        timeline.extend([name] * run)
        t += run
        rem[name] -= run
        while idx < n and order[idx][1] <= t:        # admit arrivals during the slice
            queue.append(order[idx][0])
            idx += 1
        if rem[name] > 0:                            # not finished -> back of queue
            queue.append(name)
        if not queue and idx < n:                    # CPU idle until next arrival
            timeline.extend([None] * (order[idx][1] - t))
            t = order[idx][1]
            while idx < n and order[idx][1] <= t:
                queue.append(order[idx][0])
                idx += 1
    return timeline


def mlfq_algorithm(n, process_list):
    input_data = insert_process_data(n, process_list)
    input_data.sort(key=arrivalsort)

    total_execution_time = input_data[0].a_time
    for i in range(n):
        if total_execution_time >= input_data[i].a_time:
            total_execution_time += input_data[i].b_time
        else:
            diff = input_data[i].a_time - total_execution_time
            total_execution_time += diff + input_data[i].b_time

    ghant = [-1] * total_execution_time

    pq = []                 # level 0: priority queue (highest priority runs first)
    rq = deque()            # level 1: round-robin queue (demoted processes)
    quantum = 4
    current = None          # process currently on the CPU (None == idle)
    current_in_rq = False   # True if the running process came from the rq level
    q_left = 0              # quantum ticks left for the running process

    for clock in range(total_execution_time):
        # admit every process that arrives at this tick into level 0
        for j in range(n):
            if clock == input_data[j].a_time:
                heapq.heappush(pq, Compare(input_data[j]))

        # a ready level-0 process preempts a running level-1 process
        if current is not None and current_in_rq and pq:
            rq.append(current)
            current = None

        # within level 0, a strictly higher-priority arrival preempts the current process
        if current is not None and not current_in_rq and pq:
            if pq[0].process.priority > current.priority:
                heapq.heappush(pq, Compare(current))
                current = None

        # dispatch the CPU if it is idle: prefer level 0, then level 1
        if current is None:
            if pq:
                current = heapq.heappop(pq).process
                current_in_rq = False
                q_left = quantum
            elif rq:
                current = rq.popleft()
                current_in_rq = True
                q_left = quantum

        # run the chosen process for one tick
        if current is not None:
            current.r_time -= 1
            q_left -= 1
            ghant[clock] = current.pid

            if current.r_time == 0:
                # finished
                current = None
            elif q_left == 0:
                # quantum expired: demote to (or keep in) the round-robin level
                rq.append(current)
                current = None

    input_data.sort(key=numsort)
    timeline = [pid if pid != -1 else None for pid in ghant]
    procs = [(p.pid, p.a_time, p.b_time) for p in input_data]
    return _summarize(timeline, procs)

def fcfs(processes):
    """First Come First Served (non-preemptive, arrival-aware)."""
    procs = _normalize(processes)
    return _summarize(_fcfs_timeline(procs), procs)


def rr(processes, quantum):
    """Round Robin (preemptive, arrival-aware)."""
    procs = _normalize(processes)
    return _summarize(_rr_timeline(procs, quantum), procs)


def sjf(process):
    """Shortest Job First (non-preemptive, arrival-aware)."""
    procs = _normalize(process)
    return _summarize(_sjf_timeline(procs), procs)


def srtf(process):
    """Shortest Remaining Time First (preemptive SJF, arrival-aware)."""
    procs = _normalize(process)
    return _summarize(_srtf_timeline(procs), procs)

def run_elevator_simulation(current_floor, num_requests, requests):
    # LOOK disk scheduling: serve everything below the head (moving down),
    # then everything at/above the head (moving up).
    lower_floors = sorted([f for f in requests if f < current_floor], reverse=True)
    upper_floors = sorted([f for f in requests if f >= current_floor])

    seek_sequence = [current_floor] + lower_floors + upper_floors
    all_floors = lower_floors + upper_floors

    last_floor = seek_sequence[-1]
    total_seek = sum(abs(seek_sequence[i + 1] - seek_sequence[i])
                     for i in range(len(seek_sequence) - 1))
    avg_position = sum(all_floors) / len(all_floors) if all_floors else current_floor

    return last_floor, avg_position, lower_floors, upper_floors, requests, total_seek, seek_sequence

# Banker’s Algorithm Implementation
def max_capacity(max_capacity_matrix):
    return np.array(max_capacity_matrix, dtype=int)

def allocation(allocation_matrix):
    return np.array(allocation_matrix, dtype=int)

def remaining_resources(available_matrix):
    return np.array(available_matrix, dtype=int)

def bankers_algorithm(max_capacity_matrix, allocation_matrix, available_matrix):
    max_matrix = max_capacity(max_capacity_matrix)
    allocation_matrix = allocation(allocation_matrix)
    available_matrix = remaining_resources(available_matrix)

    need = max_matrix - allocation_matrix
    n = len(allocation_matrix)

    # Safety algorithm: repeatedly grant resources to any process whose
    # remaining need can be met, then reclaim its allocation, until either
    # every process finishes (safe) or none can proceed (unsafe).
    work = available_matrix.copy()
    finish = [False] * n
    safe_sequence = []

    progress = True
    while progress:
        progress = False
        for i in range(n):
            if not finish[i] and np.all(need[i] <= work):
                work = work + allocation_matrix[i]
                finish[i] = True
                safe_sequence.append(i)
                progress = True

    is_safe = all(finish)

    return {
        'max_matrix': max_matrix.tolist(),
        'allocation_matrix': allocation_matrix.tolist(),
        'available_matrix': available_matrix.tolist(),
        'need_matrix': need.tolist(),
        'is_safe': bool(is_safe),
        'safe_sequence': [int(i) for i in safe_sequence] if is_safe else []
    }

def calculate_rr():
    num_processes = int(input("Enter the number of processes: "))
    print('------------------------')
    process_list = []
    for i in range(num_processes):
        name = input(f"Enter the name of process {i+1}: ")
        arrival_time = int(input(f"Enter the arrival time for process {name}: "))
        service_time = int(input(f"Enter the service time for process {name}: "))
        process_list.append({'name': name, 'service_time': service_time, 'arrival_time': arrival_time})
    processes = sorted(process_list, key=lambda p: p['arrival_time'])
    print('------------------------')
    quantum_time = int(input("Enter the quantum time: "))

    n = len(processes)
    remaining_bt = [process['service_time'] for process in processes]
    waiting_time = [0] * n
    turnaround_time = [0] * n
    total_wt = 0
    total_tat = 0
    t = 0
    while True:
        done = True
        for i in range(n):
            if remaining_bt[i] > 0:
                done = False
                if remaining_bt[i] > quantum_time:
                    t += quantum_time
                    remaining_bt[i] -= quantum_time
                else:
                    t += remaining_bt[i]
                    waiting_time[i] = t - processes[i]['service_time']
                    remaining_bt[i] = 0

        if done:
            break

    for i in range(n):
        turnaround_time[i] = processes[i]['service_time'] + waiting_time[i]
        total_wt += waiting_time[i]
        total_tat += turnaround_time[i]

    avg_wt = total_wt / n
    avg_tat = total_tat / n

    print("Process\t\tService Time\tWaiting Time\tTurnaround Time")
    for i in range(n):
        print(f"{processes[i]['name']}\t\t{processes[i]['service_time']}\t\t{waiting_time[i]}\t\t{turnaround_time[i]}")

    print(f"Average Waiting Time: {avg_wt:.2f}")
    print(f"Average Turnaround Time: {avg_tat:.2f}")

if __name__ == "__main__":
    calculate_rr()
