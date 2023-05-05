import time
import urllib3
import json
import psutil

QUERIES = "realdata/sample.txt"
BATCH_SIZE = 4

def get_memory_usage(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return proc.memory_info().rss
    return None

with open(QUERIES, "r") as f:
    queries = f.readlines()
queries = [q.strip() for q in queries]

http = urllib3.PoolManager()
url = "http://localhost:8080/function/gpt2batch"

timer = time.perf_counter()
res = []
for i in range(0, len(queries), BATCH_SIZE):
    batch = queries[i:i+BATCH_SIZE if i+BATCH_SIZE < len(queries) else len(queries)]
    body = {"batch_size": len(batch), "prompt_list": batch}
    body = json.dumps(body)
    headers = {"Content-Type": "application/json"}
    r = http.request("GET", url, body=body, headers=headers)
    res += json.loads(r.data.decode())

timer = time.perf_counter() - timer
print(res)

print(f"Average time: {timer / len(queries)}s")
print(f"Took {timer}s in total.")
