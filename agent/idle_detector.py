import time
import requests
from pynput import mouse, keyboard
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000/log-event/"
IDLE_THRESHOLD = 300 # 5 minutes (300 seconds)

class IdleDetector:
    def __init__(self):
        self.last_activity_time = time.time()
        self.is_idle = False

    def on_activity(self, *args):
        # Jab bhi mouse move ho ya key press ho, timer reset hoga
        if self.is_idle:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] User returned! Sending RESUME...")
            requests.post(f"{API_URL}?event_type=RESUME&source=idle_system")
            self.is_idle = False
        
        self.last_activity_time = time.time()

    def start_monitoring(self):
        # Mouse aur Keyboard listeners start karna
        mouse_listener = mouse.Listener(on_move=self.on_activity, on_click=self.on_activity, on_scroll=self.on_activity)
        key_listener = keyboard.Listener(on_press=self.on_activity)
        
        mouse_listener.start()
        key_listener.start()

        print(f"Monitoring started. Idle threshold: {IDLE_THRESHOLD} seconds.")

        while True:
            current_idle_time = time.time() - self.last_activity_time
            
            if current_idle_time > IDLE_THRESHOLD and not self.is_idle:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Idle detected! Sending PAUSE...")
                requests.post(f"{API_URL}?event_type=PAUSE&source=idle_system")
                self.is_idle = True
            
            time.sleep(5) # Har 5 second mein check karega

if __name__ == "__main__":
    detector = IdleDetector()
    detector.start_monitoring()