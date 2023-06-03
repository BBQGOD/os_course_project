import json
import sys
import redis
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextGenerationPipeline, CodeGenForCausalLM

REDIS_PORT = 6557

def prep(model_path):
    redis_client = redis.Redis(host='172.17.0.1', port=REDIS_PORT, db=0)
    
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    text_generator = TextGenerationPipeline(model, tokenizer)
    return text_generator, tokenizer, model, redis_client

def handle(event, context):
    # text_generator = prep("Salesforce/codegen-350M-mono")
    text_generator, tokenizer, model, redis_client = prep("function/hf_codegen")

    if event.method == "GET":
        json_data = json.loads(event.body)
        batch_size = json_data["batch_size"]
        prefix = json_data["prefix"]
        last = json_data["last"]
        prompt_list = json_data["prompt_list"]

        if len(prefix) > 0:
        # check in redis
            if redis_client.exists(prefix):
                redis_res = redis_client.get(prefix)
                redis_res = json.loads(redis_res.decode("utf-8"))
                past_key_values = tuple(tuple(torch.tensor(pin) for pin in p) for p in redis_res["past_key_values"])
                pre_attention_mask = torch.tensor(redis_res["pre_attention_mask"])
                print("redis hit", file=sys.stderr)
            else:
                pre_emb = tokenizer(prefix, return_tensors="pt")
                pre_input_ids = pre_emb["input_ids"][:, :-1]
                pre_attention_mask = pre_emb["attention_mask"][:, :-1]
                past_key_values = model(pre_input_ids, attention_mask=pre_attention_mask, use_cache=True, return_dict=True).past_key_values
                past_key_values_tuple = tuple(tuple(pin.tolist() for pin in p) for p in past_key_values)
                redis_client.set(prefix, json.dumps({"past_key_values": past_key_values_tuple, "pre_attention_mask": pre_attention_mask.tolist()}))

            # save past_key_value of last to redis
            if len(last) > 0:
                last_emb = tokenizer(last, return_tensors="pt")
                last_input_ids = last_emb["input_ids"][:, :-1]
                last_attention_mask = last_emb["attention_mask"][:, :-1]
                pre_attention_mask = torch.cat([pre_attention_mask, last_attention_mask], dim=1)
                past_key_values = model(last_input_ids, attention_mask=pre_attention_mask, past_key_values=past_key_values, use_cache=True, return_dict=True).past_key_values
                past_key_values_tuple = tuple(tuple(pin.tolist() for pin in p) for p in past_key_values)
                
                redis_client.set(prefix+last, json.dumps({"past_key_values": past_key_values_tuple, "pre_attention_mask": pre_attention_mask.tolist()}))

            past_key_values = tuple(tuple(pin.repeat_interleave(batch_size, dim=0) for pin in p) for p in past_key_values)
            pre_attention_mask = pre_attention_mask.repeat_interleave(batch_size, dim=0)
            
            emb = tokenizer(prompt_list, return_tensors="pt", padding=True)
            input_ids = emb["input_ids"][:, 1:-1]
            attention_mask = emb["attention_mask"][:, 1:-1]
            all_attention_mask = torch.cat([pre_attention_mask, attention_mask], dim=1)
            past_key_values = model(input_ids[:, :-1], attention_mask=all_attention_mask[:, :-1], past_key_values=past_key_values, use_cache=True, return_dict=True).past_key_values

            res = model.generate(
                input_ids[:, -1:],
                attention_mask=all_attention_mask,
                past_key_values=past_key_values,
                max_length=100,
                do_sample=True,
                temperature=0.7,
            )
            gen_res = tokenizer.batch_decode(res, skip_special_tokens=True)
        else:
            emb = tokenizer(prompt_list, return_tensors="pt", padding=True)
            input_ids = emb["input_ids"][:, 1:-1]
            attention_mask = emb["attention_mask"][:, 1:-1]
            past_key_values = model(input_ids[:, :-1], attention_mask=attention_mask[:, :-1], use_cache=True, return_dict=True).past_key_values

            res = model.generate(
                input_ids[:, -1:],
                attention_mask=attention_mask,
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
