from io import BytesIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import glob
import os
import time
import multiprocessing
from utils import *
from io import StringIO
import re


def convert_pdffile_old( pdffile ):
    
    filename = os.path.splitext(os.path.basename(pdffile))[0]
    logging.error(f'Started processing file: {filename}')
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
    logging.error(f'Completed processing file: {filename}')

def convert_pdffile( pdffile ):
    
    filename = os.path.splitext(os.path.basename(pdffile))[0]
    logging.error(f'Started processing file: {filename}')
    htmlfilepath = HTML_DIRECTORY+'/'+filename+'.html'
    print(htmlfilepath)
    with open(pdffile, 'rb') as fp:
        # Create a PDF resource manager and set up a string object to receive the output HTML
        resource_manager = PDFResourceManager()
        output_string = BytesIO()
        codec = 'utf-8'
        # Set up the HTML converter
        laparams = LAParams()
        laparams.no_footnotes = True  # Skip footnotes
        laparams.no_frames = True 
        converter = HTMLConverter(resource_manager, output_string, laparams=laparams)

        # Create a PDF interpreter object
        interpreter = PDFPageInterpreter(resource_manager, converter)

        # Process each page in the PDF file
        for page in PDFPage.get_pages(fp, check_extractable=True):
            interpreter.process_page(page)

        # Get the final HTML output
        html = output_string.getvalue().decode()
        html = re.sub(r'<sup[^>]*>.*?</sup>', '', html)

        # Remove borders
        html = re.sub(r'border:[^;"]*;?', '', html)
    # Save the HTML to a file
    with open(htmlfilepath, 'w', encoding='utf-8') as html_file:
        html_file.write(html)


def main():
    if not os.path.exists(HTML_DIRECTORY):
        os.makedirs(HTML_DIRECTORY)
    
    files_list = get_files(DATA_DIRECTORY,"pdf")
    start_time = time.time()

    files_list = [DATA_DIRECTORY+'/lnm05522022.pdf']
    #for pdffile in files_list:
    #    convert_pdffile(pdffile)
    
    # Create a process pool with 4 workers
    pool = multiprocessing.Pool(processes=4)

    # Convert all PDF files to HTML in parallel
    pool.map(convert_pdffile, files_list)

    # Close the pool and wait for the work to finish
    pool.close()
    pool.join()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")



if __name__ == '__main__':
    main()