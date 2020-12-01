import requests
import base64
import json

if __name__=="__main__":
    url = "http://157.230.32.117:8082/topics/test-pi"
    headers = {
        "Content-Type" : "application/vnd.kafka.json.v2+json",
    }
    # Create one or more messages
    payload = {"records":
        [{
            "key": 'alo',
            "value":'alo',
        }],
    }
    # Send the message
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.status_code != 200:
        print("Status Code: " + str(r.status_code))
        print(r.text)
