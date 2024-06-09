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

    pq = []
    rq = deque()
    cpu_state = 0
    quantum = 4
    current = ProcessData(-2, -2, 0, 0, 999999)

    for clock in range(total_execution_time):
        for j in range(n):
            if clock == input_data[j].a_time:
                heapq.heappush(pq, Compare(input_data[j]))

        if cpu_state == 0:
            if pq:
                current = heapq.heappop(pq).process
                cpu_state = 1
                pq_process = 1
                quantum = 4
            elif rq:
                current = rq.popleft()
                cpu_state = 1
                rq_process = 1
                quantum = 4
        elif cpu_state == 1:
            if pq_process == 1 and pq:
                if pq[0].process.priority < current.priority:
                    rq.append(current)
                    current = heapq.heappop(pq).process
                    quantum = 4
            elif rq_process == 1 and pq:
                rq.append(current)
                current = heapq.heappop(pq).process
                rq_process = 0
                pq_process = 1
                quantum = 4

        if current.pid != -2:
            current.r_time -= 1
            quantum -= 1
            ghant[clock] = current.pid
            if current.r_time == 0:
                cpu_state = 0
                quantum = 4
                current = ProcessData(-2, -2, 0, 0, 999999)
                rq_process = 0
                pq_process = 0
            elif quantum == 0:
                rq.append(current)
                current = ProcessData(-2, -2, 0, 0, 999999)
                rq_process = 0
                pq_process = 0
                cpu_state = 0

    input_data.sort(key=idsort)

    for i in range(n):
        for k in range(total_execution_time - 1, -1, -1):
            if ghant[k] == input_data[i].pid:
                input_data[i].f_time = k + 1
                break

    for i in range(n):
        for k in range(total_execution_time):
            if ghant[k] == input_data[i].pid:
                input_data[i].s_time = k
                break

    input_data.sort(key=numsort)

    results = []
    for i in range(n):
        input_data[i].res_time = input_data[i].s_time - input_data[i].a_time
        input_data[i].w_time = (input_data[i].f_time - input_data[i].a_time) - input_data[i].b_time
        results.append((input_data[i].pid, input_data[i].res_time, input_data[i].f_time, input_data[i].w_time))

    return results

def fcfs(processes):
    def waitingTime(processes, wt):
        n = len(processes)
        wt[0] = 0
        for i in range(1, n):
            wt[i] = processes[i-1][2] + wt[i-1] - (processes[i][1] - processes[i-1][1])
            if wt[i] < 0:
                wt[i] = 0

    def turnAroundTime(processes, wt, tat):
        for i in range(len(processes)):
            tat[i] = processes[i][2] + wt[i]

    n = len(processes)
    wt = [0] * n
    tat = [0] * n
    total_wt = 0
    total_tat = 0

    waitingTime(processes, wt)
    turnAroundTime(processes, wt, tat)

    result = []
    for i in range(n):
        result.append({
            'name': processes[i][0],
            'arrival_time': processes[i][1],
            'burst_time': processes[i][2],
            'waiting_time': wt[i],
            'turn_around_time': tat[i]
        })
        total_wt += wt[i]
        total_tat += tat[i]

    avg_wt = total_wt / n
    avg_tat = total_tat / n

    return result, avg_wt, avg_tat

def rr(processes, quantum):
    def waitingTime(processes, n, wt, quantum):
        rem_bt = [0] * n
        for i in range(n):
            rem_bt[i] = processes[i][2]
        t = 0
        while True:
            done = True
            for i in range(n):
                if rem_bt[i] > 0:
                    done = False
                    if rem_bt[i] > quantum:
                        t += quantum
                        rem_bt[i] -= quantum
                    else:
                        t += rem_bt[i]
                        wt[i] = t - processes[i][2]
                        rem_bt[i] = 0
            if done:
                break

    def turnAroundTime(processes, n, wt, tat):
        for i in range(n):
            tat[i] = processes[i][2] + wt[i]

    n = len(processes)
    wt = [0] * n
    tat = [0] * n
    total_wt = 0
    total_tat = 0

    waitingTime(processes, n, wt, quantum)
    turnAroundTime(processes, n, wt, tat)

    result = []
    for i in range(n):
        result.append({
            'name': processes[i][0],
            'arrival_time': processes[i][1],
            'burst_time': processes[i][2],
            'waiting_time': wt[i],
            'turn_around_time': tat[i]
        })
        total_wt += wt[i]
        total_tat += tat[i]

    avg_wt = total_wt / n
    avg_tat = total_tat / n

    return result, avg_wt, avg_tat

