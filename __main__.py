'''
        
'''

def create_data_model(dataFile=None):
    data = {}
    if dataFile is None:
        data['time_matrix'] = [
            [0, 13, 11, 15, 12, 12], # from FIRST to 1, 2, 3, 4, 5
            [13, 0, 13, 20, 16, 17], # from 1 to FIRST, , 3, 4, 5
            [11, 13, 0, 16, 14, 16], 
            [16, 19, 15, 0, 5, 12],
            [13, 17, 13, 5, 0, 11],
            [13, 18, 16, 13, 10, 0] # from 5 to FIRST, 1, 2, 3, 4
        ]

        data['pickups_deliveries'] = [
            [0, 1], # so someone needs to go from FIRST to 1
            [0, 2],
            [0, 4],
            # there should NEVER be a dropoff without an associated pickup
            [1, 0],
            [2, 0],
            [4, 0],
            # but there could be a pickup up without an associated dropoff (for the day)
            # [3, 0] # might want to comment out
        ]

        # time windows are based on minutes from midnight [0-1440)
        # all time windows are associated w/ an the same index in pickup_deliveries array
        data['time_windows'] = [
            (465, 465),
            (465, 465),
            (465, 465),
            (900, 900),
            (900, 900),
            (915, 915) 
        ]

        data['starts'] = [0]
        data['ends'] = [3]
        data['num_of_vehicles'] = 1

    else:
        # TODO: Implement reading from file/external source
        pass
    
    return data



if __name__ == '__main__':

    time_matrix = [
        [0, 13, 11, 15, 12, 12],
        [13, 0, 13, 20, 16, 17],
        [11, 13, 0, 16, 14, 16],
        [16, 19, 15, 0, 5, 12],
        [13, 17, 13, 5, 0, 11],
        [13, 18, 16, 13, 10, 0]
    ]

    time_windows = [
        (21600, 55),
        (95, 115),
        (95, 115),
        (95, 115),
        (155, 175)
    ]

    number_of_locations = len(time_matrix)
    van_capacities = [15]
    number_of_vans = len(van_capacities)    
    depot = 0

    routing_index_manager = pywrapcp.RoutingIndexManager(6, 2, 0) # Create the routing index manager.
    routing_model = pywrapcp.RoutingModel(routing_index_manager)
    
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return 1
    