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

# Function to generate the video
def generate_video(image_urls):
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
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_folder = "output_videos"
    output_filename = f"output_video_{timestamp}.mp4"
    output_path = os.path.join(output_folder, output_filename)

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Write the video file
    video_clip.write_videofile(output_path, fps=24)

    return output_path

@app.route('/generate_video', methods=['POST'])
def generate_video_api():
    # Read image URLs from request
    image_urls = request.json.get('image_urls', [])

    # Generate video
    video_path = generate_video(image_urls)

    # Get the absolute URL for the video file
    video_url = request.url_root + video_path

    return jsonify({'video_url': video_url})
