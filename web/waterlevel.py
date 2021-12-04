#
# Author: Daniel Rojas
# Date: 12-01-2021
# COMP462 Final Project
#

from multiprocessing import Lock, Queue
import RPi.GPIO as GPIO
import datetime
import time
import csv

#File That Stores Our Data For Current Day
CSV_FILE_PATH = "./data/present_daily_readings.csv"

#Delay Between Readings In Seconds (1 Hour = 3600 Seconds) (10 Min = 600 Seconds)
SLEEP_DELAY = 60

#Water Level Detector ADC Chip Channel (Channels: 0..8)
ADC_CHANNEL = 0

#Maximum Raw Reading
MAX_RAW = 330.0

#Inches Calibration Constant (How Many Inches A Fully Submerged Sensor Will Read)
INCH_CALIBRATION_CONST = 1.4

#Pins for the SPI Interface
SPI_CLK_PIN = 11
SPI_MISO_PIN = 9
SPI_MOSI_PIN = 10
SPI_CS_PIN = 8

#Reads Data From MCP3008 ADC Microchip
def getData():

    #Output Variable
    data = 0

    #GPIO Pins That Control Data Flow
    GPIO.output(SPI_CS_PIN, True)
    GPIO.output(SPI_CLK_PIN, False)
    GPIO.output(SPI_CS_PIN, False)

    #5-Bit Command to Send
    bitComm = (ADC_CHANNEL | 0b11000) << 3

    #We are Iterating Over Five Leftmost Bits and Sending Data Through MOSI By Cycling CLK
    for i in range(5):

        #Checking if Highest Order Bit is Set
        if (bitComm & 0b10000000):
            GPIO.output(SPI_MOSI_PIN, True)
        else:
            GPIO.output(SPI_MOSI_PIN, False)

        #Iterating Over to Next Bit
        bitComm = bitComm << 1

        #Cycling Clock High-Low
        GPIO.output(SPI_CLK_PIN, True)
        GPIO.output(SPI_CLK_PIN, False)

    #We are Reading Data Through MISO One Bit at a Time (1 EMPTY, 1 NULL, 10 ADC)
    for i in range(12):

        #Cycling Clock
        GPIO.output(SPI_CLK_PIN, True)
        GPIO.output(SPI_CLK_PIN, False)

        #Shifting Rightmost Bit to the Left So We Can Read and Store Another
        data = data << 1

        #If MISO Is At High State Set the Bit
        if (GPIO.input(SPI_MISO_PIN)):
            data = data | 0b1

    #Restoring Chip Select to Former State
    GPIO.output(SPI_CS_PIN, True)

    #Remove Null Bit
    data = data >> 1

    return data


#Main Method
def main(queue, lock):

    #Opening Monthly (Last 30 Days) Data From CSV
    csvFile = open(CSV_FILE_PATH, 'a') #w=write, a=append
    csvWriter = csv.writer(csvFile)

    #Wrtiting Headers (We Don't Need To, File Already Has Them)
    #headersRow = ['Water-Level(Inches)', 'Date-Time']
    #csvWriter.writerow(headersRow)

    #Cleanign up and Setting Board Pin Mode
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    #Initializing GPIO Pins
    GPIO.setup(SPI_MOSI_PIN, GPIO.OUT)
    GPIO.setup(SPI_MISO_PIN, GPIO.IN)
    GPIO.setup(SPI_CLK_PIN, GPIO.OUT)
    GPIO.setup(SPI_CS_PIN, GPIO.OUT)

    #Infinite Loop to Read From Sensor
    while True:

        #Receive Data
        rawData = getData()
        percentData = min( (rawData/MAX_RAW)*100, 100.0 )
        inchData = percentData * INCH_CALIBRATION_CONST

        #Print Data to Console
        print("\nRaw Sensor Reading:", rawData)
        print("Percentage Submerged Reading:", percentData)
        print("Inches of Rainfall:", inchData)

        #Writing Data to CSV File
        dataRow = [inchData, str(datetime.datetime.now())]
        csvWriter.writerow(dataRow)

        #We Need to Flush File Changes When Running This Using MultiProcessing
        csvFile.flush()

        #Writing Latest Water-Level Data Plus Date-Time Data to Queue
        lock.acquire()
        try:
            #Removing left-Over Data From Queue
            while not queue.empty():
                queue.get()
            #New Data
            queue.put(dataRow)
        except:
            lock.release()
        finally:
            lock.release()

        #Delay Between Measurements
        time.sleep(SLEEP_DELAY)


#Starts Program at Main Method
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()



