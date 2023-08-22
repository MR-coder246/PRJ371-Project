import threading
from datetime import datetime
import cv2
import tellopy
import numpy as np
import random
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Add PIL imports for image display
from matplotlib import pyplot as plt

# Global variables
is_recording = False
video_writer = None
irrigation_threshold = 0.4
cap = cv2.VideoCapture(0)  # Initialize the camera capture

# Create the main application window
root = tk.Tk()
root.title("AgriDrone Control")

# Create a label for status messages
status_label = ttk.Label(root, text="")
status_label.pack()

# Function to start or stop video recording and display it
def toggle_record():
    global is_recording, video_writer
    if is_recording:
        is_recording = False
        video_writer.release()
        record_button.config(text="Start Recording")
    else:
        is_recording = True
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        video_filename = f"video_{timestamp}.avi"
        video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
        record_button.config(text="Stop Recording")

        # Display the recorded video
        cap = cv2.VideoCapture(video_filename)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB format
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            video_label.config(image=photo)
            video_label.image = photo  # To prevent garbage collection

# Create a button for recording control
record_button = ttk.Button(root, text="Start Recording", command=toggle_record)
record_button.pack()

# Function to capture an image and display it
def capture_image():
    ret, frame = cap.read()
    if ret:
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        image_filename = f"image_{timestamp}.jpg"
        cv2.imwrite(image_filename, frame)
        status_label.config(text=f"Image saved as {image_filename}")

        # Display the captured image
        image = Image.open(image_filename)
        image.thumbnail((320, 240))  # Resize the image if needed
        photo = ImageTk.PhotoImage(image=image)
        image_label.config(image=photo)
        image_label.image = photo  # To prevent garbage collection

# Create a button for capturing images
capture_button = ttk.Button(root, text="Capture Image", command=capture_image)
capture_button.pack()

# Create a label for displaying images
image_label = ttk.Label(root)
image_label.pack()

# Create a label for displaying videos
video_label = ttk.Label(root)
video_label.pack()

# Function to display a temperature heat map
def display_temperature_heatmap(temperature_data):
    # Normalize temperature data to [0, 255] for display
    normalized_data = cv2.normalize(temperature_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # Apply a colormap (e.g., 'jet') for visualization
    heatmap = cv2.applyColorMap(normalized_data, cv2.COLORMAP_JET)

    # Display the heat map
    plt.imshow(heatmap)
    plt.colorbar()
    plt.title("Temperature Heat Map")
    plt.show()

# Simulated soil moisture data (replace with real data)
def get_soil_moisture():
    return random.uniform(0, 1)  # Replace with actual sensor data

# Simulated irrigation scheduling loop
def perform_irrigation_scheduling():
    while True:
        current_soil_moisture = get_soil_moisture()
        print(f"Current Soil Moisture: {current_soil_moisture}")

        if current_soil_moisture < irrigation_threshold:
            # Trigger irrigation
            print("Starting irrigation...")
            # Add code here to control your irrigation system

        # Wait for a specific interval (e.g., 1 hour) before checking again
        time.sleep(3600)

# Function to calculate NDVI (Normalized Difference Vegetation Index)
def calculate_ndvi(image):
    # Extract the red and near-infrared (NIR) channels
    red_channel = image[:, :, 2]
    nir_channel = image[:, :, 3]

    # Calculate NDVI
    ndvi = (nir_channel - red_channel) / (nir_channel + red_channel)

    return ndvi

# Function to identify pests or diseases (placeholder for more advanced methods)
def identify_pests_or_diseases(image):
    # Add your pest or disease detection logic here
    # This can involve image processing techniques, machine learning, or deep learning models

    # For demonstration, let's assume no pests or diseases
    return np.zeros_like(image[:, :, 0])

# Function to process frames from the Tello camera
def process_frame(frame):
    # Calculate NDVI
    ndvi_result = calculate_ndvi(frame)

    # Identify pests or diseases
    pests_or_diseases_result = identify_pests_or_diseases(frame)

    # Display the video frame, NDVI, and pests/diseases detection (adjust windows as needed)
    cv2.imshow("Original Image", frame)
    cv2.imshow("NDVI", (ndvi_result * 255).astype(np.uint8))  # Scale NDVI to 8-bit for display
    cv2.imshow("Pests or Diseases", (pests_or_diseases_result * 255).astype(np.uint8))  # Convert to 8-bit for display

    cv2.waitKey(1)  # Adjust the waitKey value as needed to control frame display rate

# Create a Tello object
drone = tellopy.Tello()

try:
    # Connect to the Tello drone
    drone.connect()

    # Start receiving video stream
    drone.start_video()

    # Start the irrigation scheduling thread
    irrigation_thread = threading.Thread(target=perform_irrigation_scheduling)
    irrigation_thread.daemon = True
    irrigation_thread.start()

    # Enter the main loop
    while True:
        # Capture video frame from the Tello (replace this with your image processing logic)
        frame = drone.get_frame_read().frame

        # Process the frame
        process_frame(frame)

except Exception as e:
    print(f"Error: {str(e)}")
finally:
    drone.quit()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    root.mainloop()
