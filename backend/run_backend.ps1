$env:PYTHONPATH = "d:\Project\Doctor-Scheduling-System\backend"
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
