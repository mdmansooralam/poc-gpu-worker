import io
import cloudinary
import cloudinary.uploader
from PIL import Image
from core.config import settings

# ===== ONE-TIME CONFIG =====
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
    Upload PIL Image to Cloudinary (in-memory) and return secure_url
    """

    # Convert PIL image to bytes
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # Upload directly from memory
    result = cloudinary.uploader.upload(
        buffer,
        folder=folder,
        public_id=public_id,
        overwrite=True,
        resource_type="image"
    )

    return result["secure_url"]
