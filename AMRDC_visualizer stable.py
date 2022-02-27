# This program accesses AWS and South Pole station observational data via the AMRDC Data Repository
# and generates simple line charts based on temperature, pressure, and wind speed measurements.
# Programmed by Matthew G. Noojin for the Antarctic Meteorological Research and Data Center, 2022
from urllib.request import urlopen
import datetime
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('ggplot')
plt.rcParams['axes.xmargin'] = 0

#### Links to repository
SOUTHPOLE = {
    '1958' : "https://amrdcdata.ssec.wisc.edu/dataset/surface-observational-data-amundsen-scott-south-pole-station-1958.jsonld",
    '1959' : "https://amrdcdata.ssec.wisc.edu/dataset/surface-observational-data-amundsen-scott-south-pole-station-1959.jsonld"
    }
AWS = {
    'Byrd': {
        '2019' : "https://amrdcdata.ssec.wisc.edu/dataset/quality-controlled-observational-data-byrd-automatic-weather-station-2019.jsonld",
        '2020' : "https://amrdcdata.ssec.wisc.edu/dataset/quality-controlled-observational-climatology-data-byrd-automatic-weather-system-2020.jsonld"
    },
    'Dome C' : {
        '2019' : "https://amrdcdata.ssec.wisc.edu/dataset/quality-controlled-observational-data-dome-c-automatic-weather-station-2019.jsonld",
        '2020' : "https://amrdcdata.ssec.wisc.edu/dataset/quality-controlled-observational-data-dome-c-automatic-weather-station-2020.jsonld"
    }
}
def get_resources(station_yearly_record):
    data = urlopen(station_yearly_record)
    resource_list = []
    for line in data:
            decoded_line = line.decode("utf-8")
            row = decoded_line.split('"')
            for string in row:
                if "download" in string:
                    resource_list.append(string)
    return resource_list

def readSouthPole(year):
    daily_data = []
    resource_list = get_resources(SOUTHPOLE[year])
    for url in resource_list:
        data = urlopen(url)
        for line in data:
            decoded_line = line.decode("utf-8")
            row = decoded_line.split()
            time = int(row[3])
            day = datetime.datetime(int(year), int(row[1]), int(row[2]), int(time/100), 00)
            temp = float(row[7])
            pressure = float(row[8])
            windspeed = float(row[5])
            daily_data.append([day, temp, pressure, windspeed])
    for row in daily_data:                ### Replace outliers with nan
        if row[1] >= 99.9:
            row[1] = np.nan
        if row[2] >= 9999.9:
            row[2] = np.nan
        if row[3] >= 99.9:
            row[3] = np.nan
    daily_data = np.array(daily_data)
    daily_data = daily_data[daily_data[:, 0].argsort()]
    return daily_data

def readAWS(aws_name, year):
    daily_data = []
    resource_list = get_resources(AWS[aws_name][year])
    for url in resource_list:
        data = urlopen(url)
        for line in range(2):           ## Remove first 2 lines - header
            next(data)
        for line in data:
            decoded_line = line.decode("utf-8")
            row = decoded_line.split()
            time = int(row[4])
            day = datetime.datetime(int(year), int(row[2]), int(row[3]), int(time/100), 00)
            temp = float(row[5])
            pressure = float(row[6])
            windspeed = float(row[7])
            daily_data.append([day, temp, pressure, windspeed])
    for row in daily_data:                ### Replace outliers with nan
        if row[1] >= 99.9:
            row[1] = np.nan
        if row[2] >= 9999.9:
            row[2] = np.nan
        if row[3] >= 99.9:
            row[3] = np.nan
    daily_data = np.array(daily_data)
    daily_data = daily_data[daily_data[:, 0].argsort()]
    return daily_data

def temp_plot(data, selection):
        fig, temp_plot = plt.subplots()
        temp_plot.plot(data[:,0], data[:,1])
        avg_temp = np.nanmean(data[:,1],dtype='float32')
        temp_plot.axhline(y=avg_temp, color='r', linestyle='-', alpha=0.3)
        temp_plot.set_ylabel('Temperature (C)')
        temp_plot.grid(True)
        max_temp = [data[0][0], data[0][1]]
        min_temp = [data[0][0], data[0][1]]
        for row in data:
            if max_temp[1] <= row[1]:
                max_temp = [row[0], row[1]]
            if min_temp[1] >= row[1]:
                min_temp = [row[0], row[1]]
        temp_plot.set_title('Max temp: ' + str(max_temp[1]) + " Celsius " + str(max_temp[0]) + '. Min temp: ' + str(min_temp[1]) + " Celsius " + str(min_temp[0]), fontsize='small')
        plt.suptitle("Temperature measurements, " + selection + ' Station, ' + str(data[0][0].year))
        plt.show()

