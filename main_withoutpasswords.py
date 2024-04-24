# Complete project details: https://RandomNerdTutorials.com/micropython-send-emails-esp32-esp826/
# Micropython lib to send emails: https://github.com/shawwwn/uMail
import umail
import network
import machine
import network
import time
import urequests
import utime

# Define the pin to use as input (change as needed)
input_pin = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Define LED pin
led_pin = 2  # GPIO 2 (built-in LED on most ESP32 boards)

# Configure LED pin as output
led = machine.Pin(led_pin, machine.Pin.OUT)

# Email details
sender_email = 'ramlavipushnotification@gmail.com'
sender_name = 'Water meter' #sender name
sender_app_password = '' # add gmail app password and place it here
recipient_email = ''
email_subject = 'Test Email'
email_content = 'Test content'

# Wifi details
ssid = ''
password = ''

get_hour_seconds_counter = 36000
current_hour = 0
prev_hour = 0
counters = [0] * 24

# boolean for sending summary once a day
summary_send_enable = False

# boolean for enabling alert send
alert_send_enable = True

# hour stamp of the last alert (to prevent two alerts in the same hour)
alert_hour_stamp = 0

# Connect to Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("Wi-Fi connected!")
    print("IP address:", wlan.ifconfig()[0])

def send_mail(sender_email, sender_app_password, recipient_email, sender_name, email_subject, email_content):
    # Send the email
    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True) # Gmail's SSL port
    smtp.login(sender_email, sender_app_password)
    smtp.to(recipient_email)
    smtp.write("From:" + sender_name + "<"+ sender_email+">\n")
    smtp.write("Subject:" + email_subject + "\n")
    smtp.write(email_content)
    smtp.send()
    smtp.quit()

def get_current_hour():
    # URL of the API providing time information
    api_url = "http://worldtimeapi.org/api/timezone/Asia/Jerusalem"
    
    try:
        # Send a GET request to the API
        response = urequests.get(api_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Extract the hour from the time data
            hour = int(data['datetime'][11:13])
            
            # Return the hour (0-23)
            return hour
        
        else:
            print("Failed to fetch time data. Status code:", response.status_code)
            return None
    
    except Exception as e:
        print("An error occurred:", e)
        return None

def set_time_from_api():
    try:
        # URL of the API providing time information
        api_url = "http://worldtimeapi.org/api/timezone/Asia/Jerusalem"
        
        # Send a GET request to the API
        response = urequests.get(api_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Extract year, month, day, hour, minute, and second from the time data
            year, month, day = map(int, data['datetime'][:10].split('-'))
            hour, minute, second = map(int, data['datetime'][11:19].split(':'))
            
            # Set the RTC of the ESP32
            rtc = machine.RTC()
            rtc.datetime((year, month, day, 0, hour, minute, second, 0))
            
            print("RTC set successfully!")
            print("Current time (UTC):", utime.localtime())
        else:
            print("Failed to fetch time data. Status code:", response.status_code)
    
    except Exception as e:
        print("An error occurred:", e)
# Initialize X
counter = 0

# Define a debounce delay in milliseconds
debounce_delay_ms = 250  # Adjust as needed

# Define the last touch time (initially set to 0)
last_touch_time = 0

# Define the interrupt handler function
def increment_counter(pin):
    global counter, last_touch_time
    current_time = utime.ticks_ms()
    
    # Check if enough time has passed since the last touch
    if utime.ticks_diff(current_time, last_touch_time) > debounce_delay_ms:
        if pin.value() == 1:
            counter += 1
            last_touch_time = current_time  # Update last touch time

# Attach interrupt handler to the rising edge of the input pin
input_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=increment_counter)

def summary_email():
    global counters
    global sender_email
    global sender_name
    global sender_app_password
    global recipient_email
    email_subject = 'Water meter summary'
    local_email_content = ''
    for i in range(len(counters)):
        local_email_content += f'{i} - {counters[i]} liters\n'
        #print(f'{i}: {counters[i]}\n')
    print(local_email_content)
    send_mail(sender_email, sender_app_password, recipient_email, sender_name, email_subject, local_email_content)

def check_alert_conditions():
    global counters
    global current_hour
    
    leaks_array = [5, # 0
                    2, # 1
                    2, # 2
                    2, # 3
                    2, # 4
                    2, # 5
                    2000, # 6
                    2000, # 7
                    2000, # 8
                    2000, # 9
                    2000, # 10
                    2000, # 11
                    2000, # 12
                    2000, # 13
                    2000, # 14
                    2000, # 15
                    2000, # 16
                    2000, # 17
                    2000, # 18
                    2000, # 19
                    2000, # 20
                    2000, # 21
                    2000, # 22
                    2000] # 23
    print(f'current hour - {current_hour}, leaks - {leaks_array[current_hour]}, counters - {counters[current_hour]}')
    if leaks_array[current_hour] < counters[current_hour]:
        return True
    else:
        return False

while True:
    print('start main')
    # Check Wi-Fi connection
    if network.WLAN(network.STA_IF).isconnected():
        # Wi-Fi connected, turn on LED2
        led.on()
    else:
        # Wi-Fi not connected, turn off LED2 and reconnect
        led.off()
        connect_to_wifi(ssid, password)
    
    # set the localtime
    if get_hour_seconds_counter == 36000: # set clock every 10 hours
        get_hour_seconds_counter = 0
        print('set_time_from_api()')
        set_time_from_api()
    current_hour = utime.localtime()[3] # get_current_hour()
    if current_hour is not None:
        print(f'Current hour is: {current_hour}')
    
    get_hour_seconds_counter += 1
    print(f'get_hour_seconds_counter: {get_hour_seconds_counter}')
    
    # fill the water capacity of the previous hour
    if prev_hour != current_hour:
        counters[prev_hour] = counter
        prev_hour = current_hour
        counter = 0
        print(f'fill water capacity for {prev_hour}')
        
    print(f'counter: {counter}')
    print(f'counters: {counters}')
    
    # send daily summary
    if current_hour == 21:
        if summary_send_enable == True:
            summary_email() # send daily summary
            summary_send_enable = False # prevent daily summary send again until 21:00 at the next day
            print(f'daily summary was sent')
    else: # current_hour != 21
        summary_send_enable = True
        print(f'daily summary was not sent')
    
    # allow only one alert every hour
    if alert_hour_stamp != current_hour:
        alert_send_enable = True
    
    # check conditions for alert and send e-mail if there is a leak
    if check_alert_conditions():
        if alert_send_enable == True:
            alert_hour_stamp = current_hour
            send_mail(sender_email, sender_app_password, recipient_email, sender_name, 'WATER LEAK', 'WATER LEAK!')
        alert_send_enable = False
    
    # Delay for a short period (e.g., 1 second)
    time.sleep(1)

