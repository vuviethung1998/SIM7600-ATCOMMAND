import sys
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

body = '{"Temperature(oC)":29.0,"Humidity(%)":74.5,"PM2.5(ug_m3)":30.0}'

f_sum = open("http_wifi.txt", mode="w", encoding="utf-8")


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
print("------------------------- Thong tin thu nghiem -------------------------")
print('URL = "http://45.77.243.33:8080/api/v1/alhY2wLklhTaumjaQ9V0/telemetry"\n\
    ContentType = "application/json"\n\
    Content = {"Temperature(oC)":29.0,"Humidity(%)":74.5,"PM2.5(ug_m3)":30.0}\n\
    HTTP_CONNECT_TIMEOUT = 20s\n\
    HTTP_RESPONSE_TIMEOUT = 5s\n\n')

print("------------------------- Bat dau thu nghiem trong {}s -------------------------".format(str(time_run*60*60)))

wifi_err_sum = 0
main_is_run = True
time_elapse = int(round(time.time()) + time_run*60*60)
counter = 0
info_cqs = '---'
# loop
try:
    while main_is_run:
        # Sending data to ThingsBoard 
        # Send via WiFi
        # print("========================WiFi===========================")
        start_time = int(round(time.time() * 1000))        
        ok = wifi_http_post(body) 
        if not ok:            
            wifi_err_sum += 1
            print("========================WiFi: ERROR====================")
        # else:
            # print("========================WiFi: OK=======================")
        end_time = int(round(time.time() * 1000))
        f_sum.write(str(start_time) + ',')
        f_sum.write(str(end_time) + ',')
        f_sum.write(str(end_time-start_time) + ',')
        if ok: f_sum.write('1')
        else: f_sum.write('0')
        f_sum.write("\n")

        counter += 1        
        if int(round(time.time())) > time_elapse:                
            main_is_run = False                          
            info = 'Sum:' + str(counter) + '    WiFi_Error:' + str(wifi_err_sum) + '    %error=' +str(round(wifi_err_sum*100/counter,2))
            f_sum.write(info)
            f_sum.write("\n")        
            f_sum.write(info_cqs)
            f_sum.close()

except KeyboardInterrupt:    
    main_is_run = False         
    info = 'Sum:' + str(counter) + '    WiFi_Error:' + str(wifi_err_sum) + '    %error=' +str(round(wifi_err_sum*100/counter,2))
    f_sum.write(info)
    f_sum.write("\n")
    f_sum.write(info_cqs)
    f_sum.close()

print('Sum:' + str(counter) + '    WiFi_Error:' + str(wifi_err_sum) + '    %error=' +str(round(wifi_err_sum*100/counter,2)))