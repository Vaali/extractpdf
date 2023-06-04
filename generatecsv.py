import os
import time
import json
import re
from PyPDF2 import PdfReader
from utils import *
import csv
vessels = {
"Go Explorer":"https://media.fugro.com/media/docs/default-source/about-fugro-doc/vessels/fugro-explorer_a4.pdf?sfvrsn=26cc091a_14",
"GO Discovery":"",
"GO  Discovery":"",
"GO Pursuit":"",
"Go P ursuit":"",
"M/V Fugro Enterprise":"",
"HOS Browning":"",
"RV Emma McCall":"",
"RV Brooks McCall":"",
"L/B Voyager":"",
#"Interceptor",
"NORTHSTAR VOYAGER":"",
"NORTHSTAR INTERCEPTOR":"",
"R/V Rachel K Goodwin":"",
"CANDU":"",
"RAIDER":"",
"SMOKEY":"",
"ANTHONY MILLER":"",
"M/V WINDSERVE ODYSSEY":"",
"James K Goodwin":"",
"M/V Atlantic Endeavor":"",
"WESTERLY":"",
"OCEAN CITY GIRL":"",
"YETI":"",
"ALMAR":"",
"WAM-V":"",
"PSV REGULUS":"",
"FUGRO BRASILIS":"",
"Aries Ram VII":"",
"Seaward 20":"",
"PSV HOS Mystique":"",
"R/V Shearwater":""
}
def extract_coords(data):
    #pattern = r"\d{1,2}°\s\d{1,2}'\s\d{1,2}\"[NS]\s/\s\d{1,3}°\s\d{1,2}'\s\d{1,2}\"[EW]"
    #pattern = r"\d{2}°\s\d{2}[’']\s\d{2}[\"]\w\s/\s\d{2}°\s\d{2}[’']\s\d{2}[\"]\w"
    pattern = r"\d{1,2}°\s\d{1,2}[’']\s\d{1,2}[”\"]?[NS]\s\/\s\d{1,3}°\s\d{1,2}[’']\s\d{1,2}[”\"]?[EW]"
    pattern = r"\d{1,2}°\s\d{1,2}[’']?\s\d{1,2}[”\"]?[NS][\s,][\/]?\s\d{1,3}°\s\d{1,2}[’']?\s\d{1,2}[”\"]?[EW]"

    matches = re.findall(pattern, data)
    if(len(matches) == 0 ):
        pattern = r"\d+°\d+\.\d+[’']\s*[NS]\s*\d+°\d+\.\d+[’']\s*[WE]"
        matches = re.findall(pattern, data)
    if(len(matches) == 0 ):
        pattern = r"\d+°\d+’\d+”[NS] / \d+°\d+’\d+”[EW]"
        matches = re.findall(pattern, data)
    return matches

def extract_dates(data):
    #print(data)
    pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(st|nd|rd|th)?,\s+(\d{4})"
    matches = re.findall(pattern, data)
    return matches

def can_we_skip(text):
    words = ["AUTONOMOUS","DREDGING", "NOURISHMENT", "FIREWORKS", "ORDNANCE", "ENDANGERED" ]
    pattern = "|".join(words)
    matches = re.findall(pattern, text, re.IGNORECASE)
    return(matches)


def split_sections(text):
    matches = re.findall(r'^[A-Z\s,–]+$', text, flags=re.MULTILINE)
    sections = re.split(r'^[A-Z\s,–]+$', text, flags=re.MULTILINE)[1:]
    blocks = []
    for i, match in enumerate(matches):
        section = sections[i].strip()
        # print(f"Matched Line: {match}")
        # print(f"Section Text: {section}")
        match_sc = re.search(r'SEACOAST', match, re.IGNORECASE)
        if( match_sc and not can_we_skip(match) ):
            blocks.append([ section, match ])
    return(blocks)

def extract_sections(filename):
    with open(filename, 'rb') as file:
        pdf_reader = PdfReader(file)
        total_pages = len(pdf_reader.pages)

        sections = []
        for page_num in range(total_pages):
            page = pdf_reader.pages[page_num]
            content = page.extract_text()
            matches = split_sections(content)
            sections += matches
        # Append the last section
        return sections
    
