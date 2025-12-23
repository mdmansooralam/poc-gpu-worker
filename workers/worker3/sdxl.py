_pipe = None


def get_pipe():
    global _pipe
    if _pipe is None:
        import torch
        from diffusers import StableDiffusionXLPipeline

        # ---- CUDA performance tuning ----
        torch.backends.cuda.matmul.allow_tf32 = True

        _pipe = StableDiffusionXLPipeline.from_pretrained(
            "/models/sdxl",                # 🔥 LOCAL PATH, NOT HF DOWNLOAD
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True
        )

        _pipe.to("cuda")

        # ---- Memory optimizations ----
        _pipe.enable_attention_slicing()
        _pipe.enable_vae_tiling()

    return _pipe
