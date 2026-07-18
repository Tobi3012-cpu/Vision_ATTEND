import numpy as np
from sqlalchemy.orm import Session
from database.models import Embedding, Student
from core.face_encoder import bytes_to_embedding

class RecognitionEngine:
    def __init__(self, db_session: Session, threshold: float = 0.5):
        self.threshold = threshold
        self.db = db_session
        self.known_encodings = []
        self.known_student_ids = []
        self.known_names = []
        self.load_embeddings()

    def load_embeddings(self):
        self.known_encodings.clear()
        self.known_student_ids.clear()
        self.known_names.clear()
        embeddings = self.db.query(Embedding).all()
        for emb in embeddings:
            student = emb.student
            encoding = bytes_to_embedding(emb.embedding)
            self.known_encodings.append(encoding)
            self.known_student_ids.append(student.student_id)
            self.known_names.append(f"{student.first_name} {student.last_name}")

    @staticmethod
    def _cosine_distance(a, b):
        a, b = np.asarray(a), np.asarray(b)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 1.0
        return 1.0 - dot / (norm_a * norm_b)

    def recognize(self, face_encoding: np.ndarray):
        if not self.known_encodings:
            return None, None, 0.0
        distances = [self._cosine_distance(known, face_encoding) for known in self.known_encodings]
        best_idx = np.argmin(distances)
        if distances[best_idx] < self.threshold:
            confidence = 1.0 - distances[best_idx]
            return (self.known_student_ids[best_idx],
                    self.known_names[best_idx],
                    confidence)
        return None, None, 0.0