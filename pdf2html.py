from io import BytesIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import glob
import os
import time

HTML_DIRECTORY = 'html'
DATA_DIRECTORY = 'data'

def convert_pdffile( pdffile ):
    
    filename = os.path.splitext(os.path.basename(pdffile))[0]

    htmlfilepath = HTML_DIRECTORY+'/'+filename+'.html'
    with open(pdffile, 'rb') as fh:
        input_bytes = BytesIO(fh.read())

    with open(htmlfilepath, 'wb') as fh:
        rsrcmgr = PDFResourceManager()
        codec = 'utf-8'
        laparams = LAParams()
        device = HTMLConverter(rsrcmgr, fh, codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()

        for page in PDFPage.get_pages(input_bytes, pagenos, maxpages=maxpages, password=password, caching=caching,
                                    check_extractable=True):
            interpreter.process_page(page)

        device.close()

def get_files(dir_path):
    pdf_files = glob.glob(dir_path+'/*.pdf')
    return pdf_files

def main():
    if not os.path.exists(HTML_DIRECTORY):
        os.makedirs(HTML_DIRECTORY)
    
    files_list = get_files(DATA_DIRECTORY)
    start_time = time.time()

    #files_list = ['data/lnm05382022.pdf']
    for pdffile in files_list:
        convert_pdffile(pdffile)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")



if __name__ == '__main__':
    main()