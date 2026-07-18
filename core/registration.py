import cv2
import os
import uuid
from datetime import datetime
from core.face_encoder import encode_face, check_face_quality, embedding_to_bytes
from database.models import Student, Embedding
from config import PHOTOS_DIR

class RegistrationManager:
    def __init__(self, db_session, camera_index=0):
        self.db = db_session
        self.camera_index = camera_index

    def capture_faces(self, student_id: str, num_images: int = 30):
        """Capture multiple face images for a student, save embeddings."""
        student = self.db.query(Student).filter_by(student_id=student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found.")

        photo_dir = PHOTOS_DIR / student_id
        photo_dir.mkdir(exist_ok=True)

        cap = cv2.VideoCapture(self.camera_index)
        captured = 0
        while captured < num_images:
            ret, frame = cap.read()
            if not ret:
                continue
            # Detect faces using face_recognition for location
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb)
            if len(face_locations) != 1:
                continue  # skip if not exactly one face
            if not check_face_quality(frame):
                continue

            # Save photo
            img_name = f"{uuid.uuid4().hex}.jpg"
            img_path = photo_dir / img_name
            cv2.imwrite(str(img_path), frame)

            # Encode face
            encoding = encode_face(image_array=frame)
            if encoding is not None:
                emb_bytes = embedding_to_bytes(encoding)
                emb = Embedding(student_id=student.id, embedding=emb_bytes)
                self.db.add(emb)
                self.db.commit()
                captured += 1

        cap.release()
        # Update student photo path (first image)
        images = sorted(photo_dir.glob('*.jpg'))
        if images:
            student.photo_path = str(images[0])
            self.db.commit()
        return captured