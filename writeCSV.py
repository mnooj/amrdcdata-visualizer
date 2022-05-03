## Place writeCSV.py in a directory, e.g. '~/Users/Desktop', along with an AWS .txt file, e.g. "10min-gil201601q10.txt"
## Open terminal and run the following command:
## python3 writeCSV.py "10min-gil201601q10.txt"
## The script will generate "10min-gil201601q10.csv" in the same directory

import csv
import sys

targetFile = sys.argv[1]                    ## Get filename from command line arg
data = open(targetFile, 'r')                ## Open existing .txt file

header = ['Year', 'Julian Day', 'Month', 'Day', 'Observation Time', 'Temperature', 'Pressure',
    'Wind Speed', 'Wind Direction', 'Relative Humidity', 'Delta-T']     ## Custom header

destFilepath, extension = targetFile.split('.')                         ## Get base filename

## Create new .csv file; decode UTF characters (writer expects ASCII)
with open(destFilepath + '.csv', 'w', encoding='UTF8', newline='') as newFile:
    writer = csv.writer(newFile)            ## Create writer
    writer.writerow(header)                 ## Write our custom header to csv
    for line in range(2):
        next(data)                          ## Skip header from .txt file
    for line in data:
        row = line.split()                  ## Split() cuts out all whitespaces and creates a clean array
        writer.writerow(row)                ## Write the array to a comma delineated row
