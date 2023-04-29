from weight import Weight
from wifi_connect import WifiConnect
from access_point import AccessPoint
import time

class FinalScript:
    
    def __init__(self):
        self.access_point = AccessPoint()
        self.wifi = WifiConnect(None, None)
        self.weight_scale = Weight()

if __name__ == "__main__":
    
    time.sleep(5)
    
    run = FinalScript()
    
    while True:
        
        if run.access_point.home_pass is None or run.access_point.home_ssid is None:
            run.access_point.turn_on_ap()
            try:
                if run.access_point.ip is not None:
                    connection = run.access_point.open_socket(run.access_point.ip)
                    run.access_point.serve(connection)
            except KeyboardInterrupt:
                machine.reset()
        elif run.access_point.home_pass is not None or run.access_point.home_ssid is not None:
            run.wifi.ssid = run.access_point.home_ssid
            run.wifi.password = run.access_point.home_pass
            run.wifi.connect()
            
            run.weight_scale.get_weight()