def sjf(process):
    def waitingTime(process, wt):
        n = len(process)
        wt[0] = 0
        for i in range(1, n):
            wt[i] = process[i - 1][2] + wt[i - 1]

    def turnAroundTime(process, wt, tat):
        for i in range(len(process)):
            tat[i] = process[i][2] + wt[i]

    n = len(process)
    wt = [0] * n
    tat = [0] * n
    total_wt = 0
    total_tat = 0

    waitingTime(process, wt)
    turnAroundTime(process, wt, tat)

    result = []
    for i in range(n):
        result.append({
            'name': process[i][0],
            'arrival_time': process[i][1],
            'burst_time': process[i][2],
            'waiting_time': wt[i],
            'turn_around_time': tat[i]
        })
        total_wt += wt[i]
        total_tat += tat[i]

    avg_wt = total_wt / n
    avg_tat = total_tat / n

    return result, avg_wt, avg_tat

def srtf(process):
    import sys
    def waitingTime(process, wt):
        n = len(process)
        rt = [0] * n

        for i in range(n):
            rt[i] = process[i][2]

        complete = 0
        short = 0
        current_t = 0
        min_t = sys.maxsize
        flag = False

        while complete != n:
            for i in range(n):
                if process[i][1] <= current_t and rt[i] < min_t and rt[i] > 0:
                    min_t = rt[i]
                    short = i
                    flag = True

            if not flag:
                current_t += 1
                continue

            rt[short] -= 1
            min_t = rt[short]

            if min_t == 0:
                min_t = sys.maxsize

            if rt[short] == 0:
                complete += 1
                flag = False
                final_t = current_t + 1
                wt[short] = final_t - process[short][1] - process[short][2]

                if wt[short] < 0:
                    wt[short] = 0

            current_t += 1

    def turnAroundTime(process, wt, tat):
        for i in range(len(process)):
            tat[i] = process[i][2] + wt[i]

    n = len(process)
    wt = [0] * n
    tat = [0] * n
    total_wt = 0
    total_tat = 0

    waitingTime(process, wt)
    turnAroundTime(process, wt, tat)

    result = []
    for i in range(n):
        result.append({
            'name': process[i][0],
            'arrival_time': process[i][1],
            'burst_time': process[i][2],
            'waiting_time': wt[i],
            'turn_around_time': tat[i]
        })
        total_wt += wt[i]
        total_tat += tat[i]

    avg_wt = total_wt / n
    avg_tat = total_tat / n

    return result, avg_wt, avg_tat

def run_elevator_simulation(current_floor, num_requests, requests):
    lower_floors = []
    upper_floors = []

    for request_floor in requests:
        if request_floor < current_floor:
            lower_floors.append(request_floor)
        else:
            upper_floors.append(request_floor)

    lower_floors = sorted(lower_floors, reverse=True)
    upper_floors = sorted(upper_floors)

    all_floors = lower_floors + upper_floors
    floor_labels = ['Current Floor'] + lower_floors + upper_floors
    floor_requests = [current_floor] + lower_floors + upper_floors

    last_floor = all_floors[-1] if all_floors else current_floor
    avg_position = sum(all_floors) / len(all_floors) if all_floors else current_floor

    return last_floor, avg_position, lower_floors, upper_floors, requests

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
    if np.all(available_matrix >= need[0]):
        available_matrix += allocation_matrix[0]
        is_safe = True
    else:
        is_safe = False

    return {
        'max_matrix': max_matrix.tolist(),
        'allocation_matrix': allocation_matrix.tolist(),
        'available_matrix': available_matrix.tolist(),
        'need_matrix': need.tolist(),
        'is_safe': is_safe
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
