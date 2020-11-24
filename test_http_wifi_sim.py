import sys
import sim
import requests

Debug = True

URL = 'http://httpbin.org/post'
ContentType = 'application/json'

HTTP_CONNECT_TIMEOUT = 20   #s
HTTP_RESPONSE_TIMEOUT = 5   #s

SIM_SERIAL_PORT = '/dev/ttyUSB0'
SIM_SERIAL_BAUD = 115200

body = '{"Temperature(oC)":29.0,"Humidity(%)":74.5,"PM2.5(ug_m3)":30.0}'

# ----------------- HTTP ------------------------
# 
def wifi_http_post(url, contentType, json_data, connTimeout, recvTimeout):
    try:
        headers={"Content-Type":contentType}        
        r = requests.post(url ,data=json_data, headers = headers,  timeout = (connTimeout, recvTimeout))
        if r.status_code == 200:
            return True
        return False       
    except requests.exceptions.RequestException as e:
        # print('WiFi: Request error:{}'.format(e))
        pass
    
    return False

def http_post(url, contentType, json_data, connTimeout, recvTimeout):
    if not wifi_http_post(url, contentType, json_data, connTimeout, recvTimeout):
        if Debug: print('Error: Send via WiFi error.')
        if not sim.http_post(url, contentType, json_data, connTimeout, recvTimeout):
            if Debug: print('Error: Send via Sim error.')
            return False
    return True

# ---------------------- MAIN ---------------------
# init SIM
ok = sim.at_init(SIM_SERIAL_PORT, SIM_SERIAL_BAUD, Debug)
if not ok:
    print('SIM AT init error')
    sys.exit(1)

main_is_run = True
# loop
try:
    while main_is_run:
        # Sending data to Server 

        if Debug:
            print('Send data to Server:' + URL)
            print(body)
        ok = http_post(URL, ContentType, body, HTTP_CONNECT_TIMEOUT, HTTP_RESPONSE_TIMEOUT)
        if not ok:
            if Debug: print('Error send data to Server')
    
except KeyboardInterrupt:    
    main_is_run = False     
    sim.at_close()