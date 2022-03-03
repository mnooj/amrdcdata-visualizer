# This program accesses AWS and South Pole station observational data via the AMRDC Data Repository
# and generates simple line charts based on temperature, pressure, and wind speed measurements.
# Programmed by Matthew G. Noojin for the Antarctic Meteorological Research and Data Center, 2022
from flask import Flask, jsonify, request, render_template
from urllib.request import urlopen
import datetime
import matplotlib.pyplot as plt
import matplotlib
import base64
from io import BytesIO
import numpy as np
from pyld import jsonld
import json

app = Flask(__name__)

RECORDS = "https://raw.githubusercontent.com/mnooj/amrdc_data_visualizer/main/amrdcrecords.txt"
plt.style.use('ggplot')
plt.rcParams['axes.xmargin'] = 0
matplotlib.use('Agg')

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/index2')
def overlay_index():
    return render_template('overlay.html')

@app.route('/index3')
def boxplot_index():
    return render_template('boxplot.html')


def get_record_list():
    record_list = [
    ]  # [ ["South Pole", ['1958', URL], ['1959, URL], ... ], ["Byrd", ...] ]
    data = urlopen(RECORDS)
    for line in data:
        decoded_line = line.decode("utf-8")
        decoded_line = decoded_line.rstrip('\n')
        row = decoded_line.split(",")
        for item in row:
            if "\n" in item:
                item.split("\n")
        if len(row) == 1:
            record_list.append([row[0]])
        else:
            record_list[-1].append([row[0], row[1]])
    return record_list


## Returns a list of record_names + generates records_list of URLS organized by station name / year
@app.route("/list")
def get_record_names():
    record_names = []
    record_list = get_record_list()
    for item in record_list:
        record_names.append(item[0])
    return jsonify(record_names)


## Returns a list of records by year for selected station
@app.route("/years", methods=['GET', 'POST'])
def get_record_years():
    record_list = get_record_list()
    name = request.args.get('name')
    years = []
    for row in record_list:
        if row[0] == name:
            for item in row[1:]:
                years.append(item[0])
            break
    return jsonify(years)



@app.route("/boxplot", methods=['GET', 'POST'])
def boxplot():
    selection = request.args.get('name')
    year1 = request.args.get('year1')
    year2 = request.args.get('year2')
    index = int(request.args.get('field'))

    years = []
    plot_data = []

    if int(year1) > int(year2):
        start_year = int(year2)
        end_year = int(year1)
    else:
        start_year = int(year1)
        end_year = int(year2)
    for i in range(start_year, end_year+1):
        years.append(i)
    
    max = [None, None]
    min = [None, None]

    for i in years:
        year = str(i)
        link = get_link(selection, year)
        json_link = link + ".jsonld"
        data = readData(selection, year, json_link)
        yearly_data = data[:, index]
        plot_data.append(yearly_data)

        for row in data:
            if max == [None, None]:
                min = [row[0], row[index]]
                max = [row[0], row[index]]
            if max[1] <= row[index]:
                max = [row[0], row[index]]
            if min[1] >= row[index]:
                min = [row[0], row[index]]

    units = [None, "Temperature (C)", "Pressure (hPa)", "Wind Speed (m/s)"]
    field = units[index]
    fig, plot = plt.subplots()
    fig.set_figheight(6)
    fig.set_figwidth(12)
    plot.boxplot(plot_data, positions=years )
    plot.set_ylabel(units[index])
    plot.grid(True)
    plot.set_title('Max ' + field + ': ' + str(max[1]) + ', Date: (' + str(max[0]) +
                   '). Min ' + field + ': ' + str(min[1]) + ', Date: (' + str(min[0]) + ').',
                   fontsize='small')
    plt.suptitle(field + " measurements, " + selection + ' Station, ' +
                year1 + ' - ' + year2 + '.')
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


## Returns a graph of selected data
@app.route("/plot", methods=['GET', 'POST'])
def plot():
    selection = request.args.get('name')
    year = request.args.get('year')
    index = int(request.args.get('field'))
    link = get_link(selection, year)
    json_link = link + ".jsonld"
    units = [None, "Temperature (C)", "Pressure (hPa)", "Wind Speed (m/s)"]
    field = units[index]
    data = readData(selection, year, json_link)
    fig, plot = plt.subplots()
    fig.set_figheight(6)
    fig.set_figwidth(12)
    plot.plot(data[:, 0], data[:, index])
    avg = np.nanmean(data[:, index], dtype='float32')
    plot.hlines(y=avg,
                xmin=data[:, 0][0],
                xmax=data[:, 0][-1],
                linestyle='-',
                alpha=0.7)
    plot.set_ylabel(units[index])
    plot.grid(True)
    max = [data[0][0], data[0][index]]
    min = [data[0][0], data[0][index]]
    for row in data:
        if max[1] <= row[index]:
            max = [row[0], row[index]]
        if min[1] >= row[index]:
            min = [row[0], row[index]]
    plot.set_title('Max ' + field + ': ' + str(max[1]) + ', Date: (' + str(max[0]) +
                   '). Min ' + field + ': ' + str(min[1]) + ', Date: (' + str(min[0]) + ').',
                   fontsize='small')
    plt.suptitle(field + " measurements, " + selection + ' Station, ' +
                 str(data[0][0].year))
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

