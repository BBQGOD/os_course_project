import time
import urllib3
import json
import psutil


def get_memory_usage(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return proc.memory_info().rss
    return None


http = urllib3.PoolManager()
url = "http://localhost:8080/function/gpt2batch"

timer = time.perf_counter()
body = {"batch_size": 4, "prompt_list": ["你好", "你好", "你好", "你好"]}
body = json.dumps(body)
headers = {"Content-Type": "application/json"}
r = http.request("GET", url, body=body, headers=headers)
res = json.loads(r.data.decode())
r = http.request("GET", url, body=body, headers=headers)
res += json.loads(r.data.decode())
timer = time.perf_counter() - timer
print(res)

print(f"Average time: {timer / 8}s")
print(f"Took {timer}s in total.")
