from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
import cv2

# detects scenes
scene_list = detect('../games/raw/fastball/fastball_.mp4', AdaptiveDetector())

# store timestamps (
# we use the midpoint to check which scene matches the pitch template the best
scene_timestamps = []
for scene in scene_list:
    scene_timestamps.append({
        'start': scene[0].get_seconds(),
        # milliseconds
        'midpoint': ((scene[0].get_seconds() + scene[1].get_seconds()) / 2) * 1000,
        'end': scene[1].get_seconds()
    })

#--------------------------------
# Initialize the arguments to calculate the histograms (bins, ranges and channels H and S
h_bins = 30
s_bins = 32
histSize = [h_bins, s_bins]
# hue varies from 0 to 179, saturation from 0 to 255
h_ranges = [0, 180]
s_ranges = [0, 256]
ranges = h_ranges + s_ranges # concat lists
# Use the 0-th and 1-st channels
channels = [0, 1]
#--------------------------------

template = cv2.imread('../test_files/pitch_template.png')
# Convert to HSV format
hsv_template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
# calculate the histogram for the template
hist_template = cv2.calcHist([hsv_template], channels, None, histSize, ranges, accumulate=False)
cv2.normalize(hist_template, hist_template, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)


cap = cv2.VideoCapture('../test_files/fastball_131.mp4')

scores = []
scene_num = 0
for scene in scene_timestamps:
    scene_num += 1
    cap.set(cv2.CAP_PROP_POS_MSEC, scene['midpoint'])

    # Read the frame at that position
    ret, frame = cap.read()

    if ret:
        print(f"Extracted frame at {scene['midpoint']:.2f}s")
        # Convert to HSV format
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Calculate the histogram for base frame
        hist_base = cv2.calcHist([hsv_frame], channels, None, histSize, ranges, accumulate=False)
        cv2.normalize(hist_base, hist_base, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        for compare_method in range(4):
            
            result = cv2.compareHist(hist_base, hist_template, compare_method)

            scores.append({'scene_num': scene_num, 'method': compare_method, 'result': result})


cap.release()


import pandas as pd
df = pd.DataFrame(scores)

# Method 0: Correlation (higher = more similar)
# Method 1: Chi-Square (lower = more similar)
# Method 2: Intersection (higher = more similar)
# Method 3: Bhattacharyya distance (lower = more similar)

# Calculate rankings for each method
rankings = {}
for method in range(4):
    method_results = df[df['method'] == method].copy()
    # For methods 0 and 2, higher is better (descending)
    # For methods 1 and 3, lower is better (ascending)
    ascending = method in [1, 3]
    method_results = method_results.sort_values('result', ascending=ascending)
    method_results['rank'] = range(1, len(method_results) + 1)
    rankings[method] = method_results.set_index('scene_num')['rank']

# Calculate final rankings by averaging ranks across all methods
final_rankings = {}
for scene_num in df['scene_num'].unique():
    avg_rank = sum(rankings[method][scene_num] for method in range(4)) / 4
    final_rankings[scene_num] = avg_rank

# Sort by average rank (lower is better)
sorted_final = sorted(final_rankings.items(), key=lambda x: x[1])

print("Final Rankings (based on average rank across all methods):")
print("Scene  Avg Rank")
print("-" * 15)
for scene_num, avg_rank in sorted_final:
    print(f"{scene_num:5d}  {avg_rank:8.2f}")

# Get the best matching scene
best_scene = sorted_final[0][0]
print(f"\nBest matching scene: {best_scene}")




