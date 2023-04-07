import gmplot
import re
import json
from utils import *
import os
import time
import logging

dirs = ['NE','NW','SW','SE']
NE = dict()
gmap = gmplot.GoogleMapPlotter(40.5, -73.97, 10)
def dms_to_decimal(dms):
    coords = re.split('/',dms)
    ret = []
    for cd in coords:
        parity = -1 if 'W' in cd  else 1
        parts = ( re.split('[^\d.]+', cd) )
        new_list = [s for s in parts if s]

        degrees, minutes, seconds = [float(x) for x in new_list]

        decimal = degrees + (minutes / 60) + (seconds / 3600)
        ret.append(decimal*parity)
    return ret

def map_coords(filename,gmap):
    logging.error(f'Started processing file: {filename}')
    data = {}
    # Open the JSON file
    with open(filename, 'r') as f:
        # Load the data from the file into a dictionary
        data = json.load(f)
    
    # Access the data in the dictionary
    for d in data:
        if('coords' in d) and len(d['coords']) != 0:
            rect_coords = []
            print(data)
            marker_text = d['block'] 
            for x in dirs :
                rect_coords.append(dms_to_decimal(d['coords'][x]))
            marker_lats, marker_lons = zip(*rect_coords)
            rect_coords.append(dms_to_decimal(d['coords']['NE']))
            if(d['coords']['NE'] not in NE):
                NE[d['coords']['NE']] = 0
            NE[d['coords']['NE']] = NE[d['coords']['NE']]+1
            print(rect_coords)
            print("\n")
            lats, lons = zip(*rect_coords)
            gmap.plot(lats, lons, 'cornflowerblue', edge_width=3)
            for lat, lon in zip(marker_lats, marker_lons):
                gmap.marker(lat, lon, title=d['names'][0])
            # label = d['names'][0]
            # lat_center = sum(lats) / len(lats)
            # lon_center = sum(lons) / len(lons)
            # gmap.text(lat_center, lon_center, label)

def main():
    if not os.path.exists(MAPS_DIRECTORY):
        os.makedirs(MAPS_DIRECTORY)
    start_time = time.time()

    files_list = get_files(JSON_DIRECTORY,'json')
    gmap = gmplot.GoogleMapPlotter(40.5, -73.97, 10)
    for jsonfile in files_list:
       print("hi")
       map_coords(jsonfile,gmap)

    gmap.draw("map1.html")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
    print(NE)

if __name__ == '__main__':
    main()