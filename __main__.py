'''
    Useful links:
        https://developers.google.com/optimization/routing/dimensions
        https://developers.google.com/optimization/reference/constraint_solver/routing/RoutingModel
        https://github.com/google/or-tools/blob/stable/ortools/constraint_solver/samples/vrp_time_windows.py
        https://developers.google.com/optimization/routing/vrptw
        https://developers.google.com/optimization/routing/pickup_delivery

'''

from __future__ import print_function # TODO Remove because of routing_solver.py
from ortools.constraint_solver import routing_enums_pb2 # TODO Remove because of routing_solver.py
from ortools.constraint_solver import pywrapcp # TODO Remove because of routing_solver.py

# some globals for temporary code organization
data = None
routing_index_manager = None
routing_model = None

def get_data_model(dataFile=None):
    data_model = {}
    if dataFile is None:
        data_model['time_matrix'] = [
            #0  1   2   3   4   5
            [0, 13, 11, 15, 12, 12], # from FIRST to 1, 2, 3, 4, 5
            [13, 0, 13, 20, 16, 17], # from 1 to FIRST, , 3, 4, 5
            [11, 13, 0, 16, 14, 16], 
            [16, 19, 15, 0, 5, 12],
            [13, 17, 13, 5, 0, 11],
            [13, 18, 16, 13, 10, 0] # from 5 to FIRST, 1, 2, 3, 4
        ]

        data_model['depot'] = 0
        
        data_model['number_of_vehicles'] = 2
        data_model['vehicle_capacities'] = [15]

        # pickups and deliveries
        data_model['time_windows'] = [
            (0, 5),  # depot
            (7, 12),  # 1
            (10, 15),  # 2
            (5, 14),  # 3
            (5, 13),  # 4
            (0, 5),  # 5
        ]
    else:
        # TODO: Implement reading from file/external source
        pass

    if data_model == {}:
        return None
    else:
        return data_model

def initialize_solver(): # call this or NOTHING will worrkkkkk
    global routing_index_manager
    global routing_model
    
    routing_index_manager = pywrapcp.RoutingIndexManager(
        len(data['time_matrix']), 
        data['number_of_vehicles'], 
        data['depot']
    )
    
    routing_model = pywrapcp.RoutingModel(routing_index_manager)

def time_callback(from_index, to_index):
    '''
        - returns time to between locations and passes it to the solver
        - also sets the costs/weights of the edges which defines the cost of travel
    '''

    from_node = routing_index_manager.IndexToNode(from_index) # convert from routing variable index to time matrix index
    to_node = routing_index_manager.IndexToNode(to_index)

    return data['time_matrix'][from_node][to_node]

def add_time_window_constraints_to_solver():
    transit_callback_index = routing_model.RegisterTransitCallback(time_callback)
    routing_model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    routing_model.AddDimension(
        # TODO: Make these args to function later.... maybe
        transit_callback_index,
        15, # waiting time
        60, # maximum time per vehicle
        False, # don't force star tht cumul to zero. Some vehicles may have to start after time 0 due to time constraint windows
        'Time'
    )

    time_dimension = routing_model.GetDimensionOrDie('Time')

    # Q: What is this cumuluzative variable that keeps on being referenced and talked about?
    # A: Well well well, the dimension computes thhe cumulative of something (time, distance) traveled by
    #   each vehicle along a route.
    # ... Then you can set a cost that is proportional to the maximum of the total something along each route...

    # Add time window constraints for each location except depot.
    for location_id, time_window in enumerate(data['time_windows']): # enumerate time windows then split apart
        if location_id == 0:
            continue

        index = routing_index_manager.NodeToIndex(location_id)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data['number_of_vehicles']):
        index = routing_model.Start(vehicle_id)
        
        time_dimension.CumulVar(index).SetRange(data['time_windows'][0][0], data['time_windows'][0][1])

    for i in range(data['number_of_vehicles']):
        routing_model.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing_model.Start(i)))
        routing_model.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing_model.End(i)))

    
if __name__ == '__main__':    
    data = get_data_model()
    initialize_solver()
    add_time_window_constraints_to_solver()

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    assignment = routing_model.SolveWithParameters(search_parameters)
 
    # print the solution