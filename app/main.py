from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, TimeLog, get_db
from datetime import datetime

# Database tables create karne ke liye (agar nahi bane toh)
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Work Tracker API is running"}

@app.post("/log-event/")
def log_event(event_type: str, source: str = "manual", db: Session = Depends(get_db)):
    # Naya log entry create karna
    new_log = TimeLog(
        event_type=event_type.upper(),
        source=source,
        timestamp=datetime.now()
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return {"message": f"Event {event_type} logged successfully", "id": new_log.id}

@app.get("/get-summary/")
def get_summary(db: Session = Depends(get_db)):
    logs = db.query(TimeLog).order_by(TimeLog.timestamp).all()
    
    total_work_seconds = 0
    total_break_seconds = 0
    last_event_time = None
    last_event_type = None

    for log in logs:
        if last_event_time is not None:
            duration = (log.timestamp - last_event_time).total_seconds()
            if last_event_type in ["START", "RESUME"]:
                total_work_seconds += duration
            elif last_event_type == "PAUSE":
                total_break_seconds += duration
        
        last_event_time = log.timestamp
        last_event_type = log.event_type

    # Naya logic: Current status aur last timestamp bhej rahe hain live timer ke liye
    return {
        "total_work_hours": round(total_work_seconds / 3600, 2),
        "total_work_minutes": round(total_work_seconds / 60, 2),
        "total_break_hours": round(total_break_seconds / 3600, 2),
        "total_break_minutes": round(total_break_seconds / 60, 2),
        "last_event_type": last_event_type,
        "last_event_timestamp": last_event_time.isoformat() if last_event_time else None,
        "raw_logs_count": len(logs)
    }
    
@app.get("/get-logs/")
def get_logs(db: Session = Depends(get_db)):
    # Saare logs ko latest time ke hisaab se fetch karna
    logs = db.query(TimeLog).order_by(TimeLog.timestamp.desc()).all()
    return logs