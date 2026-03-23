from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from .database import TimeLog as DBTimeLog


# Database tables create karne ke liye (agar nahi bane toh)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS SETTINGS (Green Signal for Streamlit) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Isse har jagah se request allow hogi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Pydantic Model: Incoming data ka structure check karne ke liye
class TimeLogSchema(BaseModel):
    event_type: str

@app.get("/")
def home():
    return {"status": "API is Online", "server": "Render"}

@app.post("/log-event/")
def log_event(data: TimeLogSchema, db: Session = Depends(get_db)):
    try:
        # Naya database entry create karna
        new_entry = DBTimeLog(
            event_type=data.event_type.upper(),
            source="agent", # Agent se aane wala data
            timestamp=datetime.now()
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return {"message": "Data saved successfully", "id": new_entry.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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
    
# Dashboard ke liye logs fetch karne wala endpoint
@app.get("/logs/")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(DBTimeLog).order_by(DBTimeLog.timestamp.desc()).limit(50).all()
    # Pydantic models ko JSON compatible banane ke liye list comprehension
    return [{"timestamp": l.timestamp.isoformat(), "event_type": l.event_type, "source": l.source} for l in logs]
