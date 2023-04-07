Main aim of the project is to extract data from pdfs and trying to plot the relevant data from the data.

1. Clone the repository.
2. Download the relevant pdfs and put them in a directory named data.
3. Install the requirements by running following command
```pip install -r requirements.txt```

4. First part of the program is to convert pdf files in data directory to html. These files are created in a html folder.
```python pdf2html.py```
5. Extract data from html files created from previous step and add them to json files written to json folder.
```python extract_data.py```
6. Last step is to plot the data from json files to a map.
```python plotmap.py```
