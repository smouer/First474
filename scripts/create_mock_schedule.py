from create_mock_people import create_a_set_of_people
import json
import time
from enum import Enum
import random
from datetime import datetime


class RequestType(Enum):
    DELIVERY = 1
    PICKUP = 2


def create_a_random_transporation_schedule():
    people = create_a_set_of_people(10)

    # assign some locations as places of work and others as med offices. Not
    # an accurate depication of FIRSt's real graph but eh.
    with open('data/places_network.json', 'r') as file:
        places_json = json.load(file)

    places = []
    for place in places_json:
        places.append(place['name'])

    transporation_schedule = []
    for person in people:
        if random.randint(1, 100) <= 75: # person has to go somewhere today
            possible_event_start_times = []
            temp = 21600
            while temp <= 64800:
                possible_event_start_times.append(temp)
                temp = temp + 900

            event_start_time = random.sample(possible_event_start_times, 1)

            possible_event_durations = [600]
            temp = 900
            while temp <= 36000:
                # if you want some times to be more likely than othere
                # i.e. there will be far more events that are between 6-9 hours
                # and 1 hour long than any other time (I think?.?...) then
                # you could use a series of if statements to determine 
                # ranged of durations that maybe multiple of the same times 
                # are inserted into the same list.

                possible_event_durations.append(temp)
                temp = temp + 900

            event_duration = random.sample(possible_event_durations, 1)  
            event_end_time = event_start_time + event_duration
            
            event_location = None
            while event_location is None:
                event_location = random.sample(places, 1)
                if event_location == 'FIRST':
                    event_location = None

            persons_transporation_request = {}
            persons_transporation_request['requester'] = person
            persons_transporation_request['dropoffPlace'] = event_location
            # hours, seconds = divmod(event_start_time, 3600)
            # minutes, _ = divmod(seconds, 60)
            persons_transporation_request['dropoffTime'] = event_start_time
            persons_transporation_request['pickupTime'] = event_end_time

            transporation_schedule.append(persons_transporation_request)

    return transporation_schedule
                

if __name__ == '__main__':
    schedule = create_a_random_transporation_schedule()
    with open('data/mock_schedule.json', 'w') as file:
        json.dump(schedule, file)