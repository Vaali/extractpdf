from lxml import html
import re
from utils import *
import os
import time
import json
import multiprocessing

def extract_dates(data):
    #print(data)
    pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(st|nd|rd|th)?,\s+(\d{4})"
    matches = re.findall(pattern, data)
    for match in matches:
        print(match)
    return matches

def extract_coords(data):
    coord = dict()
    for line in data.split("\n"):
        pattern = r"NW extent:"
        match = re.search(pattern, line,re.IGNORECASE)
        if match:
            print(line[match.end():])
            coord['NW'] = line[match.end():]
        pattern = r"NE extent:"
        match = re.search(pattern, line,re.IGNORECASE)
        if match:
            print(line[match.end():])
            coord['NE'] = line[match.end():]
        pattern = r"SW extent:"
        match = re.search(pattern, line,re.IGNORECASE)
        if match:
            print(line[match.end():])
            coord['SW'] = line[match.end():]
        pattern = r"SE extent:"
        match = re.search(pattern, line,re.IGNORECASE)
        if match:
            print(line[match.end():])
            coord['SE'] = line[match.end():]
    return coord

def extract_name(data):
    #print(data)
    names = data.split("\n")[1].split(",")[0:2]
    print(names)
    return names


def extract_blocks(htmlfile):
    # Load the HTML file into a tree object
    data = list()
    with open(htmlfile, 'r') as f:
        tree = html.fromstring(f.read())

    # Use XPath to get a list of elements
    elements = tree.xpath('//div[not(parent::div)]')
    pattern = r'OFFSHORE SURVEY'
    matches = []
    for element in elements:
        match = re.search(pattern, element.text_content(), re.IGNORECASE)

        if(match):
            matches.append(element.text_content())
    for block in matches:
        curr_data = dict()
        curr_data['dates']=extract_dates(block)
        curr_data['coords']=extract_coords(block)
        curr_data['names']=extract_name(block)
        curr_data['block'] = block
        data.append(curr_data)
    print(len(matches) )
    filename = os.path.splitext(os.path.basename(htmlfile))[0]
    logging.error(f'Started processing file: {filename}')
    jsonfilepath = JSON_DIRECTORY+'/'+filename+'.json'
    
    with open(jsonfilepath, 'w') as f:
        json.dump(data, f)
    

def main():
    if not os.path.exists(JSON_DIRECTORY):
        os.makedirs(JSON_DIRECTORY)
    
    files_list = get_files(HTML_DIRECTORY,'html')
    start_time = time.time()
    #for htmlfile in files_list:
    #    extract_blocks(htmlfile)
    # Create a process pool with 4 workers
    pool = multiprocessing.Pool(processes=4)

    # Convert all PDF files to HTML in parallel
    pool.map(extract_blocks, files_list)

    # Close the pool and wait for the work to finish
    pool.close()
    pool.join()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")


if __name__ == '__main__':
    main()
