import urllib3

TGT_URL = "http://localhost:8080/function/gpt2"

http = urllib3.PoolManager()

timer = 0
for i in range(10):
    body = "你好"
    headers = {"Content-Type": "text/plain"}
    r = http.request("GET", TGT_URL, body=body.encode(), headers=headers)
    print(r.data.decode())
    timer += r.elapsed.total_seconds()

print(f"Average time: {timer / 10}s")
print(f"Took {timer}s in total.")
