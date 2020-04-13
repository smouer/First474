#!/usr/bin/env python3

import sys
import urllib.request as urllib
import json
import numpy as np

def define_data():
    data = {}
    data['addresses'] = ['32+Knox+Road+Ridgecrest+NC',
                     'Pond+Road+Asheville+NC',
                     '40+Coxe+Avenue+Asheville+NC',
                     '340+Victoria+Road+Asheville+NC',
                     '24+Old+Brevard+Road+Venable+NC',
                     'Court+Plaza+Asheville+NC',
                     '3+Boston+Way+Asheville+NC',
                     '1624+Patton+Avenue+Asheville+NC',
                     '2978+US-70+Black+Mountain+NC',
                     '51+Mills+Gap+Royal+Pines+NC',
                     '1616+Patton+Avenue+Asheville+NC',
                     '86+Tunnel+Road+Asheville+NC',
                     '29+Tunnel+Road+Asheville+NC',
                     '1141+Tunnel+Road+Asheville+NC',
                     '7+McDowell+Street+Asheville+NC',
                     '39+Choctaw+Street+Asheville+NC',
                     '627+Swannanoa+River+Road+Asheville+NC',
                     '149+Old+Shoals+Road+Arden+NC',
                     '605+Sweeten+Creek+Industrial+Park+Road+Asheville+NC',
                     '140+Vista+Road+Arden+NC',
                     '900+Riverside+Drive+Asheville+NC',
                     '800+Centre+Park+Drive+Asheville+NC',
                     '141+Hillside+Street+Asheville+NC',
                     '1100+Tunnel+Road+Asheville+NC',
                     '932+Hendersonville+Road+Asheville+NC'
                     ]
    data['API_key'] = ***
    return data

def create_distance_matrix(data):
  addresses = data["addresses"]
  API_key = data["API_key"]
  # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
  max_elements = 100
  num_addresses = len(addresses) # 16 in this example.
  # Maximum number of rows that can be computed per request (6 in this example).
  max_rows = max_elements // num_addresses
  # num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
  q, r = divmod(num_addresses, max_rows)
  dest_addresses = addresses
  distance_matrix = []
  # Send q requests, returning max_rows rows per request.
  for i in range(q):
    origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
    response = send_request(origin_addresses, dest_addresses, API_key)
    distance_matrix += build_distance_matrix(response)

  # Get the remaining remaining r rows, if necessary.
  if r > 0:
    origin_addresses = addresses[q * max_rows: q * max_rows + r]
    response = send_request(origin_addresses, dest_addresses, API_key)
    distance_matrix += build_distance_matrix(response)
  return distance_matrix

def send_request(origin_addresses, dest_addresses, API_key):
  """ Build and send request for the given origin and destination addresses."""
  def build_address_str(addresses):
    # Build a pipe-separated string of addresses
    address_str = ''
    for i in range(len(addresses) - 1):
      address_str += addresses[i] + '|'
    address_str += addresses[-1]
    return address_str

  request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
  origin_address_str = build_address_str(origin_addresses)
  dest_address_str = build_address_str(dest_addresses)
  request = request + '&origins=' + origin_address_str + '&destinations=' + \
                       dest_address_str + '&key=' + API_key
  #print(request)
  jsonResult = urllib.urlopen(request).read()
  response = json.loads(jsonResult)
  #print(response)
  return response

def build_distance_matrix(response):
  distance_matrix = []
  for row in response['rows']:
    row_list = [row['elements'][j]['duration']['value']/60 for j in range(len(row['elements']))]
    distance_matrix.append(row_list)
  return distance_matrix

def main():
    data = define_data()
    matrix = create_distance_matrix(data)
    matrix = np.round(matrix,0)

    print(matrix)
    np.savetxt("time_matrix.csv",np.asarray(matrix),delimiter = ",", fmt = '%d')

if __name__ == "__main__":
    main()
