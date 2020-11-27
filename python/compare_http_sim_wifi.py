import sys
import sim
import requests
import time

time_run = 0
if len(sys.argv) < 2:
    print("Thieu thoi gian chay")
    exit(0)

time_run = float(sys.argv[1])

Debug = True
if len(sys.argv) >= 3:
    Debug = (sys.argv[2] == 'True')

URL = 'http://45.77.243.33:8080/api/v1/alhY2wLklhTaumjaQ9V0/telemetry'
ContentType = 'application/json'

HTTP_CONNECT_TIMEOUT = 20   #s
HTTP_RESPONSE_TIMEOUT = 5   #s

SIM_SERIAL_PORT = '/dev/ttyUSB0'
SIM_SERIAL_BAUD = 115200

body = '{"Temperature(oC)":29.0,"Humidity(%)":74.5,"PM2.5(ug_m3)":30.0}'

f_sum = open("http_sim_wifi.txt", mode="w", encoding="utf-8")

def getip():
    rep, ok = sim.http_get('http://httpbin.org/ip', '', 0, 0)
    if ok:
        for item in rep.split("\n"):
            if "origin" in item:                
                return item.split(':')[1].strip(), True                
    return '', False

# ------------------------------------------------------------------
def wifi_http_post(json_data):
    try:        
        r = requests.post(URL ,data=json_data, timeout=(HTTP_CONNECT_TIMEOUT, HTTP_RESPONSE_TIMEOUT))
        if r.status_code == 200:
            return True
        return False       
    except requests.exceptions.RequestException as e:
        pass
    
    return False


# ------------------------------------------
# init SIM
ok = sim.at_init(SIM_SERIAL_PORT, SIM_SERIAL_BAUD, Debug)
if not ok:
    print('SIM AT init error')
    sys.exit(1)

rssi, per = sim.rssi()
ip, ok = getip()
if not ok:
    print('Cannot get IP')
    sys.exit(-1)

print("------------------------- Thong tin thu nghiem -------------------------")
print('URL = "http://45.77.243.33:8080/api/v1/alhY2wLklhTaumjaQ9V0/telemetry"\n\
    ContentType = "application/json"\n\
    Content = {"Temperature(oC)":29.0,"Humidity(%)":74.5,"PM2.5(ug_m3)":30.0}\n\
    HTTP_CONNECT_TIMEOUT = 20s\n\
    HTTP_RESPONSE_TIMEOUT = 5s\n\n')
print("SIM:\nSIM_SERIAL_BAUD = 115200\nRSSI = {} - Channel bit error rate = {}".format(rssi, per))

print("------------------------- Bat dau thu nghiem trong {}s -------------------------".format(str(time_run*60)))

wifi_err_sum = 0
sim_err_sum = 0
main_is_run = True
time_elapse = int(round(time.time()) + time_run*60)
counter = 0

# loop
try:
    while main_is_run:
        # Sending data to ThingsBoard 

        # Send via WiFi
        # print("------------------------WiFi-----------------------")
        start_time_0 = int(round(time.time() * 1000))
        ok = wifi_http_post(body)
        if not ok:
            wifi_err_sum += 1            
            print("------------------------WiFi: ERROR----------------")
        else:
            print("------------------------WiFi: OK-------------------")
        end_time = int(round(time.time() * 1000))
        f_sum.write(str(end_time-start_time_0))
        f_sum.write(",")

        # Send via Sim
        # print("========================SIM===========================")
        start_time = int(round(time.time() * 1000))        
        ok = sim.http_post(URL, ContentType, body, '', HTTP_CONNECT_TIMEOUT, HTTP_RESPONSE_TIMEOUT) 
        if not ok:            
            sim_err_sum += 1
            print("========================SIM: ERROR====================")
        else:
            print("========================SIM: OK=======================")
        end_time = int(round(time.time() * 1000))
        f_sum.write(str(end_time-start_time))
        f_sum.write(",")        
        f_sum.write(str(end_time-start_time_0))
        f_sum.write("\n")        

        counter += 1
        # Read sensor
        # 
        # time.sleep(0.5)
        if int(round(time.time())) > time_elapse:                
            main_is_run = False              
            sim.at_close()
            info = 'Sum:' + str(counter) + '\tWiFi_Error:' + str(wifi_err_sum) + '\tSim_Error:' + str(sim_err_sum)
            f_sum.write(info)
            f_sum.close()

except KeyboardInterrupt:    
    main_is_run = False     
    sim.at_close()
    info = 'Sum:' + str(counter) + '\tWiFi_Error:' + str(wifi_err_sum) + '\tSim_Error:' + str(sim_err_sum)
    f_sum.write(info)
    f_sum.close()

print('Sum:' + str(counter) + '\tWiFi_Error:' + str(wifi_err_sum) + '\tSim_Error:' + str(sim_err_sum))