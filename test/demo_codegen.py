import urllib3
import json


SRC_FILE = "codegen/src.py"
TGT_FILE = "codegen/tgt.py"

with open(SRC_FILE, "r") as f:
    src = f.readlines()
src = [s.strip() for s in src]
src = '\n'.join(src)

http = urllib3.PoolManager()
url = "http://localhost:8080/function/codegen"
body = json.dumps({"prompt_list": [src], "batch_size": 1})
headers = {"Content-Type": "text/plain"}
r = http.request("GET", url, body=body.encode(), headers=headers)
print(r.data.decode())

res_list = json.loads(r.data.decode())
with open(TGT_FILE, "w") as f:
    for res in res_list:
        f.write(res)
