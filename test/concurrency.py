import urllib3
import concurrent.futures
import time

TGT_URL = "http://localhost:8080/function/gpt2batch"

http = urllib3.PoolManager()

def test():
    body = "你好"
    headers = {"Content-Type": "text/plain"}
    r = http.request("GET", TGT_URL, body=body.encode(), headers=headers)
    print(r.data.decode())

if __name__ == "__main__":
    # concurrent.futures.ThreadPoolExecutor
    # timer
    timer = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(8):
            executor.submit(test)
    timer = time.perf_counter() - timer

    print(f"Average time: {timer / 8}s")
    print(f"Took {timer}s in total.")

