import serial
import time

ser = None
debug = True

def at_init(port = '/dev/ttyUSB0', baud = 115200, debugMode = True):
    global ser, debug
    ser = serial.Serial(port, baud)
    ser.flushInput()
    debug = debugMode
    return check_service()

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

def check_service():    
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

def _http_config(url, contentType, connectTimeout, receiveTimeout):
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

def http_post(url, contentType, data, connectTimeout, receiveTimeout):
    # Start HTTP session
    _at_send('AT+HTTPINIT', 'OK', 120)

    # Config HTTP session
    ok = _http_config(url, contentType, connectTimeout, receiveTimeout)
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

def gps_get_data():
    # Start GPS session
    _at_send('AT+CGPS=1', 'OK', 1)

    # Get GPS info
    r, ok = _at_send('AT+CGPSINFO', 'OK', 1)
    if not ok or r == '':
        _at_send('AT+CGPS=0', '+CGPS:0', 1)
        return "", False
    if ',,,' in r:
        _at_send('AT+CGPS=0', '+CGPS:0', 1)
        return "", False
    data = r.splitlines()[2]
    data = data.split(" ")[1]

    # End GPS session
    _at_send('AT+CGPS=0', '+CGPS:0', 1)
    return data, True

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