def temp_plot_overlay(data, data2, selection, selection2):
        fig, temp_plot = plt.subplots()
        ## Should deal with Leap Year here
        temp_data = []
        temp_data2 = []
        for row in data:
            if row[0].day == 29 and row[0].month == 2: 
                continue
            else:
                temp_data.append(row)
        data = np.array(temp_data)
        for row in data2:
            if row[0].day == 29 and row[0].month == 2: 
                continue
            else:
                temp_data2.append(row)
        data2 = np.array(temp_data2)
        temp_plot.plot(data[:,0], data[:,1], label=(selection + ' ' + str(data[0][0].year)))
        temp_plot.plot(data[:,0], data2[:,1], alpha=0.6, label=(selection2 + ' ' + str(data2[0][0].year)))
        avg_temp1 = np.nanmean(data[:,1],dtype='float32') 
        avg_temp2 = np.nanmean(data2[:,1],dtype='float32')
        temp_plot.axhline(y=avg_temp1, linestyle='-', alpha=0.3, label=('Avg ' + selection + ' ' + str(data[0][0].year)))
        temp_plot.axhline(y=avg_temp2, linestyle='-', alpha=0.3, label=('Avg ' + selection2 + ' ' + str(data2[0][0].year)))
        temp_plot.set_ylabel('Temperature (C)')
        max_temp = [data[0][0], data[0][1], selection]
        min_temp = [data[0][0], data[0][1], selection]
        for row in data:
            if max_temp[1] <= row[1]:
                max_temp = [row[0], row[1], selection]
            if min_temp[1] >= row[1]:
                min_temp = [row[0], row[1], selection]
        for row in data2:
            if max_temp[1] <= row[1]:
                max_temp = [row[0], row[1], selection2]
            if min_temp[1] >= row[1]:
                min_temp = [row[0], row[1], selection2]
        temp_plot.grid(True) 
        temp_plot.set_title('Max temp: ' + str(max_temp[1]) + " Celsius, " + max_temp[2] + ' Station, ' + str(max_temp[0]) + '. Min temp: ' + str(min_temp[1]) + " Celsius, " + min_temp[2] + ' Station, ' + str(min_temp[0]), fontsize='small')
        temp_plot.legend()
        temp_plot.tick_params(labelbottom=False)
        plt.suptitle("Temperature measurements, " + selection + ' Station, ' + str(data[0][0].year) + ' / ' + selection2 + ' Station, ' + str(data2[0][0].year))
        plt.show()

def pressure_plot(data, selection):
        fig, pressure_plot = plt.subplots()
        pressure_plot.plot(data[:,0], data[:,2])
        avg_press = np.nanmean(data[:,2],dtype='float32')
        pressure_plot.axhline(y=avg_press, color='r', linestyle='-', alpha=0.3)
        pressure_plot.set_ylabel('Pressure (hPa)')
        pressure_plot.grid(True)
        max_press = [data[0][0], data[0][2]]
        min_press = [data[0][0], data[0][2]]
        for row in data:
            if max_press[1] <= row[2]:
                max_press = [row[0], row[2]]
            if min_press[1] >= row[2]:
                min_press = [row[0], row[2]]
        pressure_plot.set_title('Max press: ' + str(max_press[1]) + " hPa " + str(max_press[0]) + '. Min press: ' + str(min_press[1]) + ' hPa ' + str(min_press[0]), fontsize='small')
        plt.suptitle("Pressure measurements, " + selection + ' Station, ' + str(data[0][0].year))
        plt.show()

