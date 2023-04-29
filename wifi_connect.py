import network
import socket
from time import sleep
import machine


class WifiConnect:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
    
    def connect(self):
        #Connect to WLAN
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.ssid, self.password)
        while wlan.isconnected() == False:
            print('Waiting for connection...')
            sleep(1)
        print(wlan.ifconfig())


# if __name__ == "__main__":
#     
#     wifi = WifiConnect("SSID", "Password")
# 
#     try:
#         wifi.connect()
#     except KeyboardInterrupt:
#         machine.reset()
