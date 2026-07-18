"""
Face encoding using DeepFace (supports multiple backends).
"""

import numpy as np
import cv2
import pickle
from deepface import DeepFace

def encode_face(image_path: str = None, image_array: np.ndarray = None) -> np.ndarray | None:
    """
    Returns a 128‑dim face embedding from an image.
    Works with either an image path or a numpy array (BGR).
    """
    if image_array is not None:
        # Convert BGR (OpenCV) to RGB
        img = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    elif image_path is not None:
        img = image_path
    else:
        raise ValueError("Provide image_path or image_array")

    try:
        # Use 'Facenet' model (128d embeddings). You can change to 'OpenFace', 'VGG-Face', etc.
        embedding_objs = DeepFace.represent(
            img_path=img,
            model_name='Facenet',
            enforce_detection=True,
            detector_backend='opencv'
        )
        if not embedding_objs:
            return None
        return np.array(embedding_objs[0]['embedding'])
    except Exception:
        return None

def check_face_quality(image_array: np.ndarray) -> bool:
    """Reject blurry images using Laplacian variance."""
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() > 100

def embedding_to_bytes(embedding: np.ndarray) -> bytes:
    return pickle.dumps(embedding)

def bytes_to_embedding(data: bytes) -> np.ndarray:
    return pickle.loads(data)