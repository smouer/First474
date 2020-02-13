import json
import random

def create_a_set_of_people(num_of_people):
    with open('data/common_first_names.txt', 'r') as file:
        first_names = file.readlines()
    
    possible_first_names = []
    for name in first_names:
        no_newline_name = name.replace('\n', '')
        possible_first_names.append(no_newline_name.upper())
    del first_names
    
    with open('data/common_last_names.txt', 'r') as file:
        last_names = file.readlines()
    
    possible_last_names = []
    for name in last_names:
        no_newline_name = name.replace('\n', '')
        possible_last_names.append(no_newline_name.upper())
        
    del last_names

    people = []
    for _ in range(num_of_people):
        new_person = {}
        new_person['firstName'] = random.choice(possible_first_names)
        new_person['lastName'] = random.choice(possible_first_names)
        people.append(new_person)
        
    return people

if __name__ == '__main__':
    with open('data/mock_persons.json', 'w') as file:
        json.dump(create_a_set_of_people(10), file)