import time
import urllib3

TGT_URL = "http://localhost:8080/function/gpt2batch"
QUERIES = "realdata/sample.txt"
TIME_INTERVAL = 0.2

with open(QUERIES, "r") as f:
    queries = f.readlines()
queries = [q.strip() for q in queries]

http = urllib3.PoolManager()

delays = []

timer = time.perf_counter()
for qid, i in enumerate(queries):
    body = i
    headers = {"Content-Type": "text/plain"}
    r = http.request("GET", TGT_URL, body=body.encode(), headers=headers)
    print(r.data.decode())
    delay = time.perf_counter() - timer
    delays.append(delay - TIME_INTERVAL * qid)
    if qid < len(queries) - 1 and delay < TIME_INTERVAL * (qid + 1):
        time.sleep(TIME_INTERVAL * (qid + 1) - delay)

timer = time.perf_counter() - timer

print(f"Average time: {timer / len(queries)}s")
print(f"Took {timer}s in total.")
print(f"Delays: {delays}")
print(f"Average delay: {sum(delays) / len(delays)}s")
