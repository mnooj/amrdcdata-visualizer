# amrdcdata-visualizer

by Matthew Noojin, Antarctic Meteorological Research and Data Center

The AMRDC Data Visualizer collects data from the AMRDC Data Repository (built on the CKAN platform) and displays basic graphs along with direct links
to the raw data.

The app consists of a Python Flask API and an HTML/JavaScript front-end. The program assembles queries based on user input and sends them to CKAN, which
produces a list of direct links to resources (i.e. monthly weather observations in ASCII format); reads the text files and isolates the requested columns; 
plots the data using Matplotlib; then converts the image to HTML and delivers it to the web interface. All of the fields and data are generated dynamically 
from the current Repository catalog.

All requirements are contained in requirements.txt. The current file structure is designed for easy installation and deployment on any web server. The 
Procfile allows for seamless deployment on the Heroku platform.

Demonstration: https://amrdcdata-visualizer.herokuapp.com/.
