import json
import networkx
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # load the data needed for the graph into memory    
    with open('../data/places_network.json', 'r') as places_network_file:
        places = json.load(places_network_file)
    
    # create the netowrkx graph then add al the nodes to it.
    places_graph = networkx.DiGraph()
    
    for p in places:
        places_graph.add_node(p['name'])
    
    # insert the edges
    for p in places:
        for edge in p['driveDurations']:
            places_graph.add_weighted_edges_from([(p['name'], edge['destinationName'], edge['duration'])])
#             places_graph.add_edges_from((p['name'], edge['destinationName'], )
#             places_graph.add_edge(p['name'], edge['destinationName'])
    
    # visualize the graph
    plt.subplot(121)
    networkx.draw(places_graph, with_labels=True, font_weight='bold')
#     plt.subplot(122)
#     networkx.draw_shell(places_graph, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
    plt.show()