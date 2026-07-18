import os
import sys
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / 'database'
PHOTOS_DIR = BASE_DIR / 'photos'
EXPORTS_DIR = BASE_DIR / 'exports'
LOGS_DIR = BASE_DIR / 'logs'

# Ensure directories exist
for dir_path in (DATABASE_DIR, PHOTOS_DIR, EXPORTS_DIR, LOGS_DIR):
    dir_path.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'attendance.db'}"

# Default settings
DEFAULT_CAMERA_INDEX = 0
DEFAULT_RECOGNITION_THRESHOLD = 0.5   # Lower = stricter
DEFAULT_THEME = 'dark'
LOG_FILE = LOGS_DIR / 'visionattend.log'
LOG_LEVEL = 'INFO'