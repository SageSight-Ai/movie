from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips
import requests
from PIL import Image
import numpy as np
from io import BytesIO
import os
from datetime import datetime

app = Flask(__name__)

# Function to add fade-in and fade-out transition to each clip
def add_transitions(clip_list):
    transition_duration = 1  # Duration of fade-in and fade-out transitions in seconds
    transition_clips = [clip.fadein(transition_duration).fadeout(transition_duration) for clip in clip_list]
    return transition_clips

@app.route('/generate_video', methods=['POST'])
def generate_video():
    # Read image URLs from request
    image_urls = request.json.get('image_urls', [])

    # Remove any whitespace characters from the URLs
    image_urls = [url.strip() for url in image_urls]

    # Download images and create list of image clips
    image_clips = []
    for url in image_urls:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        image_array = np.array(image)
        image_clip = ImageClip(image_array)  # Pass NumPy array directly to ImageClip
        image_clips.append(image_clip.set_duration(3))  # Set duration for each clip to 3 seconds

    # Add fade-in and fade-out transitions to each clip
    transition_clips = add_transitions(image_clips)

    # Concatenate clips to create the final video
    video_clip = concatenate_videoclips(transition_clips, method="compose")

    # Generate unique filename for the video based on current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    video_filename = f"output_video_{timestamp}.mp4"
    video_path = os.path.join("videos", video_filename)

    # Write the video file
    video_clip.write_videofile(video_path, fps=24)

    # Get the absolute URL for the video file
    video_url = request.url_root + video_path

    return jsonify({'video_url': video_url})
