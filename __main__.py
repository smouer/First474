import networkx
from ortools.linear_solver import pywraplp
import tkinter
# import matplotlib.pyplot as plt



if __name__ == '__main__':
    # always begin by loading the data
    time_matrix = [
        [0, 1663, 1510, 1385, 1666, 1451],
        [1164, 0, 741, 773, 447, 798],
        [1564, 777, 0, 307, 780, 138],
        [1457, 775, 299, 0, 778, 331],
        [1659, 448, 738, 770, 0, 796],
        [1492, 866, 169, 349, 869, 0]
    ]

    schedule = [

    ]