def pressure_plot_overlay(data, data2, selection, selection2):
        fig, pressure_plot = plt.subplots()
        temp_data = []
        temp_data2 = []
        for row in data:
            if row[0].day == 29 and row[0].month == 2: 
                continue
            else:
                temp_data.append(row)
        data = np.array(temp_data)
        for row in data2:
            if row[0].day == 29 and row[0].month == 2: 
                continue
            else:
                temp_data2.append(row)
        data2 = np.array(temp_data2)
        pressure_plot.plot(data[:,0], data[:,2], label=(selection + ' ' + str(data[0][0].year)))
        pressure_plot.plot(data[:,0], data2[:,2], color='green', alpha=0.5, label=(selection2 + ' ' + str(data2[0][0].year)))
        avg_press1 = np.nanmean(data[:,2],dtype='float32')
        avg_press2 = np.nanmean(data2[:,2],dtype='float32')
        pressure_plot.axhline(y=avg_press1, linestyle='-', alpha=0.3, label = ('Avg ' + selection + ' ' + str(data[0][0].year)))
        pressure_plot.axhline(y=avg_press2, linestyle='-', alpha=0.3, label = ('Avg ' + selection2 + ' ' + str(data2[0][0].year)))
        pressure_plot.set_ylabel('hPa')
        max_press = [data[0][0], data[0][2], selection]
        min_press = [data[0][0], data[0][2], selection]
        for row in data:
            if max_press[1] <= row[2]:
                max_press = [row[0], row[2], selection]
            if min_press[1] >= row[2]:
                min_press = [row[0], row[2], selection]
        for row in data2:
            if max_press[1] <= row[2]:
                max_press = [row[0], row[2], selection2]
            if min_press[1] >= row[2]:
                min_press = [row[0], row[2], selection2]
        pressure_plot.grid(True)
        pressure_plot.set_title('Max pressure: ' + str(max_press[1]) + " hPa, " + max_press[2] + ' Station, ' + str(max_press[0]) + '. Min pressure: ' + str(min_press[1]) + " hPa, " + min_press[2] + ' Station, ' + str(min_press[0]), fontsize='small')
        pressure_plot.legend()
        pressure_plot.tick_params(labelbottom=False)
        plt.suptitle("Pressure measurements, " + selection + ' Station, ' + str(data[0][0].year) + ' / ' + selection2 + ' Station, ' + str(data2[0][0].year))
        plt.show()

def windspeed_plot(data, selection):
        fig, windspeed_plot = plt.subplots()
        windspeed_plot.plot(data[:,0], data[:,3])
        avg_wind = np.nanmean(data[:,3],dtype='float32')
        windspeed_plot.axhline(y=avg_wind, color='r', linestyle='-', alpha=0.3)
        windspeed_plot.set_ylabel('Wind Speed (m/s)')
        windspeed_plot.grid(True)
        max_wind = [data[0][0], data[0][3]]
        min_wind = [data[0][0], data[0][3]]
        for row in data:
            if max_wind[1] <= row[3]:
                max_wind = [row[0], row[3]]
            if min_wind[1] >= row[3]:
                min_wind = [row[0], row[3]]
        windspeed_plot.set_title('Max wind speed: ' + str(max_wind[1]) + " m/s " + str(max_wind[0]) + '. Min wind speed: ' + str(min_wind[1]) + ' hPa ' + str(min_wind[0]), fontsize='small')
        plt.suptitle("Wind speed measurements, " + selection + ' Station, ' + str(data[0][0].year))
        plt.show()

def windspeed_plot_overlay(data, data2, selection, selection2):
        fig, windspeed_plot = plt.subplots()
        temp_data = []
        temp_data2 = []
        for row in data:
            if row[0].day == 29 and row[0].month == 2: 
                continue
            else:
                temp_data.append(row)
        data = np.array(temp_data)
        for row in data2:
            if row[0].day == 29 and row[0].month == 2: 
                continue
            else:
                temp_data2.append(row)
        data2 = np.array(temp_data2)
        windspeed_plot.plot(data[:,0], data[:,3], label=(selection + ' ' + str(data[0][0].year)))
        windspeed_plot.plot(data[:,0], data2[:,3], color='green', alpha=0.5, label=(selection2 + ' ' + str(data2[0][0].year)))
        avg_wind1 = np.nanmean(data[:,3],dtype='float32')
        avg_wind2 = np.nanmean(data2[:,3],dtype='float32')
        windspeed_plot.axhline(y=avg_wind1, linestyle='-', alpha=0.3, label = ('Avg ' + selection + ' ' + str(data[0][0].year)))
        windspeed_plot.axhline(y=avg_wind2, linestyle='-', alpha=0.3, label = ('Avg ' + selection2 + ' ' + str(data2[0][0].year)))
        windspeed_plot.set_ylabel('m/s')
        max_wind = [data[0][0], data[0][3], selection]
        min_wind = [data[0][0], data[0][3], selection]
        for row in data:
            if max_wind[1] <= row[3]:
                max_wind = [row[0], row[3], selection]
            if min_wind[1] >= row[3]:
                min_wind = [row[0], row[3], selection]
        for row in data2:
            if max_wind[1] <= row[3]:
                max_wind = [row[0], row[3], selection2]
            if min_wind[1] >= row[3]:
                min_wind = [row[0], row[3], selection2]
        windspeed_plot.grid(True)
        windspeed_plot.set_title('Max wind speed: ' + str(max_wind[1]) + " m/s " + max_wind[2] + ' Station, ' + str(max_wind[0]) + '. Min wind speed: ' + str(min_wind[1]) + " m/s, " + min_wind[2] + ' Station, ' + str(min_wind[0]), fontsize='small')
        windspeed_plot.legend()
        windspeed_plot.tick_params(labelbottom=False)
        plt.suptitle("Wind speed measurements, " + selection + ' Station, ' + str(data[0][0].year) + ' / ' + selection2 + ' Station, ' + str(data2[0][0].year))
        plt.show()

