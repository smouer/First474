from __future__ import print_function # TODO Remove because of routing_solver.py
from ortools.constraint_solver import routing_enums_pb2 # TODO Remove because of routing_solver.py
from ortools.constraint_solver import pywrapcp # TODO Remove because of routing_solver.py


def get_default_data_model():
    data_model = {}

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
    data_model['demands'] = [
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (5, 14),  # 3
        (5, 13),  # 4
        (0, 5),  # 5
    ]

    return data_model

def get_data_model(dataFile=None):
    if dataFile is None:
        return get_default_data_model()
    else:
        data_model = {}

        # TODO: Implement reading from file/external source

        return data_model

    return None


if __name__ == '__main__':    
    # TODO Remove this eventually
    routing_index_manager = pywrapcp.RoutingIndexManager(6, 2, 0) # Create the routing index manager.
    routing_model = pywrapcp.RoutingModel(routing_index_manager)
    data_model = get_data_model()

    def time_callback(from_index, to_index):
        '''
            - returns time to between locations and passes it to the solver
            - also sets the costs/weights of the edges which defines the cost of travel
        '''

        from_node = routing_index_manager.IndexToNode(from_index) # convert from routing variable index to time matrix index
        to_node = routing_index_manager.IndexToNode(to_index)

        return data_model['time_matrix'][from_node][to_node]
    
    transit_callback_index = routing_model.RegisterTransitCallback(time_callback)
    routing_model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    routing_model.AddDimension(
        transit_callback_index,
        15, # waiting time
        60, # maximum time per vehicle
        False,
        'Time'
    )

    time_dimension = routing_model.GetDimensionOrDie('Time')

    # Add time window constraints for each location except depot.
    for location_id, time_window in enumerate(data_model['demands']):
        if location_id == 0:
            continue

        index = routing_index_manager.NodeToIndex(location_id)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data_model['number_of_vehicles']):
        index = routing_model.Start(vehicle_id)
        
        time_dimension.CumulVar(index).SetRange(data_model['demands'][0][0], data_model['demands'][0][1])

    for i in range(data_model['number_of_vehicles']):
        routing_model.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing_model.Start(i)))
        routing_model.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing_model.End(i)))
            

    
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    assignment = routing_model.SolveWithParameters(search_parameters)
    # print the solution
