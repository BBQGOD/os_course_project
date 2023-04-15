import urllib3
import json
from PIL import Image

http = urllib3.PoolManager()
url = "http://localhost:8080/function/sd"
body = "A bird flying in the sky"
headers = {"Content-Type": "text/plain"}
r = http.request("GET", url, body=body.encode(), headers=headers)
print(json.loads(r.data.decode()))
body = json.loads(r.data.decode())["body"]
print(body["gen_res"])
image = Image.frombytes(body["mode"], body["size"], body["raw_bytes"].encode())
image.save("test.png")
