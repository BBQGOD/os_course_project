import json
import sys
import torch
from transformers import BertTokenizer, GPT2LMHeadModel, TextGenerationPipeline

def prep(model_path):
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = GPT2LMHeadModel.from_pretrained(model_path)
    text_generator = TextGenerationPipeline(model, tokenizer)
    return text_generator, tokenizer, model

def handle(event, context):
    # text_generator = prep("uer/gpt2-distil-chinese-cluecorpussmall")
    text_generator, tokenizer, model = prep("function/hf_gpt2")

    if event.method == "GET":
        try:
            json_data = json.loads(event.body)
            batch_size = json_data["batch_size"]
            prefix = json_data["prefix"]
            prompt_list = json_data["prompt_list"]

            pre_emb = tokenizer(prefix, return_tensors="pt")
            pre_input_ids = pre_emb["input_ids"][:, :-1]
            pre_attention_mask = pre_emb["attention_mask"][:, :-1]
            past_key_values = model(pre_input_ids, attention_mask=pre_attention_mask, use_cache=True, return_dict=True).past_key_values
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

        except:
            gen_res = text_generator(
                event.body.decode(),
                max_length=100,
                do_sample=True,
                temperature=0.7,
            )[0]["generated_text"]
    else:
        gen_res = "Only support GET method."

    return {
        "statusCode": 200,
        "body": gen_res
    }
