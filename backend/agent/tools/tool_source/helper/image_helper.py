from PIL import Image
import io
import base64
import httpx
import logging

logger = logging.getLogger(__name__)


def get_mime_type_from_bytes(data: bytes) -> str:
    """Simple mime type detection from magic numbers"""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "image/gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    return "unknown"


def bytes_to_base64(data: bytes) -> str:
    # Supported types
    supported_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    mime_type = get_mime_type_from_bytes(data)

    logger.info(f"bytes_to_base64: Input mime_type={mime_type}, data length={len(data)}")

    # Log first few bytes for debugging
    data_preview = data[:50] if len(data) > 50 else data
    logger.debug(f"First bytes: {data_preview}")

    need_conversion = mime_type not in supported_types
    if need_conversion:
        try:
            image = Image.open(io.BytesIO(data))
            # Verify format
            detected_format = image.format
            logger.info(f"PIL detected format: {detected_format}")

            detected_mime = f"image/{detected_format.lower()}"

            if detected_mime in supported_types:
                mime_type = detected_mime
            else:
                # Convert to JPEG
                logger.info(f"Converting image from {detected_mime} to image/jpeg")
                buffer = io.BytesIO()
                if image.mode in ("RGBA", "LA"):
                    image = image.convert("RGB")
                image.save(buffer, format="JPEG")
                data = buffer.getvalue()
                mime_type = "image/jpeg"
        except Exception as e:
            logger.error(f"Failed to process image with PIL: {e}")
            logger.error(f"Data preview (first 100 bytes): {data[:100]}")
            # Check if it might be HTML or JSON error response
            try:
                text_preview = data[:200].decode('utf-8', errors='ignore')
                logger.error(f"Content as text: {text_preview}")
            except Exception as e:
                logger.error(f"Failed to decode content as text: {e}")
            raise ValueError(f"Cannot identify or process image data: {e}")

    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{b64}"


async def download_image_base64(url: str) -> str:
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        res = await client.get(url)
        res.raise_for_status()
        
        # Log response headers for debugging
        content_type = res.headers.get('content-type', '')
        content_length = res.headers.get('content-length', 'unknown')
        logger.info(f"Downloaded from {url}: content-type={content_type}, content-length={content_length}, actual_size={len(res.content)}")
        
        # Validate content-type if available (ignore parameters like charset)
        mime_part = content_type.split(';')[0].strip().lower() if content_type else ''
        if mime_part and not mime_part.startswith('image/'):
            logger.warning(f"Expected image but got content-type: {content_type}")
            # Log content preview for debugging
            try:
                text_preview = res.content[:500].decode('utf-8', errors='ignore')
                logger.warning(f"Response content preview: {text_preview}")
            except Exception as e:
                logger.error(f"Failed to decode content as text: {e}")
            raise ValueError(f"Invalid content-type for image: {content_type}")
        
        # Try to use content-type from header, otherwise let bytes_to_base64 detect it
        image_base64 = bytes_to_base64(res.content)
    return image_base64