def aggregate_data(jsonfile,weeks):
    filename = os.path.splitext(os.path.basename(jsonfile))[0]
    logging.error(f'Started processing file: {filename}')
    data = {}
    week_number = filename.replace('lnm05','')
    week_number = week_number.replace('2022','')
    week_number = int(week_number)
    sections = extract_sections(jsonfile)
    # Access the data in the dictionary
    weeks[week_number] = dict()
    total_states = dict()
    vess_list = list()
    for section in sections:
            d = section[0]
            #print(d)
            #print(section[1])
            states = re.findall(r'\b[A-Z]{2}\b', section[1])
            extracted_states = ""
            if(len(states) > 1 ):
                extracted_states = '-'.join(states)
            if( len(states) == 1):
                extracted_states = states[0]
            # for st in states:
            #     if(st not in total_states):
            #         total_states[st] = 0
            if(len(extracted_states)):
                if(extracted_states not in total_states):
                    total_states[extracted_states]=0
            coords = extract_coords(d)
            dates = extract_dates( d )
            for name in vessels:
                if( len( name.split() ) >1 and name.lower() in d.lower() ):
                    # for st in states:
                    #    total_states[st] = total_states[st]+1
                    total_states[extracted_states] = total_states[extracted_states]+1
                    vess_list.append([name,coords,dates,extracted_states])
                if( len( name.split() ) == 1 and re.search(r"\b" + re.escape(name.lower()) + r"\b", d.lower()) ):
                    # for st in states:
                    #    total_states[st] = total_states[st]+1
                    total_states[extracted_states] = total_states[extracted_states]+1
                    vess_list.append([name,coords,dates,extracted_states])
    pair_string=""
    total_states = {key: value for key, value in total_states.items() if value != 0}
    for key, value in total_states.items():
        pair_string = pair_string+"," + ('{}: {}'.format(key, value) )
    weeks[week_number]['vess_list']=vess_list
    weeks[week_number]['states']=(pair_string)
    #print(total_states)

    

def main():
    weeks = {}
    ships = {}
    start_time = time.time()
    files_list = get_files(DATA_DIRECTORY,"pdf")
    #files_list = get_files(JSON_DIRECTORY,'json')
    #files_list = ['json/lnm05522022.json']
    #files_list = ['D05LNM2022/lnm05092022.pdf']
    #print(files_list)
    for jsonfile in files_list:
       aggregate_data(jsonfile,weeks)
    
    #print()
    vessels_in_week = {}
    json_data = {}
    for k in weeks:
        print("Week:",k)
        #print(weeks[k])
        new_list = list()
        json_data[k] = list()
        for n in weeks[k]['vess_list']:
            new_dict = dict()
            new_list.append(n[0])
            new_dict[n[0]] = dict()
            new_dict[n[0]]['coords'] = n[1]
            new_dict[n[0]]['dates'] = n[2]
            new_dict[n[0]]['state'] = n[3]
            ships[n[0]] = 1
            json_data[k].append(new_dict)
        vessels_in_week[k] = new_list
        #print(len(weeks[k]))
    #print(json_data)
    filename = DATA_DIRECTORY+"/vessels_data.csv"
    fieldnames = ['Week Number'] + list(vessels.keys() )+['Intensity']+['States']

    data = {}

    for row in vessels_in_week:
        data[row] = {column: 1 if column in vessels_in_week[row] else 0 for column in fieldnames}
        data[row]['Intensity']=(len(vessels_in_week[row]))
        data[row]['States'] = weeks[row]['states']

    # Update the dictionary with ones based on the mapping
    json_file = DATA_DIRECTORY+"/data"+".json"
    with open(json_file, 'w') as file:
        json.dump(data, file)

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        sorted_keys = sorted(data.keys())
        #for row_number, row_data in data.items():
        for row_number in sorted_keys:
            data[row_number]['Week Number'] = row_number 
            writer.writerow(data[row_number])

if __name__ == '__main__':
    main()