import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import face_recognition
import os
import numpy as np
from PIL import Image, ImageTk
import threading
from datetime import datetime
import pandas as pd
import pywhatkit as pwk
from tkinter import simpledialog
from tkinter import messagebox
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import pandas as pd
import pywhatkit as pwk
from datetime import datetime, timedelta



# Create the main window
root = tk.Tk()
root.geometry("800x600")
root.title("Face Recognition System")
root.configure(bg="#f0f0f0")

# Navigation bar setup
nav_bar = tk.Frame(root, bg="#333", height=50)
nav_bar.pack(side=tk.TOP, fill=tk.X)

# Logo on the left side of the navigation bar
logo_label = tk.Label(nav_bar, text="MyApp", bg="#333", fg="#fff", font=("Arial", 16, "bold"))
logo_label.pack(side=tk.LEFT, padx=10)

# Placeholder icons on the right side of the navigation bar
icon_frame = tk.Frame(nav_bar, bg="#333")
icon_frame.pack(side=tk.RIGHT)

# User and data icons
user_icon = tk.Label(icon_frame, text="👤", bg="#333", fg="#fff", font=("Arial", 16))
data_icon = tk.Label(icon_frame, text="📊", bg="#333", fg="#fff", font=("Arial", 16))
user_icon.pack(side=tk.RIGHT, padx=10)
data_icon.pack(side=tk.RIGHT, padx=10)

# Function to enable buttons after successful login
def enable_buttons():
    upload_button.config(state=tk.NORMAL)
    recognize_button.config(state=tk.NORMAL)

# Function to open login/signup window
def login_signup_window():
    login_window = tk.Toplevel(root)
    login_window.title("Login / Sign Up")
    login_window.geometry("400x300")
    login_window.configure(bg="#f0f0f0")

    # Login section
    login_label = tk.Label(login_window, text="Login", font=("Arial", 16, "bold"), bg="#f0f0f0")
    login_label.pack(pady=10)

    username_label = tk.Label(login_window, text="Username:", bg="#f0f0f0")
    username_label.pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    password_label = tk.Label(login_window, text="Password:", bg="#f0f0f0")
    password_label.pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    # Function to check login credentials
    def check_credentials():
        global logged_in
        username = username_entry.get()
        password = password_entry.get()
        user_file = os.path.join("data", f"{username}.txt")

        if os.path.exists(user_file):
            with open(user_file, "r") as f:
                saved_data = f.readlines()
                saved_username = saved_data[0].strip().split(": ")[1]
                saved_password = saved_data[1].strip().split(": ")[1]

                if username == saved_username and password == saved_password:
                    messagebox.showinfo("Login Success", "You have successfully logged in!")
                    logged_in = True
                    enable_buttons()
                    login_window.destroy()
                else:
                    messagebox.showerror("Error", "Invalid username or password")
        else:
            messagebox.showerror("Error", "Username does not exist")

    login_button = tk.Button(login_window, text="Login", command=check_credentials, bg="#007BFF", fg="#fff")
    login_button.pack(pady=10)

    # Sign Up section
    signup_label = tk.Label(login_window, text="Sign Up", font=("Arial", 16, "bold"), bg="#f0f0f0")
    signup_label.pack(pady=10)

    new_username_label = tk.Label(login_window, text="New Username:", bg="#f0f0f0")
    new_username_label.pack()
    new_username_entry = tk.Entry(login_window)
    new_username_entry.pack(pady=5)

    new_password_label = tk.Label(login_window, text="New Password:", bg="#f0f0f0")
    new_password_label.pack()
    new_password_entry = tk.Entry(login_window, show="*")
    new_password_entry.pack(pady=5)

    # Function to save username and password
    def save_credentials():
        new_username = new_username_entry.get()
        new_password = new_password_entry.get()

        if not new_username or not new_password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        if not os.path.exists("data"):
            os.makedirs("data")

        with open(os.path.join("data", f"{new_username}.txt"), "w") as f:
            f.write(f"Username: {new_username}\nPassword: {new_password}")

        messagebox.showinfo("Success", "Sign Up successful!")
        new_username_entry.delete(0, tk.END)
        new_password_entry.delete(0, tk.END)

    signup_button = tk.Button(login_window, text="Sign Up", command=save_credentials, bg="#28A745", fg="#fff")
    signup_button.pack(pady=10)

# Bind the function to the user icon click event
user_icon.bind("<Button-1>", lambda event: login_signup_window())

# Variables for name, roll-no, and count
name_var = tk.StringVar()
roll_no_var = tk.StringVar()
count_var = tk.StringVar(value="0")
total_recognized_faces = 0
recognized_names = set()
uploaded_image_path = "database"
database_path = "database"  # Added definition for database_path
known_face_encodings = []  # Initialize known face encodings
known_face_names = []  # Initialize known face names
logged_in = False  # Initialize login state
frame_skip = 1 # Frame skip for performance

# Load the Haar Cascade for face detection globally
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to append recognition log to the GUI
def add_to_log(name, action):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{action}: {name} at {current_time}\n"
    log_text.config(state="normal")
    log_text.insert(tk.END, log_entry)
    log_text.config(state="disabled")

