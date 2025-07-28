"""
Face Detection Service
"""
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FaceDetectionService:
    def __init__(self, cascade_path: str = "backend/models/haarcascade_frontalface_default.xml"):
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

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Create a white mask initially
            mask = np.ones(img.shape[:2], dtype="uint8") * 255

            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) == 0:
                logger.warning("No face detected in the image. Returning a full white mask.")
                # If no face is detected, we can't inpaint, so we return a full white mask.
                # This will cause the original image to be used.
            else:
                # Assuming one face, draw a black rectangle on the mask
                (x, y, w, h) = faces[0]
                cv2.rectangle(mask, (x, y), (x+w, y+h), (0, 0, 0), -1)

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