from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request

import os
import serial
import pygame
import sys
import threading
import time
##### import RPi.GPIO as GPIO
##### GPIO.setmode(GPIO.BCM)


def get_env_var(key):
    if key in os.environ:
        return os.environ[key]
    else:
        return ''
    
#constants
ACCOUNT_SID = get_env_var('TWILIO_ACCOUNT_SID') #os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = get_env_var('TWILIO_AUTH_TOKEN') #os.environ['TWILIO_AUTH_TOKEN']
TWILIO_PHONE_NUMBER = get_env_var('TWILIO_PHONE_NUMBER') #os.environ['TWILIO_PHONE_NUMBER']
TWILIO_PN_SID = 'PN68a20eb7b497b1ea22d13d1dd5936eea'
TWILIO_DEFAULT_URL = 'https://demo.twilio.com/welcome/sms/reply/'
USER_PHONE_NUMBER = get_env_var('OWNER_PHONE_NUMBER') #os.environ['OWNER_PHONE_NUMBER']
WEIGHT_DECREASED_TEXT = 'Weight decreased, alarm on, reply with OK to turn off alarm'
WEIGHT_DIFF_THRESHOLD = 100
OK_RESPONSE_TEXT = 'OK'
ALARM_FILE_NAME = 'alarm.wav'


#globals
alarm_on = False        # True triggers alarm actions
scale_connected = True  # True when scale/sensor is connected
activated = True        # True when package monitoring is active, false when deactivated by button or text.
package_on = False      # True when package is on scale
current_weight = 0.0
app = Flask(__name__)

#if the serial port cannot be opened, assume the scale is not connected

try:
    ser = serial.Serial('/dev/ttyACM0', 57600, timeout=1)
except serial.SerialException as e:
    print("Cannot open serial port.....running in stub mode")
    scale_connected = False


#these are the GPIO pins that are used to turn on each of the lights

YELLOW_LIGHT = 26
GREEN_LIGHT = 20
RED_LIGHT = 21
BUTTON = 2

##### GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
##### GPIO.setup(YELLOW_LIGHT, GPIO.OUT)
##### GPIO.setup(GREEN_LIGHT, GPIO.OUT)
##### GPIO.setup(RED_LIGHT, GPIO.OUT)




### IF using GPIOZero instead
####yellow_light = OutputDevice(YELLOW_LIGHT_PIN, active_high=True, initial_value=False)
####green_light = OutputDevice(GREEN_LIGHT_PIN, active_high=True, initial_value=False)
####red_light = OutputDevice(RED_LIGHT_PIN, active_high=True, initial_value=False)
####button = Button(2)

# You can turn these lights off and on using xxx_light.on() and xxx_light.off()


#################### webhooks ################
@app.route('/message', methods=['POST'])
def read_reply_message():
    
    if request.method == 'POST':
        msg_text = request.form.get('Body')
        from_number = request.form.get('From')
        
        #here we can add other responses
        if from_number == USER_PHONE_NUMBER and msg_text == OK_RESPONSE_TEXT:
            turn_off_alarm()
            resp = MessagingResponse()
            resp.message('Alarm turned off')
            return str(resp)
    return 'UNKNOWN'

@app.route('/', methods=['GET'])
def index():
    return '<h1>Welcome</h1><br/>Current weight: <b>' + str(current_weight) + '</b><br/>Alarm on: ' + str(alarm_on) + '</b><br/>Package On: ' + str(package_on) + '</b><br/>Activated: ' + str(activated) + '</b><br/>Scale Connected: ' + str(scale_connected)

################### functions ###############

def run_web_server():
    global app
    app.run(debug=False, port=5000, host='0.0.0.0', use_reloader=False)

def check_alarm():
    #print('beep beep') 
    global alarm_on
    global activated
    if alarm_on and activated:
        sound_alarm()

def sound_alarm():
    pygame.mixer.music.play()

def turn_off_alarm():
    print ('Turning off alarm...')
    global alarm_on
    alarm_on = False

def set_sms_url(url):
    if ACCOUNT_SID == '' or AUTH_TOKEN == '':
        print('Cannot set url, no configuration')
    else:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        incoming_phone_number = client.incoming_phone_numbers(TWILIO_PN_SID).fetch()
        incoming_phone_number.update(sms_url=url)

def send_sms():
    if ACCOUNT_SID == '' or AUTH_TOKEN == '':
        print('Cannot send message, no message configuration')
    else:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(body=WEIGHT_DECREASED_TEXT, from_=TWILIO_PHONE_NUMBER, to=USER_PHONE_NUMBER)
        print('Message sent: ' + message.sid)


def read_weight(ser):
    print('Reading weight')
    ser.flush()
    ser.write(b"9")
    
    weight = ser.readline().decode('utf-8').rstrip()
    return(weight)

def check_sensor():
    global alarm_on
    global current_weight
    global activated
    global ser
    global package_on
    
    try:
        new_weight = float(read_weight(ser))
    except:
        new_weight = current_weight
    print(new_weight)
    if new_weight - current_weight > WEIGHT_DIFF_THRESHOLD:
        package_on = True

    if current_weight - new_weight > WEIGHT_DIFF_THRESHOLD:
        send_sms() 
        alarm_on = True
        package_on = False

    current_weight = new_weight


def set_lights():
    global alarm_on
    global package_on
    global activated

    if package_on: # turn on red light only
  #      GPIO.output(YELLOW_LIGHT, False)
  #      GPIO.output(GREEN_LIGHT, False)
  #      GPIO.output(RED_LIGHT, True)
        print ("y g R")

    elif not activated: #  turn on yellow only
#        GPIO.output(YELLOW_LIGHT, True)
#        GPIO.output(GREEN_LIGHT, False)
#        GPIO.output(RED_LIGHT, False)
        print ("Y g r")

    elif alarm_on: # flash red

 #       GPIO.output(YELLOW_LIGHT, False)
 #       GPIO.output(GREEN_LIGHT, False)
 #       GPIO.output(RED_LIGHT, not GPIO.input(RED_LIGHT))
        print ("y g RRRR")

    else: # turn on green only -- ready for package
 #       GPIO.output(YELLOW_LIGHT, False)
 #       GPIO.output(GREEN_LIGHT, True)
 #       GPIO.output(RED_LIGHT, False)
        print ("y G r")


#this is for the case when a scale is not connected. 
def stub_sensor():
    global alarm_on
    x = input("Trigger Alarm (y/n)? ")
    if x == "y":
        alarm_on = True
        print("ALARM ON")
    else:
        alarm_on = False
        print("ALARM OFF")
        
#### main program ####
if __name__ == '__main__':

    #update twilio sms url if necessary
    if len(sys.argv) > 1:
        new_url = sys.argv[1]
        set_sms_url(new_url)

    #load alarm file
    pygame.mixer.init()
    pygame.mixer.music.load(ALARM_FILE_NAME)

    flaskThread = threading.Thread(target=run_web_server)
    flaskThread.setDaemon(True)
    flaskThread.start()

    try:

        while True:

            # when the button is pressed, the pin input is false

  #          if GPIO.input(BUTTON) == False:     
  #              activated = not activated              # toggles the activate state

            if scale_connected:
                check_sensor()
            else:
                stub_sensor()

            check_alarm()
            set_lights()

            # TODO figure out the optimal interval
            time.sleep(.37) 

    except KeyboardInterrupt:
        print('Exiting')
        pygame.mixer.quit()
        exit(0)
