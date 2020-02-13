import json

if __name__ == '__main__':
    # load the data  
    with open('data/places_network.json', 'r') as places_network_file:
        places = json.load(places_network_file)