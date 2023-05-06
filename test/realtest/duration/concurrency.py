import urllib3
import concurrent.futures
import time

TGT_URL = "http://localhost:8080/function/gpt2batch"
QUERIES = "realdata/sample.txt"
TIME_INTERVAL = 0.2

http = urllib3.PoolManager()

delays = []

def test(inp, pid, start_time):
    body = inp
    headers = {"Content-Type": "text/plain"}
    r = http.request("GET", TGT_URL, body=body.encode(), headers=headers)
    delays[pid] = time.perf_counter() - start_time
    print(r.data.decode())

if __name__ == "__main__":
    with open(QUERIES, "r") as f:
        queries = f.readlines()
    queries = [q.strip() for q in queries]
    delays = [0 for _ in queries]

    # timer
    timer = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for i, q in enumerate(queries):
            executor.submit(test, q, i, time.perf_counter())
            time.sleep(TIME_INTERVAL)
    timer = time.perf_counter() - timer

    print(f"Average time: {timer / len(queries)}s")
    print(f"Took {timer}s in total.")
    print(f"Delays: {delays}")
    print(f"Average delay: {sum(delays) / len(delays)}s")