@app.route("/overlay", methods=['GET', 'POST'])
def plot_overlay():
    selection = request.args.get('name')
    year = request.args.get('year')
    index = int(request.args.get('field'))
    link = get_link(selection, year)
    json_link = link + ".jsonld"
    selection2 = request.args.get('name2')
    year2 = request.args.get('year2')
    link2 = get_link(selection2, year2)
    json_link2 = link2 + ".jsonld"
    units = [None, "Temperature (C)", "Pressure (hPa)", "Wind Speed (m/s)"]
    field = units[index]
    data = readData(selection, year, json_link)
    data2 = readData(selection2, year2, json_link2)
    fig, plot = plt.subplots()
    fig.set_figheight(6)
    fig.set_figwidth(12)
    temp_data = []  ## Should deal with Leap Year here
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
    plot.plot(data[:, 0],
              data[:, index],
              label=(selection + ' ' + str(data[0][0].year)))
    plot.plot(data[:, 0],
              data2[:, index],
              alpha=0.6,
              label=(selection2 + ' ' + str(data2[0][0].year)))
    avg1 = np.nanmean(data[:, index], dtype='float32')
    avg2 = np.nanmean(data2[:, index], dtype='float32')
    plot.hlines(y=avg1,
                xmin=data[:, 0][0],
                xmax=data[:, 0][-1],
                alpha=0.7,
                label=('Avg ' + selection + ' ' + str(data[0][0].year)))
    plot.hlines(y=avg2,
                xmin=data[:, 0][0],
                xmax=data[:, 0][-1],
                alpha=0.7,
                label=('Avg ' + selection2 + ' ' + str(data2[0][0].year)))
    plot.set_ylabel(units[index])
    max = [data[0][0], data[0][index], selection]
    min = [data[0][0], data[0][index], selection]
    for row in data:
        if max[1] <= row[index]:
            max = [row[0], row[index], selection]
        if min[1] >= row[index]:
            min = [row[0], row[index], selection]
    for row in data2:
        if max[1] <= row[index]:
            max = [row[0], row[index], selection2]
        if min[1] >= row[index]:
            min = [row[0], row[index], selection2]
    plot.grid(True)
    plot.set_title('Max ' + field + ': ' + str(max[1]) + ", " + max[2] +
                   ' Station, Date: (' + str(max[0]) + '). Min ' + field + ': ' +
                   str(min[1]) + ", " + min[2] + ' Station, Date: (' + str(min[0]) + ').',
                   fontsize='small')
    plot.legend()
    plot.tick_params(labelbottom=False)
    plt.suptitle(field + " measurements, " + selection + ' Station, ' +
                 str(data[0][0].year) + ' / ' + selection2 + ' Station, ' +
                 str(data2[0][0].year))
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

@app.route("/repo/<string:selection>/<string:year>", methods=['GET', 'POST'])
def get_link(selection, year):
    link = ""
    record_list = get_record_list()
    for item in record_list:
        if item[0] == selection:
            for record in item[1:]:
                if record[0] == year:
                    link = record[1]
                    break
    return link


def get_resources(station_yearly_record):
    doc = jsonld.flatten(station_yearly_record)
    doc = json.dumps(doc)
    resource_list = []
    data = doc.split('"')
    for string in data:
        if "download" in string:
            resource_list.append(string)
    pop_list = []
    for item in reversed(resource_list):
        if "10min" in item or "3hr" in item:
            pop_list.append(resource_list.index(item))
    for index in pop_list:
        resource_list.pop(index)
    return resource_list


def readData(name, year, json_link):
    daily_data = []
    resource_list = get_resources(json_link)
    for url in resource_list:
        data = urlopen(url)
        if name == "South Pole Station":
            for line in data:
                decoded_line = line.decode("utf-8")
                row = decoded_line.split()
                time = int(row[3])
                day = datetime.datetime(int(year), int(row[1]), int(row[2]),
                                        int(time / 100), 00)
                temp = float(row[7])
                pressure = float(row[8])
                windspeed = float(row[5])
                daily_data.append([day, temp, pressure, windspeed])
        else:
            for line in range(2):
                next(data)
            for line in data:
                decoded_line = line.decode("utf-8")
                row = decoded_line.split()
                time = int(row[4])
                day = datetime.datetime(int(year), int(row[2]), int(row[3]),
                                        int(time / 100), 00)
                temp = float(row[5])
                pressure = float(row[6])
                windspeed = float(row[7])
                daily_data.append([day, temp, pressure, windspeed])
    for row in daily_data:  ### Replace outliers with nan
        if row[1] >= 99.9:
            row[1] = np.nan
        if row[2] >= 9999.9:
            row[2] = np.nan
        if row[3] >= 99.9:
            row[3] = np.nan
    daily_data = np.array(daily_data)
    daily_data = daily_data[daily_data[:, 0].argsort()]
    return daily_data


if __name__ == '__main__':
    app.run()
    #app.run(debug=True)