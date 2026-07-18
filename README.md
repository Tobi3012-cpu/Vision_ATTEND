# VisionAttend AI

AI‑powered face recognition attendance system for schools, universities and offices.

## Features
- Administrator login with secure password hashing
- Student management (CRUD, import/export Excel)
- Face registration with quality check
- Real‑time face recognition with bounding boxes
- Automatic attendance marking (no duplicates)
- Reports: daily/weekly/monthly PDF, Excel, CSV
- Modern dark/light UI, statistics dashboard
- Camera selection, threshold settings, backup/restore

## Installation
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Run: `python app.py`

## Usage
- Default admin credentials: admin / admin (create via database if not present)
- Use the sidebar to navigate.

## Database Schema
Tables: users, students, embeddings, attendance, logs, settings

## License
MIT