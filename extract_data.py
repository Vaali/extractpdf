from lxml import html
import re
from utils import *
import os
import time
import json
import multiprocessing
import re

def extract_dates(data):
    #print(data)
    pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(st|nd|rd|th)?,\s+(\d{4})"
    matches = re.findall(pattern, data)
    for match in matches:
        print(match)
    return matches

def extract_coords(data):
    #pattern = r"\d{1,2}°\s\d{1,2}'\s\d{1,2}\"[NS]\s/\s\d{1,3}°\s\d{1,2}'\s\d{1,2}\"[EW]"
    #pattern = r"\d{2}°\s\d{2}[’']\s\d{2}[\"]\w\s/\s\d{2}°\s\d{2}[’']\s\d{2}[\"]\w"
    pattern = r"\d{1,2}°\s\d{1,2}[’']\s\d{1,2}[”\"]?[NS]\s\/\s\d{1,3}°\s\d{1,2}[’']\s\d{1,2}[”\"]?[EW]"
    pattern = r"\d{1,2}°\s\d{1,2}[’']?\s\d{1,2}[”\"]?[NS][\s,][\/]?\s\d{1,3}°\s\d{1,2}[’']?\s\d{1,2}[”\"]?[EW]"

    matches = re.findall(pattern, data)
    print(matches)
    return matches

def extract_name(data):
    vessels_keyword = "call sign"
    delimiters = ",("
    regexPattern = '|'.join(map(re.escape, delimiters))
    names = []
    currdata = data.lower()
    currdata = currdata.replace("****extended****",'')
    # if( vessels_keyword not in currdata ):
    #     line = currdata.split("\n")[1]
    #     names.append(re.split(regexPattern, line)[0])
    #     if("vessel" in currdata):
    #         print("----------",currdata.split("vessel"))
    while( vessels_keyword in currdata ):
        before_word, after_word = currdata.split(vessels_keyword, 1)
        # for ves in vessels:
        lines = before_word.split("\n")
        if(len(lines)>1):
            if('vessel' in lines[1]):
                before_word1,lines[1] = lines[1].split("vessel")
            names.append(re.split(regexPattern, lines[1])[0])
        if(len(lines) == 1):
            before_word1, after_word1 = lines[0].split("and ", 1)
            names.append(re.split(regexPattern, after_word1)[0])
        currdata = after_word
    names = [x.strip() for x in names if x.strip()]
    print(names)
    return names

def can_we_skip(text):
    words = ["AUTONOMOUS","DREDGING", "NOURISHMENT", "FIREWORKS", "ORDNANCE", "ENDANGERED" ]
    pattern = "|".join(words)
    matches = re.findall(pattern, text, re.IGNORECASE)
    return(matches)
    # if(len(matches) == 0):
    #     return False
    # else:
    #     return True

def extract_blocks_old(htmlfile):
    # Load the HTML file into a tree object
    data = list()
    with open(htmlfile, 'r') as f:
        tree = html.fromstring(f.read())

    # Use XPath to get a list of elements
    elements = tree.xpath('//div[not(parent::div)]')
    #/html/body/span[88]/div[31]/span
    #/html/body/span[82]/div[28]/span
    pattern = r'OFFSHORE SURVEY'
    pattern_new = r'SEACOAST'
    matches = []
    for element in elements:
        print(element.text_content())
        match = re.search(pattern_new, element.text_content(), re.IGNORECASE)

        if( match and not can_we_skip(element.text_content()) ):
            matches.append(element.text_content())
    for block in matches:
        curr_data = dict()
        #curr_data['dates']=extract_dates(block)
        #curr_data['coords']=extract_coords(block)
        curr_data['names']=extract_name(block)
        for n in curr_data['names']:
            if( n != "" ):
                shared_list.append(n)
        curr_data['block'] = block
        data.append(curr_data)
    print(len(matches) )
    filename = os.path.splitext(os.path.basename(htmlfile))[0]
    logging.error(f'Started processing file: {filename}')
    jsonfilepath = JSON_DIRECTORY+'/'+filename+'.json'
    
    with open(jsonfilepath, 'w') as f:
        json.dump(data, f)
    
def extract_blocks(htmlfile):
    # Load the HTML file into a tree object
    data = list()
    with open(htmlfile, 'r') as f:
        tree = html.fromstring(f.read())

    # Use XPath to get a list of elements
    elements = tree.xpath('//div[not(parent::div)]')
    #/html/body/span[88]/div[31]/span
    #/html/body/span[82]/div[28]/span
    pattern = r'OFFSHORE SURVEY'
    pattern_new = r'SEACOAST'
    matches = []
    filename = os.path.splitext(os.path.basename(htmlfile))[0]
    shared_data = {}
    shared_data[filename] = list()
    for element in elements:
        #print(element.text_content())
        match = re.search(pattern_new, element.text_content(), re.IGNORECASE)
        if( match and not can_we_skip(element.text_content()) ):
            matches.append(element.text_content())
    for block in matches:
        curr_data = dict()
        #curr_data['dates']=extract_dates(block)
        #curr_data['coords']=extract_coords(block)
        curr_data['names']=extract_name(block)
        print( curr_data['names'])
        for n in curr_data['names']:
            if( n != ""):
                shared_data[filename].append(n)
        curr_data['block'] = block
        data.append(curr_data)
    print(len(matches) )
    return shared_data
    # filename = os.path.splitext(os.path.basename(htmlfile))[0]
    # logging.error(f'Started processing file: {filename}')
    # jsonfilepath = JSON_DIRECTORY+'/'+filename+'.json'
    
    # with open(jsonfilepath, 'w') as f:
    #     json.dump(data, f)
    
def main():
    if not os.path.exists(JSON_DIRECTORY):
        os.makedirs(JSON_DIRECTORY)
    
    files_list = get_files(HTML_DIRECTORY,'html')
    #files_list = ['html/lnm05522022.html']
    start_time = time.time()
    #for htmlfile in files_list:
    #    extract_blocks(htmlfile)
    # Create a process pool with 4 workers
    with multiprocessing.Manager() as manager:
        shared_data = manager.dict()
        #pool = multiprocessing.Pool(processes=4)
        with multiprocessing.Pool(processes=4) as pool:
            # pool.starmap(extract_blocks, [(shared_data, i) for i in files_list])
            results = pool.map(extract_blocks, files_list)
            # Convert all PDF files to HTML in parallel
            # pool.map(extract_blocks, files_list)
            # Close the pool and wait for the work to finish
            pool.close()
            pool.join()
        print((results))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")


if __name__ == '__main__':
    main()
