from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
import cv2
import os
from datetime import datetime

video_path = "../test_files/fastball_131.mp4"

scene_list = detect(video_path, AdaptiveDetector())

scene_timestamps = []
for scene in scene_list:
    scene_timestamps.append({
        'start': scene[0].get_seconds(),
        # milliseconds
        'midpoint': ((scene[0].get_seconds() + scene[1].get_seconds()) / 2) * 1000,
        'end': scene[1].get_seconds()
    })


# Get current date for filename
current_date = datetime.now().strftime("%Y%m%d_%H%M%S")

# Open video
cap = cv2.VideoCapture(video_path)

# Extract frame at each midpoint
for i, scene in enumerate(scene_timestamps):
    # Set vid position to midpoint
    cap.set(cv2.CAP_PROP_POS_MSEC, scene['midpoint'])
    
    # Read the frame
    ret, frame = cap.read()
    
    if ret:
        # Save frame as image with date-based name
        output_path = os.path.join("../cnn_images/not_pitch", f"{current_date}_scene_{i+1}.jpg")
        cv2.imwrite(output_path, frame)
        print(f"Saved frame from timestamp {scene['midpoint']:.2f}ms to {output_path}")

# Release video capture
cap.release()
