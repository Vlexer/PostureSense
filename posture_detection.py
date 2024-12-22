import cv2
import mediapipe as mp
import numpy as np
import math
from tkinter import messagebox
import threading
import time
import os
import csv
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageTk
import webbrowser
import json
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 
          'https://www.googleapis.com/auth/userinfo.email']
import utils        
BAD_POSTURE_THRESHOLD = 30
camera_active = False
POSTURE_DATA_FILE = "posture_data.csv"
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
def get_google_auth():
    try:
        # Load credentials from your client_secret.json file
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',  # Download this from Google Cloud Console
            SCOPES
        )
        # Open browser for authentication
        credentials = flow.run_local_server(port=0)
        
        # Now use these credentials to get user info
        user_info = get_user_info(credentials)
        return user_info
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return None
def send_email(user_email, user_name):
    sender_email = "kpsivasubramani5@gmail.com"
    sender_password = "hvyn ctex yjov dspf"  # Use an app password if needed
    subject = "Posture Alert: Slouching Detected"

    # Email content
    body = f"""
    Hi {user_name},
    
    We noticed that you've been slouching for an extended period. Maintaining good posture is crucial for your health. Please take a moment to sit up straight and realign your posture.
    
    Stay healthy,
    Posture Sense Team
    """

    # Set up email structure
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = user_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Replace with your SMTP server
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
# Function to log posture data
def get_google_credentials():
    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return credentials
def log_posture_data(neck_angle, shoulder_angle, posture_status, timestamp):
    if not os.path.exists(POSTURE_DATA_FILE):
        with open(POSTURE_DATA_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Neck Angle", "Shoulder Angle", "Posture Status"])

    with open(POSTURE_DATA_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, neck_angle, shoulder_angle, posture_status])


def summarize_posture_data():
    data = {"dates": {}, "total_time": 0, "good_posture_time": 0, "bad_posture_time": 0}
    if not os.path.exists(POSTURE_DATA_FILE):
        return data

    with open(POSTURE_DATA_FILE, "r") as file:
        reader = csv.DictReader(file)
        last_timestamp = None
        last_posture_status = None

        for row in reader:
            current_timestamp = float(row["Timestamp"])
            current_date = datetime.datetime.fromtimestamp(current_timestamp).strftime("%Y-%m-%d")
            current_status = row["Posture Status"]

            if current_date not in data["dates"]:
                data["dates"][current_date] = {"good_posture": 0, "bad_posture": 0}

            if last_timestamp is not None:
                time_diff = current_timestamp - last_timestamp
                data["total_time"] += time_diff
                if last_posture_status == "Good Posture":
                    data["good_posture_time"] += time_diff
                    data["dates"][current_date]["good_posture"] += time_diff
                else:
                    data["bad_posture_time"] += time_diff
                    data["dates"][current_date]["bad_posture"] += time_diff

            last_timestamp = current_timestamp
            last_posture_status = current_status

    return data
