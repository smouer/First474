#!/usr/bin/env python3

import ortools.constraint_solver
import numpy as np
from collections import namedtuple
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

request = namedtuple("request", ['node', 'time', 'is_dropoff'])


def read_matrix():
    matrix = np.loadtxt(open('time_matrix.csv'), int, delimiter = ',' )
    #print(matrix)
    return matrix

def get_request_list():
    Depot = request(0,0,False)
    request_list = [Depot, request(3,60,True), request(4,60,True), request(7,90,True), request(3, 90, False), request(7,160,True) ]
    return request_list


def generate_data(matrix, request_list):
    length = len(request_list)
    
    node_matrix = np.zeros((length,length))

    for i in range(length):
        for j in range(length):
            node_matrix[i][j] = matrix[request_list[i].node][request_list[j].node]


    tw = []
    for rq in request_list:
        if rq.node == 0:
            tw.append((rq.time, rq.time + 240))
        elif rq.is_dropoff:
            tw.append((rq.time - 20, rq.time)) #dropoffs occur within 20 minutes before scheduled time
        else: tw.append((rq.time, rq.time+20)) #pickups occur within 20 minutes after

    data = {}
    data['time_matrix'] = node_matrix
    data['time_windows'] = tw
    data['depot'] = 0
    data['num_vehicles'] = 2
    
    return data



def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            plan_output += '{0} Time({1},{2}) -> '.format(
                manager.IndexToNode(index), solution.Min(time_var),
                solution.Max(time_var))
            index = solution.Value(routing.NextVar(index))
        time_var = time_dimension.CumulVar(index)
        plan_output += '{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                    solution.Min(time_var),
                                                    solution.Max(time_var))
        plan_output += 'Time of the route: {}min\n'.format(
            solution.Min(time_var))
        print(plan_output)
        total_time += solution.Min(time_var)
    print('Total time of all routes: {}min'.format(total_time))

def run(slack, request_list):
    matrix = read_matrix()
    data = generate_data(matrix,request_list)
    manager = RoutingIndexManager(len(data['time_matrix']), data['num_vehicles'], data['depot'])
    routing = RoutingModel(manager)

    #print(data)

    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    time = 'Time'

    #add time dimension
    routing.AddDimension(
        transit_callback_index,
        slack,
        240,
        False,
        time)
    time_dimension = routing.GetDimensionOrDie(time)
    
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data['time_windows'][0][0],
                                                data['time_windows'][0][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    
    print("Status: ", routing.status())
    #0: not solved yet
    #1: success
    #2: no solution
    #3: solver timed out
    #4: routing parameters invalid
    return(routing.status())

def run_block(r_l, start, stop):
        print("\n \n Time Block Start Time: ", start)
        slack = 0
        status = run(slack,r_l)
        while status != 1 and slack < 30:
            slack += 5
            status = run(slack, r_l)
        if status != 1:
            print("No optimal schedule found under these conditions.")
        else: print(slack)
        print("Time Block Stop Time: ", stop)

def run_with_blocks():

    def newList(start, list):
        new_list = []
        new_list.append(request(0,start,False))
        for rq in list:
            new_list.append(rq)
        return new_list

    print("Running with 60 minute time blocks.")
    block = 60

    
    r_l = get_request_list()
    num_blocks = r_l[-1].time // block + 1
    start = 0
    stop = block
    n = 0
    m = 0
    for i in range(num_blocks):
        while m < len(r_l) and r_l[m].time <= stop :
            m+= 1
        list = r_l[n:m]
        list = newList(start, list)
        print(list)
        n = m
        run_block(list, start, stop)
        start = start + block
        stop = stop + block


def run_without_blocks():
    r_l = get_request_list()
    print(r_l)
    slack = 0
    status = run(slack,r_l)
    while status != 1 & slack < 30:
        slack += 5
        status = run(slack, r_l)
    if status != 1:
        print("No optimal schedule found under these conditions.")
    else: print(slack)

def main():
    
    #run_without_blocks()
    
    run_with_blocks()
    

if __name__ == '__main__':
    main()
