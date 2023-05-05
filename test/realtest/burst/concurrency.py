import urllib3
import concurrent.futures
import time

TGT_URL = "http://localhost:8080/function/gpt2batch"
QUERIES = "realdata/sample.txt"

http = urllib3.PoolManager()

def test(inp):
    body = inp
    headers = {"Content-Type": "text/plain"}
    r = http.request("GET", TGT_URL, body=body.encode(), headers=headers)
    print(r.data.decode())

if __name__ == "__main__":
    with open(QUERIES, "r") as f:
        queries = f.readlines()
    queries = [q.strip() for q in queries]

    # timer
    timer = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for i in queries:
            executor.submit(test, i)
    timer = time.perf_counter() - timer

    print(f"Average time: {timer / len(queries)}s")
    print(f"Took {timer}s in total.")

