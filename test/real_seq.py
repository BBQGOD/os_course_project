import time
import urllib3

TGT_URL = "http://localhost:8080/function/gpt2"

http = urllib3.PoolManager()

timer = time.perf_counter()
for i in range(8):
    body = "你好"
    headers = {"Content-Type": "text/plain"}
    r = http.request("GET", TGT_URL, body=body.encode(), headers=headers)
    print(r.data.decode())

timer = time.perf_counter() - timer

print(f"Average time: {timer / 8}s")
print(f"Took {timer}s in total.")
