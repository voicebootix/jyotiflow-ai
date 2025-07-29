"""
Face Detection Service
"""
import cv2
import numpy as np
import logging
import os
from pathlib import Path

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
        logger.info(f"Does cascade file exist at path? {os.path.exists(cascade_path)}")

        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            logger.error(f"Failed to load Haar Cascade model from {cascade_path}")
            raise IOError(f"Failed to load Haar Cascade model from {cascade_path}")

    def create_face_mask(self, image_bytes: bytes) -> bytes:
        """
        Detects a face in an image and creates a black and white mask.
        The face area is black, and the rest is white.
        """
        try:
            # Decode image from bytes
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.error("Failed to decode image bytes.")
                raise ValueError("Invalid image bytes provided.")

            # REFRESH.MD: Ensure mask has the exact same dimensions as the input image.
            height, width, _ = img.shape
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # CORE.MD: Create a mask with the same dimensions as the original image.
            mask = np.ones((height, width), dtype="uint8") * 255 # White mask

            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) == 0:
                logger.warning("No face detected in the image. Returning a full white mask.")
                # If no face is detected, we can't inpaint, so we return a full white mask.
                # This will cause the original image to be used.
            else:
                # CORE.MD: Use an ellipse for a more natural face mask instead of a rectangle.
                (x, y, w, h) = faces[0]
                center_x = x + w // 2
                center_y = y + h // 2
                axis_x = w // 2
                axis_y = int(h * 0.6)  # Use a slightly larger vertical axis for better coverage
                cv2.ellipse(mask, (center_x, center_y), (axis_x, axis_y), 0, 0, 360, (0, 0, 0), -1)

            # Encode the mask to bytes
            is_success, buffer = cv2.imencode(".png", mask)
            if not is_success:
                logger.error("Failed to encode mask to png format.")
                raise RuntimeError("Failed to encode mask to png format.")

            return buffer.tobytes()

        except Exception as e:
            logger.error(f"Error creating face mask: {e}", exc_info=True)
            raise

def get_face_detection_service():
    """Dependency injector for FaceDetectionService."""
    return FaceDetectionService() 