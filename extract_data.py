from lxml import html
import re

def extract_dates(data):
    #lines = data.split("\n")
    #print(lines)
    pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})"
    matches = re.findall(pattern, data)
    for match in matches:
        print(match)


def extract_blocks():
    # Load the HTML file into a tree object
    with open('output121.html', 'r') as f:
        tree = html.fromstring(f.read())

    # Use XPath to get a list of elements
    elements = tree.xpath('//div[not(parent::div)]')
    pattern = r'OFFSHORE SURVEY'
    matches = []
    for element in elements:
        match = re.search(pattern, element.text_content(), re.IGNORECASE)

        if(match):
            #print(element.text_content())
            matches.append(element.text_content())
    for block in matches:
        extract_dates(block)
    print(len(matches) )
    

def main():
    extract_blocks()

if __name__ == '__main__':
    main()
