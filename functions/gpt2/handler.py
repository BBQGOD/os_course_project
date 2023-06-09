import json
from transformers import BertTokenizer, GPT2LMHeadModel, TextGenerationPipeline

def prep(model_path):
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = GPT2LMHeadModel.from_pretrained(model_path)
    text_generator = TextGenerationPipeline(model, tokenizer)
    return text_generator

def handle(event, context):
    # text_generator = prep("uer/gpt2-distil-chinese-cluecorpussmall")
    text_generator = prep("function/hf_gpt2")

    if event.method == "GET":
        try:
            json_data = json.loads(event.body)
            batch_size = json_data["batch_size"]
            prompt_list = json_data["prompt_list"]

            res = text_generator(
                prompt_list,
                max_length=100,
                do_sample=True,
                temperature=0.7,
                batch_size=batch_size,
            )
            
            gen_res = []
            for i in range(len(res)):
                gen_res.append(res[i][0]["generated_text"])

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
