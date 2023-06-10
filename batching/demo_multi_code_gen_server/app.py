import urllib3
import json
import sys

TGT_URL = "http://localhost:8080/function/codegen"
TGT_CACHED_URL = "http://localhost:8080/function/codegencached"

url = TGT_URL if sys.argv[1] == "uncached" else TGT_CACHED_URL
history = ""
last_history = ""

while True:
    src = input("Input: ")
    if src == "exit":
        break

    http = urllib3.PoolManager()
    if sys.argv[1] == "uncached":
        body = json.dumps({"prompt_list": [history+src], "batch_size": 1})
    else:
        body = json.dumps({"prompt_list": [src], "batch_size": 1, "prefix": history, "last": last_history})
    headers = {"Content-Type": "text/plain"}
    r = http.request("GET", url, body=body.encode(), headers=headers)
    res_list = json.loads(r.data.decode())
    res = res_list[0]
    print("Output: \n" + (res if sys.argv[1] == "uncached" else history + last_history + res))

    if sys.argv[1] == "uncached":
        history = res
    else:
        history += last_history
        last_history = res
