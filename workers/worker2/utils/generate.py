import os
import torch
from sqlalchemy.orm import Session

from utils.upload_pil_image import upload_pil_image
from sdxl import get_pipe
from models.jobs import Job, JobStatus


# ===== SDXL PIPE SINGLETON =====
_PIPE = None


def _get_pipe_singleton():
    global _PIPE
    if _PIPE is None:
        _PIPE = get_pipe()
        _PIPE.to("cuda")
    return _PIPE


def generate_and_store_image(
    *,
    job_id: str,
    prompt: str,
    resolution: str,
    photorealistic: bool,
    db: Session
):
    try:
        # 1️⃣ Parse resolution
        width, height = map(int, resolution.split("x"))

        # 2️⃣ Build final prompt
        final_prompt = prompt
        if photorealistic:
            final_prompt += ", ultra realistic, photorealistic, sharp focus, 8k"

        # 3️⃣ Generate image (GPU)
        pipe = _get_pipe_singleton()

        with torch.inference_mode():
            image = pipe(
                prompt=final_prompt,
                width=width,
                height=height,
                num_inference_steps=30,
                guidance_scale=7.5
            ).images[0]

        # 4️⃣ Upload image
        image_url = upload_pil_image(image=image, public_id=job_id)

        # 5️⃣ Update DB
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            raise RuntimeError("Job not found")

        job.image_url = image_url
        job.status = JobStatus.completed
        db.commit()

        return {
            "status": "success",
            "job_id": job_id,
            "image_url": image_url
        }

    except Exception as e:
        db.rollback()

        try:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = JobStatus.failed
                db.commit()
        except Exception:
            pass  # avoid cascading failure

        raise

    finally:
        # 6️⃣ Free unused GPU memory
        torch.cuda.empty_cache()
