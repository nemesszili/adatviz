# Data source: rp5.ru -> archive

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

cityName = "moscow"

arrayTime = [] #0
arrayTemperature = [] #T1
arrayPressure = [] #P3
arrayHumidity = [] #U5
arrayWindDirection = [] #DD6
arrayWindSpeed = [] #FF7
arrayMinTemp = [] #Tn14
arrayMaxTemp = [] #Tx15
arrayPrecipitation = [] #RRR23

arrayWindDirectionNumbers = []

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from windrose import WindroseAxes

# Create layout
axesTemperature = plt.subplot2grid((3,3),(0,0), colspan=2)
axesPrecipitation = plt.subplot2grid((3,3), (1,0), colspan=2)
axesPressure = plt.subplot2grid((3,3), (2,0), colspan=2)
axesWindSpeed = plt.subplot2grid((3,3), (0,2))

ax = plt.subplot2grid((3,3), (1,2), rowspan=2)
axesWindDirection = WindroseAxes(plt.gcf(), list(ax.get_position().bounds))
plt.gcf().add_axes(axesWindDirection)
plt.gcf().delaxes(ax)

axesTemperature.set_ylabel("Temperature(C)")
# axesTemperature.yaxis.labelpad = -5
axesPrecipitation.set_ylabel("Precipitation(mm)")
axesPressure.set_ylabel("Pressure(mmHg)")
axesPressure.set_xlabel("Time(day.month)")
axesWindSpeed.set_xlabel("Histogram of mean wind speed(m/s)")
axesWindDirection.set_xlabel("Histogram of wind directions")
axesTemperature.set_xlabel("Time(day.month)")
axesPrecipitation.set_xlabel("Time(day.month)")

def plotToAxis(ax, x, y, reversed=True, color=None, setLim=False, legend=None):
    dist = (max(y)-min(y))/5
    if setLim:
    	ax.set_ylim([min(y), max(y)+dist])
    if reversed:
        y = y[::-1]
    if color:
    	ax.plot(x, y, color=color)
    else:
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
        if row[14] == "":
        	arrayMinTemp.append(-999)
        else:	
        	arrayMinTemp.append(row[14])
        if row[15] == "":
        	arrayMaxTemp.append(-999)
        else:	
        	arrayMaxTemp.append(row[15])
        if row[23] == "":
        	arrayPrecipitation.append(-999)
        elif row[23] == "No precipitation":
        	arrayPrecipitation.append(0)
        elif row[23] == "Trace of precipitation":
        	arrayPrecipitation.append(-999)
        else:
        	arrayPrecipitation.append(row[23])
        arrayWindSpeed.append(row[7])

readData(cityName + '.csv')
arrayTime = arrayTime[::-1]

# Transform data to numpy array
time = np.array(arrayTime)
temperature = np.array(arrayTemperature, dtype=np.dtype(float))
pressure = np.array(arrayPressure, dtype=np.dtype(float))
humidity = np.array(arrayHumidity, dtype=np.dtype(float))
windDirectionNumbers = np.array(arrayWindDirectionNumbers, dtype=np.dtype(float))
windSpeed = np.array(arrayWindSpeed, dtype=np.dtype(float))
minTemp = np.array(arrayMinTemp, dtype=np.dtype(float))
maxTemp = np.array(arrayMaxTemp, dtype=np.dtype(float))
precipitation = np.array(arrayPrecipitation, dtype=np.dtype(float))

plotWindDirection(windDirectionNumbers)

x = np.linspace(0, len(time), len(time)).T

plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=.25, hspace=.5)
movePlotAlongXAxis(axesTemperature, -0.045)
plotToAxis(axesTemperature, x, temperature, color="goldenrod")
axesTemperature.xaxis.set_major_formatter(FuncFormatter(xaxisFormatter))

indexPrecipitationValues = precipitation != -999
movePlotAlongXAxis(axesPrecipitation, -0.045)
plotToAxis(axesPrecipitation, x[indexPrecipitationValues], precipitation[indexPrecipitationValues], setLim=True)
axesPrecipitation.xaxis.set_major_formatter(FuncFormatter(xaxisFormatter))

# movePlotAlongXAxis(axesPrecipitation, -0.045)
# plotToAxis(axesPrecipitation, x, humidity)
# axesPrecipitation.xaxis.set_major_formatter(FuncFormatter(xaxisFormatter))

movePlotAlongXAxis(axesPressure, -0.045)
plotToAxis(axesPressure, x, pressure)
axesPressure.xaxis.set_major_formatter(FuncFormatter(xaxisFormatter))

axesWindSpeed.hist(windSpeed)

indexMinValues = minTemp != -999
plotToAxis(axesTemperature, x[indexMinValues], minTemp[indexMinValues], color="blue")

indexMaxValues = maxTemp != -999
plotToAxis(axesTemperature, x[indexMaxValues], maxTemp[indexMaxValues], color="orangered")

axesTemperature.legend(['Mean Temp', 'Min Temp', 'Max Temp'])

plt.gcf().suptitle("Weather statistics for " + cityName.title())

plt.show()