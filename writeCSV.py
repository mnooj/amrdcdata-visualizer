import csv
import sys

targetFile = sys.argv[1]                   ## Get filename from command line arg
data = open(targetFile, 'r')              ## Open existing .txt file
header = ['Year', 'Julian Day', 'Month', 'Day', 'Observation Time', 'Temperature', 'Pressure',
    'Wind Speed', 'Wind Direction', 'Relative Humidity', 'Delta-T']     ## Custom header
targetFilepath, extension = targetFile.split('.')
## Create new .csv file; decode UTF characters (writer expects ASCII)
with open(targetFilepath + '.csv', 'w', encoding='UTF8', newline='') as newFile:
    writer = csv.writer(newFile)        ## Create writer
    writer.writerow(header)             ## Write our custom header to csv
    for line in range(2):
        next(data)                      ## Skip header from .txt file
    for line in data:
        row = line.split()              ## Split() cuts out all whitespaces and creates a clean array
        writer.writerow(row)            ## Write the array to a comma delineated row
