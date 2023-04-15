import urllib3
import json

http = urllib3.PoolManager()
url = "http://localhost:8080/function/gpt2"
body = {"batch_size": 3, "prompt_list": ["你好", "你好", "你好"]}
body = json.dumps(body)
headers = {"Content-Type": "text/plain"}
r = http.request("GET", url, body=body, headers=headers)
print(r.data.decode())

'''
['你好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 他 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好 我 也 好', '你好 ， 我 们 来 聊 聊 你 们 的 感 情 。 这 个 问 题 是 我 想 到 的 。 你 看 ， 你 喜 欢 我 ， 我 喜 欢 你 ， 不 是 因 为 你 喜 欢 我 ， 而 是 因 为 我 喜 欢 你 。 这 个 世 界 上 没 有 对 你 好 的 人 ， 你 好 好 爱 过 吗 ？ 如 果 你 真 的 喜 欢 我 ， 我 会 一 直 陪 你 。', '你好 ， 我 也 是 一 个 很 好 的 人 ， 很 受 欢 迎 ， 非 常 有 天 赋 。 可 惜 我 今 年 的 大 学 生 活 ， 根 本 没 有 好 好 学 习 ， 每 天 就 是 在 家 里 一 个 人 ， 我 真 的 很 累 ， 我 不 想 再 回 学 校 ， 我 也 不 想 再 回 到 学 校 ， 我 真 的 不 想 再 回 来 了 ， 不 想 再 回 来 了 ， 我 真 的 很']
'''
