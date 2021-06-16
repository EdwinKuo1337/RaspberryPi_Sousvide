import RPi.GPIO as GPIO
import os
from time import sleep
from http.server import BaseHTTPRequestHandler, HTTPServer
import _thread

host_name = '192.168.39.182'  # Change this to your Raspberry Pi IP address
host_port = 8000

cur_temp=0
tar_temp=0
timer=-2
def switch(threadname,delay,SWITCH_PIN):
    global cur_temp
    global tar_temp
    global timer
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(SWITCH_PIN,GPIO.OUT)
    while True:
        if int(timer) == -2 or int(timer) >= 0:
            if float(cur_temp) < float(tar_temp)-2:
            #print("ON")
                GPIO.output(SWITCH_PIN,GPIO.HIGH)
            else:
            #print("OFF")
                GPIO.output(SWITCH_PIN,GPIO.LOW)
        else:
            GPIO.output(SWITCH_PIN,GPIO.LOW)

def Timer(threadname,delay):
    global timer
    #print(int(timer))
    while True:
        #print(int(timer))
        if int(timer) >= 0:
            sleep(60)
            timer = str(int(timer) - 1)
        

def temp(threadname,delay):
    global cur_temp
    import time
    from w1thermsensor import W1ThermSensor
    sensor = W1ThermSensor()
    while True:
        cur_temp = sensor.get_temperature()
        #print("The temperature is %s celsius" % cur_temp)
        time.sleep(3)
    
    
class MyServer(BaseHTTPRequestHandler):
    """ A special implementation of BaseHTTPRequestHander for reading data from
        and control GPIO of a Raspberry Pi
    """

    def do_HEAD(self):
        """ do_HEAD() can be tested use curl command
            'curl -I http://server-ip-address:port'
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        global cur_temp
        global tar_temp
        global timer
        """ do_GET() can be tested using curl command
            'curl http://server-ip-address:port'
        """
        html = '''
           <meta http-equiv="refresh" content="3" />
           <html>
           <body style="width:960px; margin: 20px auto;">
           <h1 style="font-size:3vw">Sous vide Control Center</h1>
           <p style="font-size:3vw">Timer: {}</p>
           <p style="font-size:3vw">Current water temperature is {}</p>
           <p style="font-size:3vw">Target water temperature is {}</p>
           <form action="/" method="POST">
                Enter goal temperature :
                <input type="text" name="temp">
            </form>
            <form action="/" method="POST">
                Enter timer in minutes :
                <input type="text" name="min">
            </form>
            <p style="font-size:3vw"><a href="https://www.seriouseats.com/food-lab-complete-guide-to-sous-vide-steak">Sous Vide Steak Guide - by J. Kenji Lopez-Alt</a><p>
            <p style="font-size:3vw"><a href="https://www.seriouseats.com/the-food-lab-complete-guide-to-sous-vide-chicken-breast">The Food Lab's Complete Guide to Sous Vide Chicken Breast - by J. Kenji Lopez-Alt</a><p>
            
           </body>
           </html>
        '''
        if int(timer) >= 0:
            tm = str(timer)+' minutes left'
        elif int(timer) == -1:
            tm = 'Times\'s up! The fire is off'
        elif int(timer) == -2:
            tm = 'Not set a timer yet!'
        #tm = timer
        c_temp = cur_temp
        t_temp = tar_temp
        self.do_HEAD()
        self.wfile.write(html.format(tm, c_temp, t_temp).encode("utf-8"))
        #self.wfile.write(html.format(t_temp).encode("utf-8"))

    def do_POST(self):
        """ do_POST() can be tested using curl command
            'curl -d "submit=On" http://server-ip-address:port'
        """
        global tar_temp
        global timer
        content_length = int(self.headers['Content-Length'])  # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8")  # Get the data
        #print(post_data)
        post_data_x = post_data.split("=")[1]  # Only keep the value
        if post_data.split("=")[0] == 'temp':
            tar_temp = post_data_x
        if post_data.split("=")[0] == 'min':
            timer = post_data_x
        
        # GPIO setup
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setwarnings(False)
        #GPIO.setup(18, GPIO.OUT)

        #if post_data == 'On':
            #GPIO.output(18, GPIO.HIGH)
        #else:
            #GPIO.output(18, GPIO.LOW)
        #print("LED is {}".format(post_data))
        self._redirect('/')  # Redirect back to the root url


if __name__ == '__main__':
    #global cur_temp
    #global tar_temp
    _thread.start_new_thread(Timer,("Thread-3",1,))
    _thread.start_new_thread(temp,("Thread-1",3,))
    _thread.start_new_thread(switch,("Thread-2",2,11,))
    http_server = HTTPServer((host_name, host_port), MyServer)
    #print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
