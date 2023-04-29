import socket
import network
import machine
import math
import utime
import time

class AccessPoint:
    def __init__(self):
        self.ssid = "SSID"
        self.password = "Password"
        self.home_ssid = None
        self.home_pass = None
        self.ip = None
        
        self.wifi_login = """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Connect to Home Wifi</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            background-color: #f5f5f5;
                        }
                        h1 {
                            text-align: center;
                            color: #333;
                        }
                        form {
                            width: 50%;
                            margin: 0 auto;
                            background-color: #fff;
                            padding: 20px;
                            border-radius: 5px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                        }
                        label {
                            display: block;
                            margin-bottom: 10px;
                            font-weight: bold;
                        }
                        input[type="text"], input[type="password"] {
                            padding: 10px;
                            border-radius: 5px;
                            border: none;
                            box-shadow: 0 1px 1px rgba(0,0,0,0.1);
                            width: 100%;
                            margin-bottom: 20px;
                        }
                        input[type="submit"], input[type="reset"] {
                            background-color: #4CAF50;
                            color: #fff;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 5px;
                            cursor: pointer;
                        }
                        input[type="submit"]:hover, input[type="reset"]:hover {
                            background-color: #3e8e41;
                        }
                        #response {
                            color: green;
                            font-weight: bold;
                            text-align: center;
                            margin-top: 20px;
                        }
                        #error {
                            color: red;
                            font-weight: bold;
                            text-align: center;
                            margin-top: 20px;
                        }
                    </style>
                </head>
                <body>
                    <h1>Connect to Home Wifi</h1>
                    <form id="wifiForm" onsubmit="return submitForm()">
                        <label for="ssid">SSID:</label>
                        <input type="text" id="ssid" name="ssid" required>
                        <label for="pass">Password:</label>
                        <input type="password" id="pass" name="pass" required>
                        <div style="text-align: center;">
                            <input type="submit" value="Submit">
                            <input type="reset" value="Reset">
                        </div>
                    </form>
                    <div id="response"></div>
                    <div id="error"></div>
                    <script>
                        function submitForm() {
                            var home_ssid = document.getElementById('ssid').value;
                            var home_password = document.getElementById('pass').value;
                            
                            // Here, you can replace this dummy implementation with your actual code
                            if (home_ssid && home_password) {
                                document.getElementById("response").innerHTML = "Connected to home wifi successfully!";
                            } else {
                                document.getElementById("error").innerHTML = "Please enter both SSID and password.";
                            }
                            document.getElementById("wifiForm").addEventListener("submit", getInputValues);
                            document.getElementById("wifiForm").reset();
                            return false;
                        }
                    </script>
                </body>
            </html>
        """


        self.wifi_connecting = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Loading</title>
                <style>
                    .loader {
                        border: 16px solid #f3f3f3;
                        border-top: 16px solid #3498db;
                        border-radius: 50%;
                        width: 120px;
                        height: 120px;
                        animation: spin 2s linear infinite;
                        margin: auto;
                        position: absolute;
                        top: 0;
                        bottom: 0;
                        left: 0;
                        right: 0;
                    }

                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            </head>
            <body>
                <div class="loader"></div>
                <h1 style="text-align: center;">Now connecting to your wifi...</h1>
            </body>
            </html>
        """
    
    def turn_on_ap(self):
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=self.ssid, password=self.password) 
        ap.active(True)

        while ap.active == False:
          pass

        print("Access point active")
        print(ap.ifconfig())
        self.ip = ap.ifconfig()[0]
        
    def unquote_plus(self, s):
        s = s.replace('+', ' ')
        res = s.split('%')
        for i in range(1, len(res)):
            item = res[i]
            try:
                res[i] = chr(int(item[:2], 16)) + item[2:]
            except ValueError:
                res[i] = '%' + item
        return "".join(res)

   
    def serve(self, connection):
        while True:
            client = connection.accept()[0]
            request = client.recv(1024)
            request = str(request)
            
            try:
                request = request.split()[1]
            except IndexError:
                pass
            
            print(request)
            if "?" in request:
                # Get the query string
                query = request.split("?")[1]
                # Split the query string into individual key-value pairs
                query_params = query.split("&")
                # Extract the values of ssid and pass from the query parameters
                for param in query_params:
                    key, value = param.split("=")
                    if key == "ssid":
                        self.home_ssid = self.unquote_plus(value)
                    elif key == "pass":
                        self.home_pass = self.unquote_plus(value)
                # Print the values of ssid and pass
                print("SSID:", self.home_ssid)
                print("Password:", self.home_pass)
                
                client.send(self.wifi_connecting)
                
                time.sleep(5)
                
                response = 'HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n'
                client.send(response.encode())
                break
            else:
                client.send(self.wifi_login)
            client.close()

    def open_socket(self, ip):
        # Open a socket
        address = (ip, 80)
        connection = socket.socket()
        connection.bind(address)
        connection.listen(1)
        return(connection)

if __name__ == "__main__":
    ap = AccessPoint()
    ap.turn_on_ap()
    try:
        if ap.ip is not None:
            connection = ap.open_socket(ap.ip)
            ap.serve(connection)
    except KeyboardInterrupt:
        machine.reset()
