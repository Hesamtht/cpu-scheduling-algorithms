from django.shortcuts import render
from django.http import JsonResponse
from .models import Process
from .algorithms import *
import json

def index(request):
    return render(request, 'scheduler/index.html')

def round_robin(request):
    return render(request, 'scheduler/round_robin.html')

def get_processes(request):
    processes = list(Process.objects.values())
    return JsonResponse(processes, safe=False)

def add_process(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        process = Process.objects.create(
            name=data['name'],
            arrival_time=data['arrival_time'],
            burst_time=data['burst_time']
        )
        return JsonResponse({'status': 'success', 'process_id': process.id})

def delete_process(request, process_id):
    if request.method == 'DELETE':
        try:
            process = Process.objects.get(id=process_id)
            process.delete()
            return JsonResponse({'status': 'success'})
        except Process.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Process not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def schedule(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        processes = list(Process.objects.values())
        algorithm = data['algorithm']

        process_list = [[p['id'], p['arrival_time'], p['burst_time'], 0] for p in processes]  # Dummy priority 0

        if algorithm == 'FCFS':
            result, avg_wt, avg_tat = fcfs(process_list)
        elif algorithm == 'SJF':
            result, avg_wt, avg_tat = sjf(process_list)
        elif algorithm == 'SRTF':
            result, avg_wt, avg_tat = srtf(process_list)
        elif algorithm == 'MLFQ':
            mlfq_result = mlfq_algorithm(len(process_list), process_list)
            result = [{'name': p[0], 'arrival_time': 0, 'burst_time': 0, 'waiting_time': p[3], 'turn_around_time': p[2]} for p in mlfq_result]
            avg_wt = sum(p[3] for p in mlfq_result) / len(mlfq_result)
            avg_tat = sum(p[2] for p in mlfq_result) / len(mlfq_result)
        else:
            result = []
            avg_wt = 0
            avg_tat = 0

        return JsonResponse({'result': result, 'avg_wt': avg_wt, 'avg_tat': avg_tat})

def round_robin_schedule(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        processes = list(Process.objects.values())
        quantum = int(data['quantum'])

        process_list = [[p['id'], p['arrival_time'], p['burst_time'], 0] for p in processes]  # Dummy priority 0

        result, avg_wt, avg_tat = rr(process_list, quantum)

        return JsonResponse({'result': result, 'avg_wt': avg_wt, 'avg_tat': avg_tat})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def mlfq_view(request):
    return render(request, 'scheduler/mlfq.html')

def mlfq_get_processes(request):
    processes = list(Process.objects.values())
    return JsonResponse(processes, safe=False)

def mlfq_add_process(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        process = Process.objects.create(
            name=data['name'],
            arrival_time=data['arrival_time'],
            burst_time=data['burst_time'],
            priority=data['priority']
        )
        return JsonResponse({'status': 'success', 'process_id': process.id})

def mlfq_schedule(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        processes = list(Process.objects.values())
        process_list = [[p['id'], p['arrival_time'], p['burst_time'], p['priority']] for p in processes]

        mlfq_result = mlfq_algorithm(len(process_list), process_list)
        result = [{'name': p[0], 'arrival_time': 0, 'burst_time': 0, 'waiting_time': p[3], 'turn_around_time': p[2]} for p in mlfq_result]
        avg_wt = sum(p[3] for p in mlfq_result) / len(mlfq_result)
        avg_tat = sum(p[2] for p in mlfq_result) / len(mlfq_result)

        return JsonResponse({'result': result, 'avg_wt': avg_wt, 'avg_tat': avg_tat})

def elevator_view(request):
    return render(request, 'scheduler/elevator.html')

def run_elevator(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        num_floors = int(data['num_floors'])
        elevator_capacity = int(data['elevator_capacity'])
        num_requests = int(data['num_requests'])

        # Simulating requests for floors within the range of num_floors
        requests = [randint(0, num_floors - 1) for _ in range(num_requests)]

        last_floor, avg_position, lower_floors, upper_floors, all_requests = run_elevator_simulation(0, num_requests, requests)  # Starting from floor 0

        response_data = {
            'last_floor': last_floor,
            'avg_position': avg_position,
            'lower_floors': lower_floors,
            'upper_floors': upper_floors,
            'all_requests': all_requests
        }

        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def banker_view(request):
    return render(request, 'scheduler/banker.html')

def run_banker(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        max_capacity_matrix = data['max_capacity']
        allocation_matrix = data['allocation']
        available_matrix = data['available']

        result = bankers_algorithm(max_capacity_matrix, allocation_matrix, available_matrix)

        return JsonResponse(result)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def calculator(request):
    return render(request, 'scheduler/calculator.html')