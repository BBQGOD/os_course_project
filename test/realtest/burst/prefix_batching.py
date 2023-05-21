import time
import urllib3
import json
import psutil

QUERIES = "realdata/sample.txt"
BATCH_SIZE = 4


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = None
        self.cnt = 0

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.nodes = [self.root]

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                new_node = TrieNode()
                node.children[char] = len(self.nodes)
                self.nodes.append(new_node)
            node = self.nodes[node.children[char]]
        node.is_end = True
        node.word = word
        node.cnt += 1

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = self.nodes[node.children[char]]
        return node.is_end

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = self.nodes[node.children[char]]
        return self._get_words(node)

    def _get_words(self, node):
        words = []
        if node.is_end:
            words.append(node.word)
        for child in node.children.values():
            words.extend(self._get_words(self.nodes[child]))
        return words

    def delete(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = self.nodes[node.children[char]]
        if not node.is_end:
            return False
        node.is_end = False
        node.word = None
        return True
    
def longest_common_prefix(words):
    if not words:
        return ""
    for i, char in enumerate(words[0]):
        for word in words[1:]:
            if i >= len(word) or word[i] != char:
                return words[0][:i]
    return words[0]

with open(QUERIES, "r") as f:
    queries = f.readlines()
queries = [q.strip() for q in queries]
queries = sorted(queries)

http = urllib3.PoolManager()
url = "http://localhost:8080/function/gpt2prefixbatchcached"
delays = []

timer = time.perf_counter()
res = []
for i in range(0, len(queries), BATCH_SIZE):
    batch = queries[i:i+BATCH_SIZE if i+BATCH_SIZE < len(queries) else len(queries)]
    prefix = longest_common_prefix(batch)
    if len(prefix) >= min(len(q) for q in batch) - 1:
        prefix = prefix[:-2]
    if len(prefix) < 10:
        prefix = ''
    batch = [q[len(prefix):] for q in batch]
    # if len(prefix) > 0:
    #     prefix = ' '.join([prefix for _ in range(4)])
    #     batch = [prefix + q for q in batch]
    # if len(prefix) > 0:
        # prefix = ' '.join([prefix for _ in range(5)])
    # prefix = ''

    body = {"batch_size": len(batch), "prompt_list": batch, "prefix": prefix, "max_length": 200}
    print(prefix)
    # print(body)
    body = json.dumps(body)
    headers = {"Content-Type": "application/json"}
    r = http.request("GET", url, body=body, headers=headers)
    delays += [time.perf_counter() - timer for _ in range(len(batch))]
    # print(r.data)
    tmpres = json.loads(r.data.decode())
    tmpres = [prefix + res for res in tmpres]
    # print(tmpres)
    res += tmpres

timer = time.perf_counter() - timer
print(res)

print(f"Average time: {timer / len(queries)}s")
print(f"Took {timer}s in total.")
print(f"Delays: {delays}")
print(f"Average delay: {sum(delays) / len(delays)}s")