# Function to load known faces from the database
def load_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings.clear()
    known_face_names.clear()
    
    if not os.path.exists(database_path):
        os.makedirs(database_path)
    
    for filename in os.listdir(database_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(database_path, filename)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_face_encodings.append(encoding[0])
                known_face_names.append(os.path.splitext(filename)[0])

# Upload an image for face encoding
def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        upload_preview_label={}
        img = Image.open(file_path)
        img.thumbnail((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        upload_preview_label.config(image=img_tk)
        upload_preview_label.image = img_tk

        # Save the uploaded image to the database and reload known faces
        filename = os.path.basename(file_path)
        img.save(os.path.join(database_path, filename))
        load_known_faces()
        messagebox.showinfo("Upload", "Image uploaded and added to the recognition database.")

def process_recognition(cap, video_label, location_label):
    frame_count = 0
    recognized_this_frame = set()  # Set to track recognized names for this frame
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:  # Skip frames for performance
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                match_index = matches.index(True)
                name = known_face_names[match_index]

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Log entry if recognized for the first time in this frame
            if name not in recognized_this_frame and name != "Unknown":
                recognized_this_frame.add(name)
                add_to_log(name, "Recognized Entry")
                
        video_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        video_image = video_image.resize((400, 300))
        video_image_tk = ImageTk.PhotoImage(video_image)

        video_label.config(image=video_image_tk)
        video_label.image = video_image_tk

    cap.release()

# Create a frame for video streams
video_frame = tk.Frame(root)
video_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Create labels for entry and exit video streams
entry_video_label = tk.Label(video_frame)
entry_video_label.pack(side=tk.TOP)

exit_video_label = tk.Label(video_frame)
exit_video_label.pack(side=tk.BOTTOM)

# Create a frame for buttons and log
control_frame = tk.Frame(root, bg="#f0f0f0")
control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Add buttons to the control frame
upload_button = tk.Button(control_frame, text="Upload Image", command=upload_image, state=tk.DISABLED)
upload_button.pack(pady=10)

recognize_button = tk.Button(control_frame, text="Start Recognition", command=lambda: start_recognition(entry_video_label, exit_video_label), state=tk.DISABLED)
recognize_button.pack(pady=10)
# Define scopes for Google Drive API access
def generate_excel():
    """Generate an Excel file from log data and save it locally."""
    log_entries = log_text.get("1.0", tk.END).strip().split("\n")
    data = [entry.split(": ") for entry in log_entries if entry]
    
    data.sort(key=lambda x: datetime.strptime(x[1].split(" at ")[1], "%Y-%m-%d %H:%M:%S"))

    df = pd.DataFrame(data, columns=["Action", "Details"])
    file_path = os.path.join(os.getcwd(), "recognition_log.xlsx")
    df.to_excel(file_path, index=False)
    
    messagebox.showinfo("File Generated", f"Excel file generated successfully at {file_path}")
    return file_path

def send_whatsapp(whatsapp_number, message):
    """Send a WhatsApp message."""
    try:
        now = datetime.now() + timedelta(minutes=2)  # Set message for 2 minutes into the future
        pwk.sendwhatmsg(whatsapp_number, message, now.hour, now.minute)
        messagebox.showinfo("WhatsApp", "Message sent successfully on WhatsApp!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send the message on WhatsApp: {str(e)}")


def on_data_icon_click(event):
    """Handle data icon click event, prompt for WhatsApp number, and send report."""
    whatsapp_number = simpledialog.askstring("WhatsApp Number", "Enter the WhatsApp number (+countrycodephonenumber):")
    
    if whatsapp_number:
        file_path = generate_excel()
        if file_path:
            message = f"Here is the recognition log report. The file is saved locally at: {file_path}"
            send_whatsapp(whatsapp_number, message)
    else:
        messagebox.showerror("Error", "WhatsApp number is required to send the file.")

# Bind the data icon click event to the function
data_icon.bind("<Button-1>", on_data_icon_click)

# Log display
log_label = tk.Label(control_frame, text="Recognition Log", bg="#f0f0f0")
log_label.pack(pady=10)

log_text = tk.Text(control_frame, height=15, state="disabled", bg="#fff")
log_text.pack(fill=tk.BOTH, expand=True)

# Function to start recognition in a separate thread
def start_recognition(entry_label, exit_label):
    # Attempt to open the entry camera
    entry_cap = cv2.VideoCapture(0)
    if not entry_cap.isOpened():
        messagebox.showerror("Error", "Entry camera not available, trying exit camera instead.")
        # Attempt to open the exit camera if entry camera fails
        entry_cap = cv2.VideoCapture(1)  # Use the exit camera index
        if not entry_cap.isOpened():
            messagebox.showerror("Error", "Could not open exit camera either.")
            return  # Exit if no cameras are available

    # Attempt to open the exit camera
    exit_cap = cv2.VideoCapture(2)  # Try a different index for the exit camera
    if not exit_cap.isOpened():
        messagebox.showerror("Error", "Exit camera not available, using entry camera only.")

    # Load known faces before starting the recognition process
    load_known_faces()

    # Start recognition for entry camera
    threading.Thread(target=process_recognition, args=(entry_cap, entry_label, "Entry")).start()
    
    # Start recognition for exit camera only if it's opened successfully
    if exit_cap.isOpened():
        threading.Thread(target=process_recognition, args=(exit_cap, exit_label, "Exit")).start()
# Start the Tkinter event loop
root.mainloop()
