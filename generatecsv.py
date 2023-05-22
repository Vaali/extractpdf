import os
import time
import json
import re
from PyPDF2 import PdfReader
from utils import *
vessels = {
"Go Explorer":"https://media.fugro.com/media/docs/default-source/about-fugro-doc/vessels/fugro-explorer_a4.pdf?sfvrsn=26cc091a_14",
"R/V GO Discovery":"",
"R/V GO Pursuit":"",
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
    # for match in matches:
    #     print(match)
    return matches
def aggregate_data_old(jsonfile,weeks):
    filename = os.path.splitext(os.path.basename(jsonfile))[0]
    logging.error(f'Started processing file: {filename}')
    data = {}
    week_number = filename.replace('lnm05','')
    week_number = week_number.replace('2022','')
    week_number = int(week_number)
    # Open the JSON file
    with open(jsonfile, 'r') as f:
        # Load the data from the file into a dictionary
        data = json.load(f)
    # Access the data in the dictionary
    weeks[week_number] = list()
    for d in data:
        if('block' in d):
            coords = extract_coords(d['block'])
            dates = extract_dates( d['block'] )
            for name in vessels:
                # print(d.keys())
                # print(len(d['names']))
                # print(d['names'])
                if( len( name.split() ) >1 and name.lower() in d['block'].lower() ):
                    weeks[week_number].append([name.lower(),coords,dates])
                if( len( name.split() ) == 1 and re.search(r"\b" + re.escape(name.lower()) + r"\b", d['block'].lower()) ):
                    weeks[week_number].append([name.lower(),coords,dates])
        # if('coords' in d) and len(d['coords']) != 0:
        #     print(data)
        #     # marker_text = d['block'] 
        #     # for x in dirs :
        #     #     rect_coords.append(dms_to_decimal(d['coords'][x]))
        #     # marker_lats, marker_lons = zip(*rect_coords)
        #     # rect_coords.append(dms_to_decimal(d['coords']['NE']))
        #     # if(d['coords']['NE'] not in NE):
        #     #     NE[d['coords']['NE']] = 0
        #     # NE[d['coords']['NE']] = NE[d['coords']['NE']]+1
        #     # print(rect_coords)
        #     # print("\n")
        #     # lats, lons = zip(*rect_coords)
        #     # gmap.plot(lats, lons, 'cornflowerblue', edge_width=3)
        #     # for lat, lon in zip(marker_lats, marker_lons):
        #     #     gmap.marker(lat, lon, title=d['names'][0])
        #     # # label = d['names'][0]
        #     # # lat_center = sum(lats) / len(lats)
        #     # # lon_center = sum(lons) / len(lons)
        #     # # gmap.text(lat_center, lon_center, label)

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
            blocks.append(section)
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
    weeks[week_number] = list()
    for d in sections:
            coords = extract_coords(d)
            dates = extract_dates( d )
            for name in vessels:
                if( len( name.split() ) >1 and name.lower() in d.lower() ):
                    weeks[week_number].append([name.lower(),coords,dates,d])
                if( len( name.split() ) == 1 and re.search(r"\b" + re.escape(name.lower()) + r"\b", d.lower()) ):
                    weeks[week_number].append([name.lower(),coords,dates,d])

    

def main():
    weeks = {}
    ships = {}
    start_time = time.time()
    files_list = get_files(DATA_DIRECTORY,"pdf")
    #files_list = get_files(JSON_DIRECTORY,'json')
    #files_list = ['json/lnm05522022.json']
    #files_list = ['D05LNM2022/lnm05012022.pdf']
    #print(files_list)
    for jsonfile in files_list:
       aggregate_data(jsonfile,weeks)
    print(weeks)
    for k in weeks:
        print("Week:",k)
        print(len(weeks[k]))
        new_list = list()
        for n in weeks[k]:
            #parts = n[0].strip().split(" ")
            #print(parts)

            #if(len(parts) <= 5 ):
                new_list.append(n)
                ships[n[0]] = 1
        weeks[k] = new_list
        #print(len(weeks[k]))
    print(ships)
    for i in range(1,53):
        print(i,":\t",weeks[i])

if __name__ == '__main__':
    main()