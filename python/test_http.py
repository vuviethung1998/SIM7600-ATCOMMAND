import sys
import sim

Debug = True

URL_HTTP = 'http://httpbin.org/post'
URL_HTTPS = 'https://httpbin.org/post'
ContentType = 'application/json'
body = '{"Temperature(oC)":29.0,"Humidity(%)":74.5,"PM2.5(ug_m3)":30.0}'

HTTP_CONNECT_TIMEOUT = 20   #s
HTTP_RESPONSE_TIMEOUT = 5   #s

SIM_SERIAL_PORT = '/dev/ttyUSB0'
SIM_SERIAL_BAUD = 115200

AMAZON_CERT = '''-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy
rqXRfboQnoZsG4q5WTP468SQvvG5
-----END CERTIFICATE-----
'''

# ---------------------- MAIN ---------------------
# init SIM
ok = sim.at_init(SIM_SERIAL_PORT, SIM_SERIAL_BAUD, Debug)
if not ok:
    print('SIM AT init error')
    sys.exit(1)

# SSL: Delete cert
ok = sim.ssl_delete_file('amazon_ca.pem')
if not ok:
        if Debug: print('Error: Can not delete cert in SIM')

# SSL: List config
rep = sim.ssl_list()
print('SSL List:' + rep)

if 'amazon_ca.pem' not in rep:
    # SSL: Download cert to SIM, save as 'amamzon_ca.pem'
    ok = sim.ssl_download_file_to_sim('amazon_ca.pem', AMAZON_CERT)
    if not ok:
        if Debug: print('Error: Can not download cert to SIM')


# SSL: Query config
rep = sim.ssl_query_config('0')
print('SSL query:' + rep)

# POST HTTP
if Debug:
    print('Send data to HTTP Server:' + URL_HTTP)
    print(body)
# Reset authmode
ok = sim.ssl_config('0','authmode', '0')
if not ok:
    if Debug: print("ssl_config('0','authmode', '0') Failed")

ok = sim.http_post(URL_HTTP, ContentType, body, '' ,HTTP_CONNECT_TIMEOUT, HTTP_RESPONSE_TIMEOUT)
if not ok:
    if Debug: print('Error send data to HTTP Server')

# POST HTTPS
if Debug:
    print('Send data to HTTPS Server:' + URL_HTTPS)
    print(body)
# Set authmode
ok = sim.ssl_config('0','authmode', '1')
if not ok:
    if Debug: print("ssl_config('0','authmode', '1') Failed")

# Set cert
ok = sim.ssl_config('0', 'cacert', 'amazon_ca.pem')
if not ok:
    if Debug: print("ssl_config('0', 'cacert', 'amazon_ca.pem') Failed")

ok = sim.http_post(URL_HTTPS, ContentType, body, '0' ,HTTP_CONNECT_TIMEOUT, HTTP_RESPONSE_TIMEOUT)
if not ok:
    if Debug: print('Error send data to HTTPS Server') 

sim.at_close()