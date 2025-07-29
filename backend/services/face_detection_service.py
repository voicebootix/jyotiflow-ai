"""
Face Detection Service
"""
import cv2
import numpy as np
import logging
import os
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

class FaceDetectionService:
    def __init__(self):
        # CORE.MD: Path to the Haar Cascade model is now constructed relative to this file's location.
        # This makes it robust to changes in the current working directory.
        base_dir = Path(__file__).resolve().parent.parent
        cascade_path = os.getenv("HAAR_CASCADE_PATH", str(base_dir / "models/haarcascade_frontalface_default.xml"))
        
        # REFRESH.MD: Add detailed logging to debug file path issues on Render.
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Calculated Haar Cascade path: {cascade_path}")
        
        # REFRESH.MD: Add explicit file existence and readability checks for robust debugging on Render.
        if not os.path.exists(cascade_path):
            logger.error(f"Haar Cascade model file NOT FOUND at the specified path: {cascade_path}")
            raise IOError(f"Haar Cascade model file not found at: {cascade_path}")
        
        try:
            # Check if the file is readable before passing to OpenCV, which gives vague errors.
            with open(cascade_path, 'rb') as f:
                pass
            logger.info("Haar Cascade model file is accessible and readable.")
        except OSError as e:
            logger.error(f"OS error while trying to read the Haar Cascade model file: {e}", exc_info=True)
            raise IOError(f"Could not read Haar Cascade model file due to OS error: {e}") from e

        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            logger.error(f"Failed to load Haar Cascade model from {cascade_path}. The file might be corrupted or not a valid OpenCV model.")
            raise IOError(f"Failed to load Haar Cascade model from {cascade_path}. File may be invalid.")

    def create_face_mask(self, image_bytes: bytes) -> Tuple[bytes, bytes]:
        """
        Decodes an image, resizes it to 1024x1024 for Stability.ai compatibility,
        detects a face, and creates a corresponding mask.

        Returns:
            A tuple containing (resized_image_bytes, mask_bytes).
        """
        try:
            # Decode image from bytes
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.error("Failed to decode image bytes.")
                raise ValueError("Invalid image bytes provided.")

            # REFRESH.MD: Resize image to the 1024x1024 requirement for the SDXL model.
            target_size = (1024, 1024)
            resized_img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
            
            # Create mask based on the resized image
            height, width, _ = resized_img.shape
            gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
            
            # CORE.MD: Create a mask with the same dimensions as the resized image.
            mask = np.ones((height, width), dtype="uint8") * 255 # White mask

            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) == 0:
                logger.warning("No face detected in the resized image. The mask will be all white.")
            else:
                # CORE.MD: Use an ellipse with axes as half the bounding box dimensions for a consistent fit.
                (x, y, w, h) = faces[0]
                center_x = x + w // 2
                center_y = y + h // 2
                axis_x = w // 2
                axis_y = h // 2
                cv2.ellipse(mask, (center_x, center_y), (axis_x, axis_y), 0, 0, 360, (0, 0, 0), -1)

            # Encode both the resized image and the mask to PNG bytes
            is_success_img, resized_img_buffer = cv2.imencode(".png", resized_img)
            if not is_success_img:
                logger.error("Failed to encode resized image to png format.")
                raise RuntimeError("Failed to encode resized image.")

            is_success_mask, mask_buffer = cv2.imencode(".png", mask)
            if not is_success_mask:
                logger.error("Failed to encode mask to png format.")
                raise RuntimeError("Failed to encode mask.")

            return resized_img_buffer.tobytes(), mask_buffer.tobytes()

        except Exception as e:
            logger.error(f"Error creating face mask: {e}", exc_info=True)
            raise

def get_face_detection_service():
    """Dependency injector for FaceDetectionService."""
    return FaceDetectionService() 