def main():
    print("AMRDC Data Visualizer. (NOTE: All entries are case-sensitive!)")
    print("Which dataset would you like to visualize?")
    print("South Pole       AWS")
    selection = input("Your selection: ")
    if selection == "South Pole":
        first_viz_name = selection
        print("Which year would you like to visualize?")
        for key in SOUTHPOLE:
            print(key)
        year = input("Your selection: ")
        data = np.array(readSouthPole(year))
        print("Which measurement would you like to plot?")
        print("Temperature      Pressure        Wind Speed")
        measurement = input("Your selection: ")
        if measurement == "Temperature":
            temp_plot(data, first_viz_name)
        elif measurement == "Pressure":
            pressure_plot(data, first_viz_name)
        elif measurement == "Wind Speed":
            windspeed_plot(data, first_viz_name)   
    if selection == "AWS":
        print("Which AWS would you like to visualize?")
        for key in AWS:
            print(key)
        aws_selection = input("Your selection: ")
        first_viz_name = aws_selection
        print("Which year of " + aws_selection + " AWS would you like to visualize?")
        for key in AWS[aws_selection]:
            print(key)
        year = input("Your selection: ")
        data = np.array(readAWS(aws_selection, year))
        print("Which measurement would you like to plot?")
        print("Temperature      Pressure        Wind Speed")
        measurement = input("Your selection: ")
        if measurement == "Temperature":
            temp_plot(data, first_viz_name)
        elif measurement == "Pressure":
            pressure_plot(data, first_viz_name)
        elif measurement == "Wind Speed":
            windspeed_plot(data, first_viz_name)

    print("Type Overlay to overlay a different year on top of your visualization, or New to start a new query.")
    overlay = input("Your selection: ")
    if overlay == "Overlay":
        print("Which dataset would you like to overlay?")
        print("South Pole       AWS")
        selection = input("Your selection: ")
        if selection == "South Pole":
            print("Which year would you like to visualize?")
            for key in SOUTHPOLE:
                print(key)
            year = input("Your selection: ")
            data2 = np.array(readSouthPole(year))
            if measurement == "Temperature":
                temp_plot_overlay(data, data2, first_viz_name, selection)
            elif measurement == "Pressure":
                pressure_plot_overlay(data, data2, first_viz_name, selection)
            elif measurement == "Wind Speed":
                windspeed_plot_overlay(data, data2, first_viz_name, selection)
        if selection == "AWS":
            print("Which AWS would you like to visualize?")
            for key in AWS:
                print(key)
            aws_selection = input("Your selection: ")
            print("Which year of " + aws_selection + " AWS would you like to visualize?")
            for key in AWS[aws_selection]:
                print(key)
            year = input("Your selection: ")
            data2 = np.array(readAWS(aws_selection, year))
            if measurement == "Temperature":
                temp_plot_overlay(data, data2, first_viz_name, aws_selection)
            elif measurement == "Pressure":
                pressure_plot_overlay(data, data2, first_viz_name, aws_selection)
            elif measurement == "Wind Speed":
                windspeed_plot_overlay(data, data2, first_viz_name, aws_selection)
    if overlay == "New":
        main()

if __name__ == "__main__":
    main()