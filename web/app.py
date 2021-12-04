#
# Author: Daniel Rojas
# Date: 12-01-2021
# COMP462 Final Project
#

from flask import Flask, Markup, render_template, request
from multiprocessing import Process, Lock, Queue
import csv
from waterlevel import main, SLEEP_DELAY

#Necessary since we need a shared queue to send/receive data between processes concurrently
lock = Lock()
queue = Queue()

#Initializes Multiprocessing With Process that Will Read Live Measurements
child = Process(target=main, args=(queue,lock))
child.start()

#Global Variable Responsible For Storing the Last Fetched Live Data
liveData = []

#Opens Daily (Today's) Data From CSV
DAILY_FILE_PATH = "./data/present_daily_readings.csv"
dailyFile = open(DAILY_FILE_PATH)
dailyReader = csv.reader(dailyFile)
next(dailyReader) #Ignores Headers

#Responsible for holding all values for daily data
dailyData = []

#Extracting Data Values
for row in dailyReader:
    dailyData.append(row)

#Opening Monthly (Last 30 Days) Data From CSV
CSV_FILE_PATH = "./data/avg_hourly_per_day.csv"
csvFile = open(CSV_FILE_PATH)
csvReader = csv.reader(csvFile)

#Extracting Headers
headersRow = next(csvReader)

#Extracting Data Values
dataRows = []
for row in csvReader:
    dataRows.append(row)

#Closing since we don't need it anymore (New Values Come From Other Python Script)
csvFile.close()

#Setting Up Data For Chart & Graph
xLabels = []
yValues = []
for row in dataRows:
    yValues.append(row[0])
    xLabels.append(row[1])

app = Flask(__name__)

#Home Page
@app.route("/")
def home():
    return render_template('home.html')

#Page That Shows Chart of Monthly Data
@app.route("/chart")
def chart():
    return render_template('chart.html', labels=xLabels, values=yValues)

#Page That Shows Graph of Monthly Data
@app.route("/graph")
def graph():
    return render_template('graph.html', labels=xLabels, values=yValues)

#Page That Shows Most Recent Reading From The Sensor
@app.route('/live')
def live():

    global liveData

    lock.acquire()
    tempData = liveData #Backup In Case of Exception
    try:
        #Necessary or server will freeze untill queue gets something
        if not queue.empty():
            liveData = queue.get()
    except:
        liveData = tempData #Restoring Old Data
        lock.release()
    finally:
        lock.release()

    return render_template('live.html', liveData=liveData, delay=SLEEP_DELAY)


#
# THERE IS A BETTER WAY TO IMPLEMENT THE METHOD BELOW SO WE DON'T HAVE TO
# RE-READ THE SAME FILE OVER AND OVER AGAIN. WE WOULD READ ONCE BEFORE THIS
# METHOD IS CALLED(WHERE GLOBALS ARE DECLARED) AND THEN JUST HAVE THE OTHER
# PROCESS SEND US ANY NEW DATA THROUGH A NEW QUEUE. THIS WAY WE WOULD ONLY
# NEED TO APPEND HOWEVER MANY VALUES THERE ARE IN THE QUEUE, SAVING TIME
#

#Page That Displays Current Day's Data Collected As of That Moment As A Table
@app.route("/today")
def today():

    #We Need To Re-Open File To See Latest Changes
    dailyFile = open(DAILY_FILE_PATH)
    dailyReader = csv.reader(dailyFile)
    next(dailyReader) #Ignores Headers
    dailyData = []

    #Ignore Headers
    next(dailyReader)

    #Extracting Latest Un-Read Data Values and Appending to Exisitng Data
    for row in dailyReader:
        dailyData.append(row)

    return render_template('today.html', dailyData=dailyData)

#Initalizes Flask Web Server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
