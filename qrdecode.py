import requests
import json
files = {'file': open('D:/ttt.png', 'rb')}
res = requests.post(url='http://api.qrserver.com/v1/read-qr-code/',
    files=files)
jdata = json.loads(res.text)
qrdecode=jdata[0]['symbol'][0]['data']
