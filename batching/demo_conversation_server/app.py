import time
from flask import Flask, request
import json
import urllib3
import concurrent.futures

FAAS_URL = "http://localhost:8080/function/gpt2batch"
FAAS_CACHED_URL = "http://localhost:8080/function/gpt2prefixbatchcached"
CANDIDATES_NUM = 8

app = Flask(__name__)
http = urllib3.PoolManager()

# set方法
@app.route('/send_sequential', methods=['GET'])
def send_sequential():
    query = request.args.get('query')
    timer = time.perf_counter()
    body = query
    ans_list = []
    for i in range(CANDIDATES_NUM):
        headers = {"Content-Type": "text/plain"}
        r = http.request("GET", FAAS_URL, body=body.encode(), headers=headers)
        ans_list.append(r.data.decode())

    timer = time.perf_counter() - timer
    return json.dumps({"ans_list": ans_list, "time": timer}, ensure_ascii=False)

# get方法
@app.route('/send_concurrency', methods=['GET'])
def send_concurrency():
    ans_list = [""] * CANDIDATES_NUM
    def test(inp, pid):
        body = inp
        headers = {"Content-Type": "text/plain"}
        r = http.request("GET", FAAS_URL, body=body.encode(), headers=headers)
        ans_list[pid] = r.data.decode()
    query = request.args.get('query')
    timer = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(CANDIDATES_NUM):
            executor.submit(test, query, i, timer)
    timer = time.perf_counter() - timer

    return json.dumps({"ans_list": ans_list, "time": timer}, ensure_ascii=False)

# exists方法
@app.route('/send_batch', methods=['GET'])
def send_batch():
    query = request.args.get('query')
    body = {"batch_size": CANDIDATES_NUM, "prompt_list": [query] * CANDIDATES_NUM}
    body = json.dumps(body)
    headers = {"Content-Type": "application/json"}
    timer = time.perf_counter()
    r = http.request("GET", FAAS_URL, body=body, headers=headers)
    timer = time.perf_counter() - timer
    ans_list = json.loads(r.data.decode())
    return json.dumps({"ans_list": ans_list, "time": timer}, ensure_ascii=False)
    
@app.route('/send_prefixbatch', methods=['GET'])
def send_prefixbatch():
    query = request.args.get('query')
    prefix, query = query[:-2], query[-2:]
    body = {"batch_size": CANDIDATES_NUM, "prompt_list": [query] * CANDIDATES_NUM, "prefix": prefix, "max_length": 100}
    body = json.dumps(body)
    headers = {"Content-Type": "application/json"}
    timer = time.perf_counter()
    r = http.request("GET", FAAS_CACHED_URL, body=body, headers=headers)
    timer = time.perf_counter() - timer
    ans_list = json.loads(r.data.decode())
    ans_list = [prefix + i for i in ans_list]
    return json.dumps({"ans_list": ans_list, "time": timer}, ensure_ascii=False)

if __name__ == '__main__':
    app.run(debug=True, port=7050)
