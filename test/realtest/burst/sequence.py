import time
import urllib3

TGT_URL = "http://localhost:8080/function/gpt2batch"
QUERIES = "realdata/sample.txt"

with open(QUERIES, "r") as f:
    queries = f.readlines()
queries = [q.strip() for q in queries]

http = urllib3.PoolManager()

timer = time.perf_counter()
for i in queries:
    body = i
    headers = {"Content-Type": "text/plain"}
    r = http.request("GET", TGT_URL, body=body.encode(), headers=headers)
    print(r.data.decode())

timer = time.perf_counter() - timer

print(f"Average time: {timer / len(queries)}s")
print(f"Took {timer}s in total.")
