# RIMM: Rainfall-Inches-Measuring-Machine
## Author: Daniel Rojas

### Hardware Pre-Requisites:
- Raspberry Pi 3B+ Computer (Or Any Other SPI Capable RPi)
- MCP3008 Analog-to-Digital Converter SPI Chip
- ELEEGO Water Level Sensor
- Wiring Cables
- Whatever Rain Gauge Container You Choose

### Software Pre-Requisites:
- RPi Python Library: Flask, `pip3 install Flask`
- You must Connect RPi and Sensor Via a SPI Connection

### How To Run:

1- Copy “web” folder over to your Raspberry Pi

2- Navigate to “web” folder within Raspberry Pi and run one of the two following commands:
`flask run` OR `python3 app.py`

3- Using a web browser within your Raspberry Pi, type in the following address: [localhost:5000](localhost:5000)

 (NOTE: Delay between measurements is 60 seconds, but it can be changed simply by updating SLEEP_DELAY in the 'waterlevel' python scirpt. You must rrstart the server for it to take effect)

### STOP SERVER PROCESS:
While the server is running, navigate to the terminal window in which the server is running. Hit 'CTRL + C' within the terminal window once, if it does not do anything, press the keys once more until it kills the process.
