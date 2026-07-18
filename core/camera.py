import cv2
import queue
import numpy as np
import traceback
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtGui import QImage
from core.recognition import RecognitionEngine
from deepface import DeepFace


class CameraManager(QObject):
    frame_ready = Signal(object)          # QImage
    recognition_result = Signal(dict)
    fps_updated = Signal(float)
    error = Signal(str)

    def __init__(self, recognition_engine: RecognitionEngine, camera_index=0, process_every=3):
        super().__init__()
        self.recognition = recognition_engine
        self.camera_index = camera_index
        self.process_every = process_every      # only analyse every N frames
        self.capture_thread = None
        self.recognition_thread = None
        self.frame_queue = queue.Queue(maxsize=5)
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        self.capture_thread = CaptureThread(self.camera_index, self.frame_queue)
        self.capture_thread.error.connect(self.on_error)
        self.recognition_thread = RecognitionThread(self.frame_queue, self.recognition, self.process_every)
        self.recognition_thread.frame_processed.connect(self.on_frame_processed)
        self.recognition_thread.error.connect(self.on_error)
        self.capture_thread.start()
        self.recognition_thread.start()

    def stop(self):
        self.running = False
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread.wait()
        if self.recognition_thread:
            self.recognition_thread.stop()
            self.recognition_thread.wait()

    def on_frame_processed(self, qimage):
        self.frame_ready.emit(qimage)

    def on_error(self, msg):
        self.error.emit(msg)


class CaptureThread(QThread):
    error = Signal(str)

    def __init__(self, camera_index, frame_queue):
        super().__init__()
        self.camera_index = camera_index
        self.frame_queue = frame_queue
        self._stop = False

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.error.emit(f"Cannot open camera index {self.camera_index}")
            return
        while not self._stop:
            ret, frame = cap.read()
            if not ret:
                continue
            # If queue is full, drop the oldest frame to avoid lag
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            self.frame_queue.put(frame)
            self.msleep(10)
        cap.release()

    def stop(self):
        self._stop = True


class RecognitionThread(QThread):
    frame_processed = Signal(object)
    error = Signal(str)

    def __init__(self, frame_queue, recognition_engine, skip_frames):
        super().__init__()
        self.frame_queue = frame_queue
        self.recognition = recognition_engine
        self.skip_frames = skip_frames
        self._stop = False
        self.frame_cnt = 0
        self.error_shown = False          # only show first error

    def run(self):
        while not self._stop:
            try:
                frame = self.frame_queue.get(timeout=1)
            except queue.Empty:
                continue

            self.frame_cnt += 1
            if self.frame_cnt % self.skip_frames != 0:
                continue

            # Always create a copy for drawing, even if recognition fails
            display_frame = frame.copy()

            try:
                faces = DeepFace.extract_faces(
                    img_path=frame,
                    target_size=(160, 160),
                    detector_backend='opencv',
                    enforce_detection=False
                )
            except Exception as e:
                if not self.error_shown:
                    self.error.emit(f"Face detection error: {e}")
                    self.error_shown = True
                faces = []

            for face_obj in faces:
                facial_area = face_obj['facial_area']
                x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
                face_img = face_obj['face']

                try:
                    embedding_objs = DeepFace.represent(
                        img_path=face_img,
                        model_name='Facenet',
                        enforce_detection=False,
                        detector_backend='skip'
                    )
                    if embedding_objs:
                        encoding = np.array(embedding_objs[0]['embedding'])
                        sid, name, conf = self.recognition.recognize(encoding)
                        label = f"{name} ({sid}) {conf:.2f}" if sid else "UNKNOWN"
                        color = (0, 255, 0) if sid else (0, 0, 255)
                    else:
                        label = "UNKNOWN"
                        color = (0, 0, 255)
                except Exception:
                    label = "ERROR"
                    color = (0, 0, 255)

                cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(display_frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Always emit the frame
            h, w, ch = display_frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(display_frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
            self.frame_processed.emit(qt_img.copy())

    def stop(self):
        self._stop = True