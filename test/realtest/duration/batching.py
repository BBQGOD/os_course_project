import time
import urllib3
import json
import psutil

QUERIES = "realdata/sample.txt"
BATCH_SIZE = 4
TIME_INTERVAL = 0.2

with open(QUERIES, "r") as f:
    queries = f.readlines()
queries = [q.strip() for q in queries]

http = urllib3.PoolManager()
url = "http://localhost:8080/function/gpt2batch"
delays = []

timer = time.perf_counter()
res = []
for i in range(0, len(queries), BATCH_SIZE):
    batch = queries[i:i+BATCH_SIZE if i+BATCH_SIZE < len(queries) else len(queries)]
    body = {"batch_size": len(batch), "prompt_list": batch}
    body = json.dumps(body)
    headers = {"Content-Type": "application/json"}
    r = http.request("GET", url, body=body, headers=headers)
    delay = time.perf_counter() - timer
    delays += [delay - TIME_INTERVAL * j for j in range(i, i + len(batch))]
    nex_batch_size = BATCH_SIZE if i + BATCH_SIZE < len(queries) else len(queries) - i
    if i < len(queries) - 1 and delay < TIME_INTERVAL * (i + nex_batch_size):
        time.sleep(TIME_INTERVAL * (i + nex_batch_size) - delay)
    res += json.loads(r.data.decode())

timer = time.perf_counter() - timer
print(res)

print(f"Average time: {timer / len(queries)}s")
print(f"Took {timer}s in total.")
print(f"Delays: {delays}")
print(f"Average delay: {sum(delays) / len(delays)}s")
