import torch
from diffusers import StableDiffusionPipeline

def prep(model_path, device):
    # pipe = StableDiffusionPipeline.from_pretrained(model_path, torch_dtype=torch.float16, device_map=device)
    pipe = StableDiffusionPipeline.from_pretrained(model_path)
    pipe.enable_attention_slicing()
    return pipe

def handle(event, context):
    model_id = "function/SDv1-4"
    device = "auto"
    # device = "cpu"
    diffusion_pipe = prep(model_id, device)

    if event.method == "GET":
        image = diffusion_pipe(event.body.decode()).images[0]
        gen_res = "Success."
    else:
        gen_res = "Only support GET method."

    return {
        "statusCode": 200,
        "body": {
            "mode": image.mode,
            "size": image.size,
            "raw_bytes": image.tobytes().decode(),
            "gen_res": gen_res,
        }
    }
