import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# Load just the first 3 rows
df = pd.read_csv("pitches.csv")

# Track category counts
category_counts = {}

# Create parent clips folder
os.makedirs("clips", exist_ok=True)

# Create category subfolders
categories = ["fastball", "breaking", "offspeed"]
for category in categories:
    os.makedirs(os.path.join("clips", category), exist_ok=True)

# Loop through only 3 rows
for index, row in df.iterrows():
    url = row['video_link']
    category = row['category'].strip().lower()

    # Map category to folder name
    if "fastball" in category:
        folder = "fastball"
    elif "breaking" in category:
        folder = "breaking"
    elif "offspeed" in category:
        folder = "offspeed"
    else:
        print(f"Unknown category: {category}, skipping...")
        continue

    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the video element and its source
    video_tag = soup.find("video", {"id": "sporty"})
    if not video_tag:
        print(f"No video element found at {url}")
        continue
        
    source_tag = video_tag.find("source")
    if not source_tag or not source_tag.get("src"):
        print(f"No video source found at {url}")
        continue

    video_url = source_tag["src"]

    count = category_counts.get(folder, 0) + 1
    category_counts[folder] = count

    filename = f"{category}_{count}.mp4"
    filepath = os.path.join("clips", folder, filename)

    try:
        print(f"Downloading: {video_url} → {filepath}")
        video_data = requests.get(video_url).content
        with open(filepath, "wb") as f:
            f.write(video_data)
    except Exception as e:
        print(f"Failed to download {video_url}: {e}")