def calculate_posture_statistics():
    good_posture_time = 0
    bad_posture_time = 0
    last_timestamp = None
    last_posture_status = None

    if not os.path.exists(POSTURE_DATA_FILE):
        return good_posture_time, bad_posture_time

    with open(POSTURE_DATA_FILE, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            current_timestamp = float(row["Timestamp"])
            current_status = row["Posture Status"]

            if last_timestamp is not None:
                time_diff = current_timestamp - last_timestamp
                if last_posture_status == "Good Posture":
                    good_posture_time += time_diff
                else:
                    bad_posture_time += time_diff

            last_timestamp = current_timestamp
            last_posture_status = current_status

    return good_posture_time, bad_posture_time

# Adding a GUI button for showing statistics

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
def calculate_angle(point1, point2, point3):
    # Calculate vectors
    vector1 = [point1[0] - point2[0], point1[1] - point2[1]]
    vector2 = [point3[0] - point2[0], point3[1] - point2[1]]
    
    # Calculate magnitudes
    magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
    magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    # Calculate dot product
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    
    # Clip the cosine value to the range [-1, 1] to avoid math domain error
    cos_theta = max(-1, min(1, dot_product / (magnitude1 * magnitude2)))
    
    # Calculate angle in radians and convert to degrees
    angle_radians = math.acos(cos_theta)
    return math.degrees(angle_radians)

# Global variables
camera_visible = False
bad_posture_start_time = None
snooze_until = 0  # Time until which alerts are snoozed

# Function to calculate neck angle
def calculate_neck_angle(midpoint_shoulders, midpoint_ears):
    return calculate_angle(midpoint_shoulders, midpoint_ears, (midpoint_shoulders[0], midpoint_shoulders[1] - 50))

# Function to calculate shoulder angle
def calculate_shoulder_angle(left_shoulder, right_shoulder, left_hip, right_hip):
    midpoint_hips = ((left_hip[0] + right_hip[0]) // 2, (left_hip[1] + right_hip[1]) // 2)
    midpoint_shoulders = ((left_shoulder[0] + right_shoulder[0]) // 2, (left_shoulder[1] + right_shoulder[1]) // 2)
    return calculate_angle(midpoint_hips, midpoint_shoulders, (midpoint_hips[0], midpoint_hips[1] - 50))

#     alert.mainloop()
from tkinter.font import Font
import pygame
def show_alert(body_part):
    global snooze_until
    
    def play_sound():
        try:
            pygame.mixer.init()
            pygame.mixer.music.load('notify.mp3')
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error playing sound: {e}")
            import winsound
            winsound.Beep(1000, 3000)
    
    def snooze():
        global snooze_until
        snooze_until = time.time() + 300
        # Fade out animation
        fade_out()
    
    def fade_in():
        alpha = 0.0
        while alpha < 1.0:
            alpha += 0.1
            alert.attributes('-alpha', alpha)
            alert.update()
            time.sleep(0.05)
    
    def fade_out():
        alpha = 1.0
        while alpha > 0:
            alpha -= 0.1
            alert.attributes('-alpha', alpha)
            alert.update()
            time.sleep(0.05)
        alert.destroy()
    
    def on_enter(button):
        button.configure(bg="#1a73e8")
    
    def on_leave(button):
        button.configure(bg="#2196f3")
    
    # Create main window
    alert = tk.Tk()
    alert.title("")  # Remove title bar text
    alert.geometry("400x300")
    
    # Make window appear on top
    alert.lift()
    alert.attributes("-topmost", True)
    
    # Set window background
    alert.configure(bg="#1e1e1e")
    
    # Remove window border (optional, comment out if you want window controls)
    # alert.overrideredirect(True)
    
    # Center the window on screen
    screen_width = alert.winfo_screenwidth()
    screen_height = alert.winfo_screenheight()
    x = (screen_width - 400) // 2
    y = (screen_height - 300) // 2
    alert.geometry(f"400x300+{x}+{y}")
    
    # Create gradient effect (simulate with multiple frames)
    gradient_frame = tk.Frame(alert, bg="#1e1e1e", height=300, width=400)
    gradient_frame.pack(fill="both", expand=True)
    
    # Add icon/image (replace path with your icon)
    try:
        icon = tk.PhotoImage(file="posture.jpg")
        icon_label = tk.Label(gradient_frame, image=icon, bg="#1e1e1e")
        icon_label.image = icon  # Keep a reference
        icon_label.pack(pady=(20, 0))
    except:
        pass  # Skip if image not found
    
    # Title with custom font
    title_font = Font(family="Helvetica", size=24, weight="bold")
    title = tk.Label(
        gradient_frame,
        text="Posture Check!",
        font=title_font,
        fg="#ffffff",
        bg="#1e1e1e"
    )
    title.pack(pady=(20, 0))
    
    # Message with custom font
    message_font = Font(family="Helvetica", size=14)
    message = tk.Label(
        gradient_frame,
        text=f"Time to fix your {body_part} posture",
        font=message_font,
        fg="#e0e0e0",
        bg="#1e1e1e",
        wraplength=350
    )
    message.pack(pady=(10, 20))
    
    # Button styles
    button_font = Font(family="Helvetica", size=12, weight="bold")
    button_style = {
        "font": button_font,
        "borderwidth": 0,
        "highlightthickness": 0,
        "padx": 20,
        "pady": 10,
        "cursor": "hand2"
    }
    
    # Buttons frame
    buttons_frame = tk.Frame(gradient_frame, bg="#1e1e1e")
    buttons_frame.pack(pady=20)
    
    # Snooze button
    snooze_btn = tk.Button(
        buttons_frame,
        text="Snooze (5m)",
        command=snooze,
        bg="#2196f3",
        fg="white",
        **button_style
    )
    snooze_btn.pack(side=tk.LEFT, padx=10)
    snooze_btn.bind("<Enter>", lambda e: on_enter(snooze_btn))
    snooze_btn.bind("<Leave>", lambda e: on_leave(snooze_btn))
    
    # OK button
    ok_btn = tk.Button(
        buttons_frame,
        text="Got it!",
        command=lambda: fade_out(),
        bg="#4caf50",
        fg="white",
        **button_style
    )
    ok_btn.pack(side=tk.LEFT, padx=10)
    ok_btn.bind("<Enter>", lambda e: on_enter(ok_btn))
    ok_btn.bind("<Leave>", lambda e: on_leave(ok_btn))
    
    # Play sound
    play_sound()
    
    # Start fade in animation
    alert.attributes('-alpha', 0.0)
    fade_in()
    
    # Email notification in background
    try:
        with open('user_data.json', 'r') as file:
            user_data = json.load(file)
            user_email = user_data.get('email')
            user_name = user_data.get('username')

        if user_email and user_name:
            email_thread = threading.Thread(
                target=send_email,
                args=(user_email, user_name)
            )
            email_thread.start()
    except Exception as e:
        print(f"Error with email notification: {e}")
    
    alert.mainloop()
def get_user_info(credentials):
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture')
        }
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None
# Posture Detection Function (Show Camera)
def start_posture_detection():
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)
    # Thresholds for posture evaluation
    neck_threshold = 0.5
    shoulder_threshold = 0.7
    alignment_threshold = 20  # Nose-shoulder alignment threshold in pixels
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            # Get landmark positions
            try:
                left_shoulder = (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1]),
                                int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]))
                right_shoulder = (int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1]),
                                int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]))
                left_ear = (int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x * frame.shape[1]),
                            int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y * frame.shape[0]))
                right_ear = (int(landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x * frame.shape[1]),
                            int(landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].y * frame.shape[0]))
                left_hip = (int(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * frame.shape[1]),
                            int(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * frame.shape[0]))
                right_hip = (int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x * frame.shape[1]),
                            int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y * frame.shape[0]))
                nose = (int(landmarks[mp_pose.PoseLandmark.NOSE.value].x * frame.shape[1]),
                        int(landmarks[mp_pose.PoseLandmark.NOSE.value].y * frame.shape[0]))
                # Calculate midpoints
                midpoint_shoulders = ((left_shoulder[0] + right_shoulder[0]) // 2,
                                    (left_shoulder[1] + right_shoulder[1]) // 2)
                midpoint_ears = ((left_ear[0] + right_ear[0]) // 2,
                                (left_ear[1] + right_ear[1]) // 2)
                # Calculate angles
                neck_angle = calculate_neck_angle(midpoint_shoulders, midpoint_ears)
                shoulder_angle = calculate_shoulder_angle(left_shoulder, right_shoulder, left_hip, right_hip)
                # Draw landmarks on frame
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                # Determine posture status based on thresholds
                neck_status = "Good Posture" if abs(neck_angle - neck_threshold) <= 0.5 else "Poor Posture - Forward Neck"
                shoulder_status = "Good Posture" if abs(shoulder_angle - shoulder_threshold) <= 0.6 else "Poor Posture - Rounded Shoulders"
                # Check nose-shoulder alignment
                if abs(nose[0] - midpoint_shoulders[0]) <= alignment_threshold:
                    alignment_status = "Good Posture - Nose Aligned"
                    alignment_color = (0, 255, 0)
                else:
                    alignment_status = "Poor Posture - Misaligned Nose"
                    alignment_color = (0, 0, 255)
                # Display status for neck, shoulder, and alignment
                
                cv2.putText(frame, neck_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 0) if neck_status == "Good Posture" else (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, f"Neck Angle: {neck_angle:.1f}/{neck_threshold:.1f}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

                cv2.putText(frame, shoulder_status, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 0) if shoulder_status == "Good Posture" else (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, f"Shoulder Angle: {shoulder_angle:.1f}/{shoulder_threshold:.1f}", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                # Display alignment status
                cv2.putText(frame, alignment_status, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, alignment_color, 2, cv2.LINE_AA)
                # ---------------------------------#
                
            except Exception as e:
                
                print(f"Error processing landmarks: {e}")
        else:
            print("No pose landmarks detected.")
        # Display the frame
        cv2.imshow('Posture Corrector', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


# Background Posture Detection (No Camera)
def detect_posture_in_background():
    messagebox.showinfo("Posture Detection", "Posture detection is running in the background.")
    global camera_active
    camera_active = True
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)

    while camera_active and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        
        # Placeholder: Process frame logic
        process_frame(frame, pose)

    cap.release()
    print("Camera closed.")



def start_background_detection():
    global camera_active
    if camera_active:
        messagebox.showinfo("Camera Active", "The camera is already running.")
        return

    # Start the camera in a separate thread
    threading.Thread(target=detect_posture_in_background, daemon=True).start()
    # update_indicator(True)


def process_frame(frame, pose):
    global bad_posture_start_time, snooze_until
    mp_pose = mp.solutions.pose
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        try:
            # Get landmark positions
            left_shoulder = (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1]),
                           int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]))
            right_shoulder = (int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1]),
                            int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]))
            left_ear = (int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x * frame.shape[1]),
                       int(landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y * frame.shape[0]))
            right_ear = (int(landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x * frame.shape[1]),
                        int(landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].y * frame.shape[0]))
            left_hip = (int(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * frame.shape[1]),
                       int(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * frame.shape[0]))
            right_hip = (int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x * frame.shape[1]),
                        int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y * frame.shape[0]))
            nose = (int(landmarks[mp_pose.PoseLandmark.NOSE.value].x * frame.shape[1]),
                   int(landmarks[mp_pose.PoseLandmark.NOSE.value].y * frame.shape[0]))
            
            # Calculate midpoints
            midpoint_shoulders = ((left_shoulder[0] + right_shoulder[0]) // 2,
                                (left_shoulder[1] + right_shoulder[1]) // 2)
            midpoint_ears = ((left_ear[0] + right_ear[0]) // 2,
                           (left_ear[1] + right_ear[1]) // 2)
            
            # Calculate angles and alignment
            neck_angle = calculate_neck_angle(midpoint_shoulders, midpoint_ears)
            shoulder_angle = calculate_shoulder_angle(left_shoulder, right_shoulder, left_hip, right_hip)
            nose_shoulder_offset = abs(nose[0] - midpoint_shoulders[0])
            
            # Define thresholds
            NECK_THRESHOLD = 25  # degrees from vertical
            SHOULDER_THRESHOLD = 25  # degrees from vertical
            ALIGNMENT_THRESHOLD = 30  # pixels
            
            # Check individual posture components
            is_neck_good = abs(90 - neck_angle) <= NECK_THRESHOLD
            is_shoulders_good = abs(90 - shoulder_angle) <= SHOULDER_THRESHOLD
            is_aligned = nose_shoulder_offset <= ALIGNMENT_THRESHOLD
            
            # Determine overall posture status (good if at least one measure is good)
            is_good_posture = is_neck_good or is_shoulders_good or is_aligned
            posture_status = "Good Posture" if is_good_posture else "Bad Posture"
            
            # Log the data
            current_timestamp = time.time()
            log_posture_data(neck_angle, shoulder_angle, posture_status, current_timestamp)
            
            # Draw landmarks and display status
            if hasattr(frame, 'shape'):  # Check if we're in display mode
                mp_drawing = mp.solutions.drawing_utils
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                # Display detailed status
                cv2.putText(frame, f"Overall: {posture_status}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, 
                           (0, 255, 0) if is_good_posture else (0, 0, 255), 2)
                
                cv2.putText(frame, f"Neck: {'Good' if is_neck_good else 'Poor'} ({neck_angle:.1f}°)", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                           (0, 255, 0) if is_neck_good else (0, 0, 255), 1)
                
                cv2.putText(frame, f"Shoulders: {'Good' if is_shoulders_good else 'Poor'} ({shoulder_angle:.1f}°)", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                           (0, 255, 0) if is_shoulders_good else (0, 0, 255), 1)
                
                cv2.putText(frame, f"Alignment: {'Good' if is_aligned else 'Poor'} ({nose_shoulder_offset:.1f}px)", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                           (0, 255, 0) if is_aligned else (0, 0, 255), 1)
            neck_threshold = 1
            shoulder_threshold = 0.7
            alignment_threshold = 20 
            # Handle alerts for consistently bad posture
            if not is_good_posture and time.time() > snooze_until:
                if bad_posture_start_time is None:
                    bad_posture_start_time = time.time()
                elif time.time() - bad_posture_start_time >= 30:  # Alert after 30 seconds of bad posture
                    message = []
                    if not is_neck_good:
                        message.append("neck")
                    if not is_shoulders_good:
                        message.append("shoulders")
                    if not is_aligned:
                        message.append("alignment")
                    show_alert(" and ".join(message))
                    bad_posture_start_time = None
                is_neck_bad = abs(neck_angle - neck_threshold) > 0.5
                is_shoulders_bad = abs(shoulder_angle - shoulder_threshold) > 0.6
                is_misaligned = abs(nose[0] - midpoint_shoulders[0]) > alignment_threshold

                # Trigger bad posture start time
                
                #-------------------------#


                # Setup logging to debug issues
                

                
            else:
                bad_posture_start_time = None
                
        except Exception as e:
            print(f"Error processing landmarks: {e}")
            
    return frame  # Return the processed frame

# GUI
