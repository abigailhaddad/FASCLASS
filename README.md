# FASCLASS

This contains three files:

-the main.py files for pulling FASCLASS position descriptions from https://acpol2.army.mil/fasclass/search_fs/search_fasclass.asp if you have the position description #s you're interested in. the process for this is that we search bing for the position description number and look for a link that's formatted correctly, and then scrape the text from that page. if that doesn't work, we try google. the resulting text is cleaned. this is done in chunks of 10,000 PDs, and then written out to a .csv and .xslx file

-the requirements.txt file for running this code

-the pulFromPythonAnywhere script for pulling down the resulting XLSX data from my pythonanywhere account, if you have the API key
