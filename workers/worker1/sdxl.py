_pipe = None

def get_pipe():
    global _pipe
    if _pipe is None:
        from diffusers import StableDiffusionXLPipeline
        import torch

        _pipe = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16,
            use_safetensors=True
        )
        _pipe.to("cuda")
        _pipe.enable_attention_slicing()
    return _pipe
