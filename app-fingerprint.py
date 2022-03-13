from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request

import os
import serial
import pygame
import sys
import threading
import time
from gpiozero import Button, OutputDevice


############ Fingerprint code start
import board
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
############ Fingerprint code end


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
PACKAGE_ADDED_TEXT = 'Package detected'
WEIGHT_DIFF_THRESHOLD = 100
OK_RESPONSE_TEXT = 'OK'
ALARM_FILE_NAME = 'alarm.wav'

#globals
alarm_on = False        # True triggers alarm actions
activated = True        # True when package monitoring is active, false when deactivated by button or text.
package_on = False      # True when package is on scale
matched_finger = False     # True when a recognized fingerprint
current_weight = 0.0
app = Flask(__name__)

############ Fingerprint code start
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
############ Fingerprint code end


# open the serial port for reading the scale
ser = serial.Serial('/dev/ttyACM0', 57600, timeout=1)

#these are the GPIO pins that are used to turn on each of the lights

YELLOW_LIGHT = 26
GREEN_LIGHT = 20
RED_LIGHT = 21
BUTTON = 2

# using gpiozero 
yellow_light = OutputDevice(YELLOW_LIGHT, active_high=True, initial_value=False)
green_light = OutputDevice(GREEN_LIGHT, active_high=True, initial_value=False)
red_light = OutputDevice(RED_LIGHT, active_high=True, initial_value=False)
button = Button(2)

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
    return '<h1>Welcome</h1><br/>Current weight: <b>' + str(current_weight) + '</b><br/>Alarm on: ' + str(alarm_on) + '</b><br/>Package On: ' + str(package_on) + '</b><br/>Activated: ' + str(activated)

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
    time.sleep(.37) # length of alarm wave file

def turn_off_alarm():
    print ('Turning off alarm...')
    global alarm_on
    global activated
    global package_on
    
    alarm_on = False
    package_on = False
    activated = False

def set_sms_url(url):
    if ACCOUNT_SID == '' or AUTH_TOKEN == '':
        print('Cannot set url, no configuration')
    else:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        incoming_phone_number = client.incoming_phone_numbers(TWILIO_PN_SID).fetch()
        incoming_phone_number.update(sms_url=url)

def send_sms(message_text):
    if ACCOUNT_SID == '' or AUTH_TOKEN == '':
        print('Cannot send message, no message configuration')
    else:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(body=message_text, from_=TWILIO_PHONE_NUMBER, to=USER_PHONE_NUMBER)
        print('Message sent: ' + message.sid)


def read_weight(ser):

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

    if activated:
        if new_weight - current_weight > WEIGHT_DIFF_THRESHOLD:
            package_on = True
            send_sms(PACKAGE_ADDED_TEXT)

        if current_weight - new_weight > WEIGHT_DIFF_THRESHOLD:
            send_sms(WEIGHT_DECREASED_TEXT) 
            alarm_on = True
            package_on = False

    current_weight = new_weight

def set_lights():
    global alarm_on
    global package_on
    global activated

    if not activated: #  turn on yellow only
        yellow_light.on()
        green_light.off()
        red_light.off()

    elif alarm_on: # flash red
        yellow_light.off()
        green_light.off()
        red_light.toggle()

    elif package_on: # turn on red light only
        yellow_light.off()
        green_light.off()
        red_light.on()

    else: # turn on green only -- ready for package
        yellow_light.off()
        green_light.on()
        red_light.off()

def toggle_activated_state():
    global activated
    global alarm_on 
    global package_on

    if not activated:
        activated = True    # activate program
        alarm_on  = False   # reset alarm if it was on
        package_on = False  # reset package detection 

    else:
        activated = False   # deactivate everything
        alarm_on = False
        package_on = False


def get_fingerprint():
    
    global matched_finger
    
    while True:
        # Get a finger print image, template it, and see if it matched
        # matched_finger needs to be cleared before looking for another print
            
        if matched_finger == False:
                
            while finger.get_image() != adafruit_fingerprint.OK:
                pass
        
            if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                matched_finger = False
                
            if finger.finger_search() != adafruit_fingerprint.OK:
                matched_finger = False
        
            if finger.finger_id > 0:
                matched_finger = True
                finger.set_led(finger.finger_id, 3) # 3 is steady on
                time.sleep(1)
                finger.set_led(7, 3) # turn white


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
    #flaskThread.setDaemon(True)
    flaskThread.daemon = True
    flaskThread.start()

    button.when_pressed = toggle_activated_state
    
    finger.set_led(7,3) # turn on white
    fingerThread = threading.Thread(target=get_fingerprint)
    fingerThread.daemon = True
    fingerThread.start()
    
    try:
        while True:
              
            if matched_finger == True:
                toggle_activated_state()
                matched_finger = False
            
            print('wt: ' + str(current_weight) + ' | act: ' + str(activated) + ' | package_on: ' + str(package_on) + ' | alarm_on: ' + str(alarm_on) + ' | fp: ' + str(finger.finger_id) )
            set_lights()
            check_sensor()
            check_alarm()
            time.sleep(.1) # to catch keyboard interrupt
        

    except (KeyboardInterrupt):
        print('Exiting')
        flaskThread.join()
        fingerThread.join()
        pygame.mixer.quit()
        red_light.off()
        yellow_light.off()
        green_light.off()
        finger.set_led(1,4) ## fingerprint led off. 4 = off   
        exit(0)
