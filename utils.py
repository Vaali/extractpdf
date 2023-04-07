import glob
import logging

HTML_DIRECTORY = 'html'
JSON_DIRECTORY = 'json'
DATA_DIRECTORY = 'data'
MAPS_DIRECTORY = 'maps'
logging.basicConfig(filename='conversion.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')
def get_files(dir_path, extension):
    pdf_files = glob.glob(dir_path+'/*.'+extension)
    return pdf_files
