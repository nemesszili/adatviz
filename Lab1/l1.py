# T - temperature
# Po - pressure at weather station level
# P - pressure at sea level
# U - humidity
# DD - mean wind direction at 10-12 meters
# FF - mean wind speed at 10-12 meters(m/s)
# FF10 - empty
# FF3 - maximum gust value at 10-12 meters between two observations
# Tn - minimum temperature over the last 12h
# Tx - maximum temperature over the last 12h
# Cl - cloud
# Nh - dunno
# H - height of the base of the lowest clouds
# VV - horizontal visibility in km(empty during night hours)
# RRR - amount of precipitation in mm
# sss - snow depth

arrayTime = [] #0
arrayTemperature = [] #T1
arrayPressure = [] #P3
arrayHumidity = [] #U5
arrayWindDirection = [] #DD6
arrayWindSpeed = [] #FF7

arrayWindDirectionNumbers = []

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from windrose import WindroseAxes

# Create layout
axesTemperature = plt.subplot2grid((3,3),(0,0), colspan=2)
axesHumidity = plt.subplot2grid((3,3), (1,0), colspan=2)
axesPressure = plt.subplot2grid((3,3), (2,0), colspan=2)
axesWindSpeed = plt.subplot2grid((3,3), (0,2))

ax = plt.subplot2grid((3,3), (1,2), rowspan=2)
axesWindDirection = WindroseAxes(plt.gcf(), list(ax.get_position().bounds))
plt.gcf().add_axes(axesWindDirection)
plt.gcf().delaxes(ax)

def plotToAxis(ax, x, y, reversed=True):
    dist = (max(y)-min(y))/10
    ax.set_ylim([min(y)-dist, max(y)+dist])
    if reversed:
        y = y[::-1]
    ax.plot(x, y)
    # ax.yaxis.set_ticks(np.arange(min(y), max(y), 0.8))

def movePlotAlongXAxis(ax, dist):
    pos = np.array(ax.get_position().bounds)
    pos[0] += dist
    ax.set_position(pos)

def xaxisFormatter(tick_val, tick_pos):
    if tick_val >= 0 and tick_val < len(arrayTime):
        return arrayTime[int(tick_val)]
    return ''

def transformWindDirectionToNumber(windDirection):
    directions = windDirection.split('-')
    if len(directions) == 1 and directions[0] == '':
        return -1
    if len(directions) == 1:
        d = directions[0]
        if d == "north":
            return 0
        if d == "east":
            return 90
        if d == "south":
            return 180
        if d == "west":
            return 270
    ret = 0
    direction1 = directions[0]
    direction2 = directions[1]
    if "north" == direction1 and "west" in direction2:
        ret = 360
    elif direction1 == "east":
        ret = 90
    elif direction1 == "south":
        ret = 180
    elif direction1 == "west":
        ret = 270
    if direction2 == "west":
        ret += 270
    elif direction2 == "east":
        ret += 90
    if direction2 == "northeast":
        ret += 45
    elif direction2 == "northwest":
        ret += 315
    elif direction2 == "southeast":
        ret += 135
    elif direction2 == "southwest":
        ret += 225
    return ret//2

def plotWindDirection(windDirection):
    data = dict()
    for d in windDirection:
        if d == -1:
            continue
        if d not in data:
            data[d] = 0
        data[d] += 1
    ws = []
    wd = []
    for d in data:
        for s in range(0, data[d]):
            ws.append(data[d])
            wd.append(d)
    axesWindDirection.calm_count = 0    
    axesWindDirection.bar(wd, ws, normed=True, opening=0.8, edgecolor='white')

def readData(fileName):
    reader = csv.reader(open(fileName, newline='\n'), delimiter=';', quotechar='"')
    next(reader, None)
    for row in reader:
        arrayTime.append(row[0][:5])
        arrayTemperature.append(row[1])
        arrayPressure.append(row[3])
        arrayHumidity.append(row[5])
        arrayWindDirection.append(row[6][22:])
        arrayWindDirectionNumbers.append(transformWindDirectionToNumber(row[6][22:]))
        # if row[6][22:] != '' and transformWindDirectionToNumber(row[6][22:]) == -1:
        #     print("!!!!!!" + row[6][22:])
        # print(row[6][22:])
        # print(transformWindDirectionToNumber(row[6][22:]))
        arrayWindSpeed.append(row[7])

readData('moscow.csv')
arrayTime = arrayTime[::-1]

# Transform data to numpy array
time = np.array(arrayTime)
temperature = np.array(arrayTemperature, dtype=np.dtype(float))
pressure = np.array(arrayPressure, dtype=np.dtype(float))
humidity = np.array(arrayHumidity, dtype=np.dtype(float))
windDirectionNumbers = np.array(arrayWindDirectionNumbers, dtype=np.dtype(float))
windSpeed = np.array(arrayWindSpeed, dtype=np.dtype(float))

plotWindDirection(windDirectionNumbers)

axes = []
axes.append(axesTemperature)
axes.append(axesHumidity)
axes.append(axesPressure)

data = []
data.append(temperature)
data.append(pressure)
data.append(humidity)

x = np.linspace(0, len(time), len(time)).T

plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=.25, hspace=.5)
for ax, d in zip(axes, data):
    movePlotAlongXAxis(ax, -0.045)
    plotToAxis(ax, x, d)
    ax.xaxis.set_major_formatter(FuncFormatter(xaxisFormatter))

axesWindSpeed.hist(windSpeed)

plt.show()