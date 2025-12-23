import cloudinary
import cloudinary.uploader
import tempfile
import os
from PIL import Image
from core.config import settings

# ✅ ONE-TIME CONFIG (this part of yours is correct)
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


def upload_pil_image(
    *,
    image: Image.Image,
    public_id: str,
    folder: str = "sdxl_jobs"
) -> str:
    """
    Upload PIL Image to Cloudinary and return secure_url
    """
    tmp_path = None

    try:
        # Save PIL image to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            tmp_path,
            folder=folder,
            public_id=public_id,
            overwrite=True,
            resource_type="image"
        )

        return result.get("secure_url")

    finally:
        # Cleanup
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
