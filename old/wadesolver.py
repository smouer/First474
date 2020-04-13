#!/usr/bin/env python3

import ortools.constraint_solver
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel

def create_data_model():
    data = {}

    data['time_matrix'] = [
        [0,3,7,9],
        [3,0,6,8],
        [7,6,0,4],
        [9,8,4,0]
        ]

    data['pickups_deliveries']=[
        [0,2],
        #[0,3],
        #[1,0],
        #[3,0]
        ]

    data['time_windows'] = [
        (0,500),
        #(10,100),
        #(5,500),
        #(5,500)
        ]

    assert(len(data['time_windows']) == len(data['pickups_deliveries']))
    
    data['demands'] = {}

    for i in range(len(data['time_windows'])):
        if data['pickups_deliveries'][i][0] == 0:
            data['demands'][i] = -1
        else:
            data['demands'][i] = 1

    data['num_vehicles'] = 1
    data['depot'] = 0
    data['capacities'] = [6]

    return data

def print_solution(data, manager, routing, assignment):
    """Prints assignment on console."""
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_load = 0
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            #route_load += data['demands'][manager.IndexToNode(index)]
            plan_output += '{0} Time({1},{2}) Load({3})-> '.format(
                manager.IndexToNode(index), assignment.Min(time_var),
                assignment.Max(time_var), route_load)
            index = assignment.Value(routing.NextVar(index))
        time_var = time_dimension.CumulVar(index)
        plan_output += '{0} Time({1},{2})\n'.format(
            manager.IndexToNode(index), assignment.Min(time_var),
            assignment.Max(time_var))
        plan_output += 'Time of the route: {}min\n'.format(
            assignment.Min(time_var))
        print(plan_output)
        total_time += assignment.Min(time_var)
    print('Total time of all routes: {}min'.format(total_time))


def main():
    print("Lets debug!!")
    data = create_data_model()
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
        1000,
        5000,
        False,
        time)
    time_dimension = routing.GetDimensionOrDie(time)

    def demand_callback(node):
        return(data['demands'][node])

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        slack_max=0,  # null slack
        # vehicle maximum capacities
        vehicle_capacities=data['capacities'],
        fix_start_cumul_to_zero=False,  # start cumul to zero
        name='Capacity',
    )

    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    for pd, tw in zip(data['pickups_deliveries'], data["time_windows"]):
        pickup, dropoff = pd
        routing.AddPickupAndDelivery(pickup, dropoff)
        routing.solver().Add(routing.VehicleVar(pickup) == routing.VehicleVar(dropoff))

        time_dimension.CumulVar(dropoff).SetRange(tw[0],
                                                  tw[1])

    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    assignment = routing.SolveWithParameters(search_parameters)
    if assignment:
        print_solution(data, manager, routing, assignment)

    print("solver status: ", routing.status())
    #0: not solved yet
    #1: success
    #2: no solution
    #3: solver timed out
    #4: routing invalid

if __name__ == "__main__":
    main()
