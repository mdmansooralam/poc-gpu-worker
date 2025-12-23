import os
import torch
import tempfile
from sqlalchemy.orm import Session
from utils.upload_pil_image import upload_pil_image

from sdxl import get_pipe
from models.jobs import Job, JobStatus


def generate_and_store_image(
    *,
    job_id: str,
    prompt: str,
    resolution: str,
    photorealistic: bool,
    db: Session
):
    tmp_path = None

    try:
        # 1️⃣ Parse resolution
        width, height = map(int, resolution.split("x"))

        # 2️⃣ Build final prompt
        final_prompt = prompt
        if photorealistic:
            final_prompt += ", ultra realistic, photorealistic, sharp focus, 8k"

        # 3️⃣ Generate image (GPU)
        with torch.inference_mode():
            pipe = get_pipe()
            image = pipe(
                prompt=final_prompt,
                width=width,
                height=height,
                num_inference_steps=30,
                guidance_scale=7.5
            ).images[0]

        # 4️⃣ Save image to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name

        # 5️⃣ Upload to Cloudinary

        image_url = upload_pil_image(image=image, public_id=job_id)

        # 6️⃣ Update DB
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            raise Exception("Job not found")

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

        job = db.query(Job).filter(Job.job_id == job_id).first()
        if job:
            job.status = JobStatus.failed
            db.commit()

        raise e

    finally:
        # 7️⃣ Cleanup temp file
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
