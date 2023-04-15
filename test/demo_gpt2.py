import urllib3
import json

http = urllib3.PoolManager()
url = "http://localhost:8080/function/gpt2"
body = "你好"
headers = {"Content-Type": "text/plain"}
r = http.request("GET", url, body=body.encode(), headers=headers)
print(json.loads(r.data.decode()))
