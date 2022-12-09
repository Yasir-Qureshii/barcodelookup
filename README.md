### Website 
https://www.barcodelookup.com

The scraper reads a sibling **brands.xlsx** file for the barcode or search term in the only column of the excel. It then scrapes all the products for 
that barcode/keyword from barcodelookup.com and saves these products in an excel file. There should be a file named **brands.xlsx** in the same directory
where the script.py lies. The **brands.xlsx** should contain a single column containing barcodes and research terms.

The scraper scrapes the following fields;
 -- Product Name
 -- Barcode Formats
 -- Category
 -- Manufacturer
 -- Brand

### Procedure to run the scraper
#### Create and Activate the virtual environment(windows)
``virtualenv venv``  
``venv\scripts\venv``

#### Install Requirements
``pip install -r requirements.txt``

#### Run the scraper
``python script.py``
