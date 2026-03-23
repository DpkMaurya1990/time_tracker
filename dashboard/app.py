import streamlit as st
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pandas as pd

# Har 1 second mein page refresh hoga live timer ke liye
st_autorefresh(interval=1000, key="timer_refresh")

API_URL = "https://time-tracker-n9cl.onrender.com"
SUMMARY_URL = "https://time-tracker-n9cl.onrender.com/get-summary/"

st.title("⏱️ AI Work Tracker")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("▶️ Start Work", use_container_width=True):
        requests.post(f"{API_URL}?event_type=START")
with col2:
    if st.button("⏸️ Take Break", use_container_width=True):
        requests.post(f"{API_URL}?event_type=PAUSE")
with col3:
    if st.button("⏹️ Stop/End Day", use_container_width=True):
        requests.post(f"{API_URL}?event_type=STOP")

st.divider()

try:
    res = requests.get(SUMMARY_URL)
    if res.status_code == 200:
        data = res.json()
        
        # --- LIVE TIMER LOGIC ---
        if data["last_event_timestamp"] and data["last_event_type"] != "STOP":
            last_ts = datetime.fromisoformat(data["last_event_timestamp"])
            live_duration = (datetime.now() - last_ts).total_seconds()
            
            # Format seconds to HH:MM:SS
            hours, rem = divmod(int(live_duration), 3600)
            mins, secs = divmod(rem, 60)
            time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
            
            if data["last_event_type"] in ["START", "RESUME"]:
                st.subheader(f"🟢 Currently Working: `{time_str}`")
            else:
                st.subheader(f"🟡 On Break: `{time_str}`")
        # -------------------------

        m1, m2, m3 = st.columns(3)
        # Hours aur Minutes dono dikhane ke liye label update kiya hai
        m1.metric("Total Work", f"{data['total_work_hours']} hrs", f"{data['total_work_minutes']} mins")
        m2.metric("Total Break", f"{data['total_break_hours']} hrs", f"{data['total_break_minutes']} mins")
        m3.metric("Events", data['raw_logs_count'])
        
        # Progress Bar (Goal: 8 hours)
        st.write("---")
        goal = 8.0
        progress = min(data['total_work_hours'] / goal, 1.0)
        st.write(f"🎯 Daily Goal Progress: **{int(progress*100)}%** ({data['total_work_hours']} / {goal} hrs)")
        st.progress(progress)

        # Timeline Table
        st.subheader("📜 Activity Timeline")
        logs_res = requests.get("http://127.0.0.1:8000/get-logs/")
        if logs_res.status_code == 200:
            logs_list = logs_res.json()
            if logs_list:
                df = pd.DataFrame(logs_list)
                # Formatting Time for display
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
                st.dataframe(df[['timestamp', 'event_type', 'source']], use_container_width=True)
                
        # --- CSV EXPORT LOGIC ---
                st.write("") # Thoda space dene ke liye
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Daily Report (CSV)",
                    data=csv,
                    file_name=f"work_report_{datetime.now().strftime('%Y-%m-%d')}.csv",
                    mime='text/csv',
                    use_container_width=True
                )        

except Exception as e:
    st.error("API is offline!")