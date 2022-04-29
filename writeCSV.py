import csv 

def writeCSV(datafile, targetFilepath):
    data = open(datafile, 'r')              ## Open existing .txt file
    header = ['Year', 'Julian Day', 'Month', 'Day', 'Observation Time', 'Temperature', 'Pressure',
        'Wind Speed', 'Wind Direction', 'Relative Humidity', 'Delta-T']     ## Custom header

    ## Create new .csv file; decode UTF characters (writer expects ASCII)
    with open(targetFilepath + '.csv', 'w', encoding='UTF8', newline='') as newFile:
        writer = csv.writer(newFile)        ## Create writer
        writer.writerow(header)             ## Write our custom header to csv
        for line in range(2):
            next(data)                      ## Skip two line header from .txt file
        for line in data:           
            row = line.split()              ## Split() cuts out all whitespaces and creates an array of strings
            writer.writerow(row)            ## Write the array to a comma delineated row
