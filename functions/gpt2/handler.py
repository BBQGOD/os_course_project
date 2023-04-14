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
