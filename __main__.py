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
    
    def demand_callback(from_index):
        from_node = routing_index_manager.IndexToNode(from_index)
        
        return data_model['demands'][from_node]
    
    transit_callback_index = routing_model.RegisterTransitCallback(time_callback)
    routing_model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    allowed_waiting_time = 10 # aka the 'slack' we give the solver
    total_route_time_upper_bound = 30

    '''
        Quantities at a node are represented by "cumul" variables and the increase or decrease of quantities
        between nodes are represented by "transit" variables.
        https://developers.google.com/optimization/reference/constraint_solver/routing/RoutingDimension
    '''
    force_start_cumul_to_zero = True

    routing_model.AddDimensionWithVehicleCapacity(
        transit_callback_index,
        allowed_waiting_time,
        total_route_time_upper_bound,
        force_start_cumul_to_zero,
        'Time'
    )


    demand_callback_index = routing_model.RegisterUnaryTransitCallback(demand_callback)

    # dimensions represent quantiies that accumulate at nodes along routes. Ex: weight of routes like times or distance
    routing_model.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0, # TODO: this means null capacity slack, but what does that mean?
        data_model['vehicle_capacities'],
        True, # starts the accumulation at zero (I think)
        'Capacity'
    )

    # Apparnetly this allows the dropping of nodes... which means that if the problem can't be solved with
    # all nodesbeing visted the algorithm can starting getting rid of nodes.
    penalty = 1000 # higher value means worse for the algorithm to drop a node, which is probably good for us cause we want all nodes to be visted always.
    for node in range(1, len(data_model['time_matrix'])):
        # a disjunction is simply a variable that the solver uses to decide whether to include a given location in the solution.
        routing_model.AddDisjunction([routing_index_manager.NodeToIndex(node)], penalty)
    
    # need to have dimension for tracking the total waiting for pickup-up time. Enforce the constraint of the waiting for
    # a van time.
    def total_time_waiting_callback(from_index):
        return None

    routing_model.AddDimension(
        
    )


    # define pickup and delivery requests
    for demand in data_model['demands']:
        pickup_index = routing_index_manager.NodeToIndex(demand[0][0])
        delivery_index = routing_index_manager.NodeToIndex(demand[0][1])
        routing_model.AddPickupAndDelivery(pickup_index, delivery_index)

        # adds the constraint that every pickup and delivery request has to be servided by the same vehicle 
        routing_model.solver().Add(
            routing_model.VehicleVar(pickup_index) == routing_model.VehicleVar(delivery_index)
        )

        # item has to be picked up before it can be dropped off 
        routing_model.solver().Add(
            Time.CumulVar(pickup_index) <= Time.CumulVar(delivery_index)
        )

    # print the solution
