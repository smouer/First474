from __future__ import print_function # TODO Remove because of routing_solver.py
from ortools.constraint_solver import pywrapcp # TODO Remove because of routing_solver.py
from ortools.constraint_solver import routing_enums_pb2 # TODO Remove because of routing_solver.py


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
    
    data_model['num_vehicles'] = 1
    data_model['vehicle_capacities'] = [15]

    # data_model['demands'] = [2, 3, 5]
    data_model['demands'] = [
        (2, 25200),
        (3, 26100),
        (5, 43200)
    ]

    # pickups and deliveries
    data_model['demands'] = [
        [[0, 2], 25200],
        [[0, 3], 26100],
        [[0, 5], 43200]
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
    

    # print the solution
