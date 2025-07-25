from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg, open_video
import cv2
import os

# this script splits the videos into frames at the midpoint of each scene
# all clips are saved to "not_pitch" folder
# pitch clips are manually added to "pitch" folder

# next step: train model to classify pitch and not pitch



def split_video(video_path, scene_timestamps, num, pitch_type):

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
            output_path = os.path.join("./training_data/not_pitch", f"scene_snapshot_{pitch_type}_{num}_{i+1}.jpg")
            cv2.imwrite(output_path, frame)
            print(f"Saved frame from timestamp {scene['midpoint']:.2f}ms to {output_path}")

    # Release video capture
    cap.release()


# pitch type is the folder name
def each_video(pitch_type, num_videos):
    # test for first 10 videos.
    for num in range(1, num_videos + 1):
        video_path = f"../games/raw/{pitch_type}/{pitch_type}_{num}.mp4"

        scene_list = detect(video_path, AdaptiveDetector())

        scene_timestamps = []
        for scene in scene_list:
            scene_timestamps.append({
                'start': scene[0].get_seconds(),
                # milliseconds
                'midpoint': ((scene[0].get_seconds() + scene[1].get_seconds()) / 2) * 1000,
                'end': scene[1].get_seconds()
            })

        video = open_video(video_path)
        duration = video.duration.get_seconds()

        if not scene_timestamps:
            scene_timestamps.append({
                'start': 0.0,
                'midpoint': (duration / 2) * 1000,
                'end': duration
            })

        split_video(video_path, scene_timestamps, num, pitch_type)



if __name__ == "__main__":
    each_video("fastball", 165)
    each_video("offspeed", 59)
    each_video("breaking", 130)
