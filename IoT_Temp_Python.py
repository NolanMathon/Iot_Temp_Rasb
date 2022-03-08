import serial, time, datetime
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

cooldown_button = datetime.timedelta(seconds=5)
last_temp_button = datetime.datetime.now() - cooldown_button


def button_callback(channel):
    global last_temp_button
    if last_temp_button + cooldown_button <= datetime.datetime.now():
        get_temp()
        last_temp_button = datetime.datetime.now()


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


def get_capteur(string):
    return int(string[1:2])


def is_good_temp(string):
    if string[:1] != 'C':
        return -1

    if string[-3] != 'T':
        return -1

    if '|' not in string:
        return -1

    temp = float(string[2:string.index('|')])
    validator = float(string[string.index('|') + 1:-3])
    validator = round(validator / 2, 2)

    if validator == temp:
        return temp

    return -1


def get_temp():
    ser.write("CGetTemp|T".encode('utf-8'))
    line = ser.readline()
    if line:
        string = line.decode()
        temp = is_good_temp(string)
        if temp != -1:
            capteur = get_capteur(string)
            client.publish('capteurs/' + str(capteur) + "/temperature", payload=temp, qos=0, retain=False)
            print(temp)
        else:
            get_temp()


GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(10, GPIO.IN,
           pull_up_down=GPIO.PUD_DOWN)  # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.add_event_detect(10, GPIO.RISING, callback=button_callback)  # Setup event on pin 10 rising edge

# Connect to serial
ser = serial.Serial('/dev/ttyUSB0', 9600)

# Connect to MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.connect("broker.emqx.io", 1883, 60)

time.sleep(2)

cooldown = datetime.timedelta(seconds=10)
last_temp = datetime.datetime.now() - cooldown

# Every 2 minutes
while True:
    if last_temp + cooldown <= datetime.datetime.now():
        get_temp()
        last_temp = datetime.datetime.now()

ser.close()