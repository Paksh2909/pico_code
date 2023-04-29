from hx711.hx711_gpio import HX711
from machine import Pin
import time
import urequests
import ujson
import network
import socket
import gc


url = "Insert Backend URL here"
pin_OUT = Pin(2, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(4, Pin.OUT)
hx711 = HX711(pin_SCK, pin_OUT, gain=128)

class Weight:

    def __init__(self):
        
        self.start_time = 0
        self.end_time = 0
        self.weight_changed = False
        self.duration = 0
        
        self.start_weight = 0
        self.upload_weight = 0
        self.started = False
        
        self.cat_name = "Haybe"
        self.user = "testUser"
        
        self.tare()
        
    def tare(self):
        hx711.tare()



    def detemine_poop_or_pee(self, duration):
        # we need to do some data collect to determine the time thresholds
        if duration > 15:
            return "Poop"
        elif 5 < duration <= 15:
            return "Pee"
        else:
            return "Unknown - for debugging purpose"

    def get_weight(self):
        
        while True:
            value = hx711.read_average(10)
            weight = int((0.0022 * value) - 607 + 14)
            print("Weight :", weight)
            
            
            if self.start_weight < 10 and weight > 100:
                print("inside 1st")
                self.started = True
                self.start_weight = weight
                self.start_time = time.time()
            
            if weight > self.start_weight and self.started:
                self.start_weight = weight
            
            if weight < 10 and self.start_weight > 100:
                print("inside 2nd")
                self.upload_weight = self.start_weight
                self.start_weight = weight
                self.end_time = time.time()
                self.started = False
            
            if self.start_time != 0 and self.end_time != 0:
                print("inside 3rd")
                self.duration = self.end_time - self.start_time
                self.start_time = 0
                self.end_time = 0
            
            
            print("Duration:", self.duration)
            
            print()
            
            
            if self.duration != 0:
                local_time = time.localtime()
                timestamp =  str(local_time[0]) + "-" + str(local_time[1]) + "-" + str(local_time[2]) + "," + str(local_time[3]) + ":" + str(local_time[4]) + ":" + str(local_time[5])
                
                event_type = self.detemine_poop_or_pee(self.duration)
            
                weight_url = url+"/weight?timestamp="+timestamp+"&catName="+self.cat_name+"&value="+str(self.upload_weight)+"&userID="+self.user
                usage_url = url+"/usage?timestamp="+timestamp+"&catName="+self.cat_name+"&usageType="+event_type+"&userID="+self.user
                #print("Weight URL: ", weight_url)
                #print("Usage URL: ", usage_url)
                
                notification_body = ujson.dumps({
                    "title": "Smart Litter",
                    "subtitle": "Usage Alert",
                    "bodyMessage": self.cat_name+"just"+event_type+"ed!!"
                })
                
                print(notification_body)
                
                try:
                    weight_response = urequests.get(weight_url)
                    time.sleep(2)
                    usage_response = urequests.get(usage_url)
                    time.sleep(2)
                    notify_response = urequests.post(url+"/notify", headers = {'content-type': 'application/json'}, data = notification_body)
                    time.sleep(2)
                    print("Weight: ", weight_response.status_code)
                    print("Usage: ", usage_response.status_code)
                    #print("Notify: ", notify_response.body)
                    
                except Exception as e:
                    print(e) 
                
                weight_response.close()
                usage_response.close()
                notify_response.close()
                self.duration = 0
            
            gc.collect()
            time.sleep(2)

if __name__ == "__main__":
    scale = Weight()
    scale.get_weight()
