import json
import sys
import requests
import torch
from transformers import BertTokenizer, GPT2LMHeadModel, TextGenerationPipeline
import redis

REDIS_PORT = 5000

def prep(model_path):
    # redis_client = redis.Redis(host='localhost', port=REDIS_PORT, db=0)

    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = GPT2LMHeadModel.from_pretrained(model_path)
    text_generator = TextGenerationPipeline(model, tokenizer)
    return text_generator, tokenizer, model

def rexists(key):
    reply = requests.get(f"http://host.docker.internal:{REDIS_PORT}/exists", params={"key": key})
    return reply.text == "Key exists"

def rget(key):
    reply = requests.get(f"http://host.docker.internal:{REDIS_PORT}/get", params={"key": key})
    return reply.text

def rset(key, value):
    requests.post(f"http://host.docker.internal:{REDIS_PORT}/set", data={"key": key, "value": value})

def handle(event, context):
    # text_generator = prep("uer/gpt2-distil-chinese-cluecorpussmall")
    text_generator, tokenizer, model = prep("function/hf_gpt2")

    if event.method == "GET":
        json_data = json.loads(event.body)
        batch_size = json_data["batch_size"]
        prefix = json_data["prefix"]
        prompt_list = json_data["prompt_list"]

        # check in redis
        if rexists(prefix):
            redis_res = rget(prefix)
            redis_res = json.loads(redis_res)
            past_key_values = tuple(tuple(torch.tensor(pin) for pin in p) for p in redis_res["past_key_values"])
            pre_attention_mask = torch.tensor(redis_res["pre_attention_mask"])
        else:
            pre_emb = tokenizer(prefix, return_tensors="pt")
            pre_input_ids = pre_emb["input_ids"][:, :-1]
            pre_attention_mask = pre_emb["attention_mask"][:, :-1]
            past_key_values = model(pre_input_ids, attention_mask=pre_attention_mask, use_cache=True, return_dict=True).past_key_values
            past_key_values_tuple = tuple(tuple(pin.tolist() for pin in p) for p in past_key_values)
            rset(prefix, json.dumps({"past_key_values": past_key_values_tuple, "pre_attention_mask": pre_attention_mask.tolist()}))

        past_key_values = tuple(tuple(pin.repeat_interleave(batch_size, dim=0) for pin in p) for p in past_key_values)
        pre_attention_mask = pre_attention_mask.repeat_interleave(batch_size, dim=0)
        
        emb = tokenizer(prompt_list, return_tensors="pt", padding=True)
        input_ids = emb["input_ids"][:, 1:-1]
        attention_mask = emb["attention_mask"][:, 1:-1]
        all_attention_mask = torch.cat([pre_attention_mask, attention_mask], dim=1)
        past_key_values = model(input_ids[:, :-1], attention_mask=all_attention_mask[:, :-1], past_key_values=past_key_values, use_cache=True, return_dict=True).past_key_values

        res = model.generate(
            input_ids,
            attention_mask=all_attention_mask,
            past_key_values=past_key_values,
            max_length=100,
            do_sample=True,
            temperature=0.7,
        )
        gen_res = tokenizer.batch_decode(res, skip_special_tokens=True)

    else:
        gen_res = "Only support GET method."

    return {
        "statusCode": 200,
        "body": gen_res
    }
