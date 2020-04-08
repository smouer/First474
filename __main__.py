from __future__ import print_function
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from collections import namedtuple
from enum import Enum, auto
import numpy as np
import random
import time

# VanRequest = namedtuple('VanRequest', ['client', 'is_dropoff', 'location', 'time'])
VanRequest = namedtuple('VanRequest', ['is_dropoff', 'place', 'time'])
Van = namedtuple('Van', ['id', 'is_operational', 'capacity'])

class SolverDataModel(object):

    def __init__(self, travel_times, depot, client_requests):
        self._travel_times = travel_times
        self._depot = depot

        # initialize the time matrix mechanism
        self._time_matrix_index_to_place = {0: self._depot} # node 0 is always depot
        m = len(client_requests) + 1 # +1 for depot.
        self._time_matrix = []
        for _ in range(m): # m x m matrix filled with Nones
            self._time_matrix.append([None] * m)

        for i in range(len(client_requests)):
            self._time_matrix_index_to_place[i + 1] = client_requests[i].place

        for row, fp in self._time_matrix_index_to_place.items():
            for col, tp in self._time_matrix_index_to_place.items():
                time_between_places = self._travel_times[fp][tp]
                self._time_matrix[row][col] = time_between_places

        self._time_windows = []
        for request in client_requests:
            h, m, s = request.time.split(':')
            time_in_seconds = int(h) * 3600 + int(m) * 60 + int(s)
            
            if request.is_dropoff:
                left_window = time_in_seconds - (15 * 60) # minutes in seconds
                right_window = time_in_seconds
            else:
                left_window = time_in_seconds
                right_window = time_in_seconds + (5 * 60) # TODO: Play with
            
            self._time_windows.append((left_window, right_window))
    
    @property
    def time_matrix(self):
        return self._time_matrix
    
    @property
    def index_of_depot(self):
        return 0
    
    @property
    def time_windows(self):
        return self._time_windows

if __name__ == '__main__':
    sample_travel_times = {
        'P_A': {'P_A': 0, 'P_B': 13, 'P_C': 11, 'P_D': 15},
        'P_B': {'P_A': 13, 'P_B': 0, 'P_C': 13, 'P_D': 20},
        'P_C': {'P_A': 11, 'P_B': 13, 'P_C': 0, 'P_D': 16},
        'P_D': {'P_A': 16, 'P_B': 19, 'P_C': 15, 'P_D': 0},
    }

    sample_depot = 'P_A'

    sample_client_requests = []
    for _ in range(random.randint(10, 50)):
        is_dropoff = random.choice([True, False])
        place = random.choice([p for p, _ in sample_travel_times.items()])
        rendezvous_time = random.choice(['06:00:00', '07:00:00', '08:00:00', 
            '09:00:00', '10:00:00', '11:00:00', '12:00:00', '13:00:00', 
            '14:00:00', '15:00:00', '16:00:00', '17:00:00', '18:00:00', 
            '19:00:00', '20:00:00'])
        
        sample_client_requests.append(VanRequest(is_dropoff, place, rendezvous_time))

    dm = SolverDataModel(sample_travel_times, sample_depot, sample_client_requests)
    print(*dm.time_windows, sep='\n')
    print(*dm.time_matrix, sep='\n')