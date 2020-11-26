# 
# According to sim7500_sim7600_series_at_command_manual_v2.00.pdf
# 


import serial
import time

ser = None
debug = True

# Init AT Command service
def at_init(port = '/dev/ttyUSB0', baud = 115200, debugMode = True):
    global ser, debug
    ser = serial.Serial(port, baud)
    ser.flushInput()
    debug = debugMode
    return _check_service()

# Close AT Command service
def at_close():
    global ser
    if ser != None:
        ser.close()
    return

def _at_send(command,back,timeout, step_check = 0.01):
    global ser

    rec_buff = ''
    if len(command):
        ser.flushInput()         
        ser.write((command+'\r\n').encode())
            
    i = 0
    while i < timeout/step_check:
        time.sleep(step_check)
        if ser.inWaiting():
            time.sleep(step_check)
            rec_buff = ser.read(ser.inWaiting())
            break
        i += 1
    if rec_buff != '':
        if back not in rec_buff.decode():
            if debug: print(command + ' ERROR')
            if debug: print(command + ' back:\t' + rec_buff.decode())            
            return rec_buff.decode(), False
        else:
            if debug: print(rec_buff.decode())
            return rec_buff.decode(), True
    else:
        if debug: print(command + ' no responce')
        return '', False

def _check_service():    
    # SIM Card Status
    _, ok = _at_send('AT+CPIN?','READY', 1)
    if not ok:
        return False

	# Check signal quality
    _, ok = _at_send('AT+CSQ','OK', 1)
    if not ok:
        return False

	# GPRS network status
    _at_send('AT+CREG?','+CREG: 0,1', 1)
    if not ok:
        return False
    _at_send('AT+CGREG?','+CGREG: 0,1', 1)
    if not ok:
        return False
    
    # End the previous http session if any
    _at_send('AT+HTTPTERM', 'OK', 120)
    return True

def _http_config(url, contentType, sslConfigId, connectTimeout, receiveTimeout):
    if sslConfigId != '':
        _, ok = _at_send('AT+HTTPPARA="SSLCFG",' + sslConfigId, 'OK', 1)
        if not ok:
            return False
    _, ok = _at_send('AT+HTTPPARA="URL","' + url + '"', 'OK', 1)
    if not ok:
        return False
    _, ok = _at_send('AT+HTTPPARA="CONTENT","' + contentType + '"', 'OK', 1)
    if not ok:
        return False
    _, ok = _at_send('AT+HTTPPARA="CONNECTTO",' + str(connectTimeout), 'OK', 1)
    if not ok:
        return False
    _, ok = _at_send('AT+HTTPPARA="RECVTO",' + str(receiveTimeout), 'OK', 1)
    if not ok:
        return False
    return True

# POST HTTP/HTTPS
# HTTP: sslConfigId = ''
# HTTPS: sslConfigId = "0"-"9"
def http_post(url, contentType, data, sslConfigId, connectTimeout, receiveTimeout):
    # Start HTTP session
    _at_send('AT+HTTPINIT', 'OK', 120)

    # Config HTTP session
    ok = _http_config(url, contentType, sslConfigId,connectTimeout, receiveTimeout)
    if not ok:        
        return False

    # POST data
    _, ok = _at_send('AT+HTTPDATA=' + str(len(data)) + ',10000','DOWNLOAD', 1)
    if ok:
        _, ok = _at_send(data, 'OK', 1)
        if ok:
            _, ok = _at_send('AT+HTTPACTION=1', 'OK', 1)            
            if ok:
                _, ok = _at_send('', '1,200', 120)

    # End HTTP session
    _at_send('AT+HTTPTERM', 'OK', 120)   
    return ok

# Start GPS session
def gps_start():
    _at_send('AT+CGPS=1', 'OK', 1)
    time.sleep(2)

# Get GPS info
def gps_get_data():    
    r, ok = _at_send('AT+CGPSINFO', 'OK', 1)
    if not ok or r == '':
        _at_send('AT+CGPS=0', '+CGPS:0', 1)
        return "", False
    if ',,,' in r:
        _at_send('AT+CGPS=0', '+CGPS:0', 1)
        return "", False
    data = r.splitlines()[2]
    data = data.split(" ")[1]
    
    return data, True

# Get GPS info
def gps_stop():    
    _at_send('AT+CGPS=0', 'OK', 1)
    _at_send("", "+CGPS: 0", 5);

# Get time
def time_get():
    r, ok = _at_send('AT+CCLK?', 'OK', 1)
    if not ok:
        return ''
    try:
        data = r.splitlines()[2]
        data = data.split(' ')[1]
        data = data.split('"')[1]
        return data
    except:
        print(r)
        return ''

def rssi():
    # Check signal quality
    rep, ok = _at_send('AT+CSQ','OK', 1)
    if not ok : return 0,0
    if "+CSQ: " not in rep: return 0,0
    start_index = rep.find("+CSQ: ")+ len("+CSQ: ")
    end_index = rep.find( '\r\n',start_index)    
    result = rep[start_index: end_index]
    print("CSQ:" + result)
    l = result.split(",", 1)
    if len(l) < 2: return 0,0
    rssi = int(l[0])
    if rssi == 0: rssi = -113
    if rssi == 1: rssi = -111
    if rssi >= 2 and rssi <= 30: rssi = int(-109 + (rssi -2)*3.1)
    if rssi == 31: rssi = -51
    # ....
    per = float(l[1])
    if per == 0: per = "<0.01%"
    if per == 1: per = "0.01--0.1%"
    # ...
    if per == 99: per = 'not known or not detectable'
    return rssi, per

# Download certificate into the module
def ssl_download_file_to_sim(filename, content):
    _, ok = _at_send('AT+CCERTDOWN="' + filename + '",' + str(len(content)), '>', 1)
    if not ok: return False
    _, ok = _at_send(content, 'OK', 5)
    return ok

# Delete certificates
def ssl_delete_file(filename):
    _, ok = _at_send('AT+CCERTDELE="' + filename + '"', 'OK', 1)
    return ok

# List certificates
def ssl_list():
    rep, _ = _at_send('AT+CCERTLIST', 'OK', 1)
    return rep

# Query the configuration of the specified SSL context
def ssl_query_config(sslConfigId):
    rep, _ = _at_send('AT+CSSLCFG=' + sslConfigId, 'OK', 1)
    return rep

# Configure the SSL context
def ssl_config(sslConfigId, typeConfig, contentConfig):
    prefix = 'AT+CSSLCFG="' + typeConfig + '",' + sslConfigId + ','
    if typeConfig in ['sslversion', 'authmode', 'ignorlocaltime', 'negotiatetime', 'enableSNI', \
         'keypwd', 'ciphersuites']:
        _, ok = _at_send(prefix + contentConfig, 'OK', 1)
        return ok
    if typeConfig in ['cacert', 'clientcert', 'clientkey']:
        _, ok = _at_send(prefix + '"' + contentConfig + '"', 'OK', 1)
        return ok

    if debug: print('Not support config type:' + typeConfig)
    return False