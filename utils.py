import glob

HTML_DIRECTORY = 'html'
JSON_DIRECTORY = 'json'
DATA_DIRECTORY = 'data'

def get_files(dir_path, extension):
    pdf_files = glob.glob(dir_path+'/*.'+extension)
    return pdf_files