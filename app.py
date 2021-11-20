from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler

import os
import serial
import pygame

def get_env_var(key):
    if key in os.environ:
        return os.environ[key]
    else:
        return ''
    
#constants
ACCOUNT_SID = get_env_var('TWILIO_ACCOUNT_SID') #os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = get_env_var('TWILIO_AUTH_TOKEN') #os.environ['TWILIO_AUTH_TOKEN']
TWILIO_PHONE_NUMBER = get_env_var('TWILIO_PHONE_NUMBER') #os.environ['TWILIO_PHONE_NUMBER']
USER_PHONE_NUMBER = get_env_var('OWNER_PHONE_NUMBER') #os.environ['OWNER_PHONE_NUMBER']
WEIGHT_DECREASED_TEXT = 'Weight decreased, alarm on, reply with OK to turn off alarm'
WEIGHT_DIFF_THRESHOLD = 100
OK_RESPONSE_TEXT = 'OK'
ALARM_FILE_NAME = 'alarm.wav'

#globals
alarm_on = False
current_weight = 0.0
app = Flask(__name__)
ser = serial.Serial('/dev/ttyACM0', 57600, timeout=1)

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
    return '<h1>Welcome</h1><br/>Current weight: <b>' + str(current_weight) + '</b><br/>Alarm on: ' + str(alarm_on)

################### functions ###############

def check_alarm():
    #print('beep beep') 
    global alarm_on
    if alarm_on == True:
        sound_alarm()

def sound_alarm():
    pygame.mixer.music.play()

def turn_off_alarm():
    print ('Turning off alarm...')
    global alarm_on
    alarm_on = False

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
    global ser
    
    new_weight = float(read_weight(ser))
    print(new_weight)
    if current_weight - new_weight > WEIGHT_DIFF_THRESHOLD:
        send_sms() 
        alarm_on = True
    current_weight = new_weight
        
#### main program ####
if __name__ == '__main__':

    pygame.mixer.init()
    pygame.mixer.music.load(ALARM_FILE_NAME)

    try:
        #start scheduler
        sched = BackgroundScheduler(daemon=True)
        #check weight every 3 seconds
        sched.add_job(check_sensor, 'interval', seconds=3)
        # check if alarm should be on, current alarm file is 11 sec, so check every 12
        sched.add_job(check_alarm, 'interval', seconds=12)
        sched.start()

   
    
        #start web server
        app.run(debug=False, port=5000, host='0.0.0.0')

    except KeyboardInterrupt:
        print('Exiting')
        sched.shutdown()
        pygame.mixer.quit()



