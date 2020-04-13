#!/usr/bin/env python3

import ortools.constraint_solver
import numpy as np
from collections import namedtuple
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

def read_matrix():
    matrix = np.loadtxt(open('time_matrix.csv'), int, delimiter = ',' )
    #print(matrix)
    return matrix

def generate_data(matrix):
    request = namedtuple("request", ['node', 'time', 'is_dropoff'])

    Depot = request(0,0,False)
    request_list = [Depot, request(3,60,True), request(4,60,True), request(7,90,True), request(3, 120, False) ]
    length = len(request_list)
    
    node_matrix = np.zeros((length,length))

    for i in range(length):
        for j in range(length):
            node_matrix[i][j] = matrix[request_list[i].node][request_list[j].node]


    tw = []
    for rq in request_list:
        if rq.is_dropoff:
            tw.append((rq.time - 30, rq.time))
        else: tw.append((rq.time, rq.time+30))


    data = {}
    data['time_matrix'] = node_matrix
    data['time_windows'] = tw
    data['depot'] = 0
    data['num_vehicles'] = 1
    
    return data



def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print("hello, hello")
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

def run():
    print("Lets debug!!")
    matrix = read_matrix()
    data = generate_data(matrix)
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
        30,
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

def main():
    #matrix = read_matrix()
    #generate_request(matrix)
    run()


if __name__ == '__main__':
    main()
