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

# Function to generate video from image URLs
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

    # Define output file path
    output_file = f"output_video_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
    output_path = os.path.join("output_videos", output_file)

    # Write the video file
    video_clip.write_videofile(output_path, fps=24)

    return output_path

@app.route('/generate_video', methods=['POST'])
def generate_video_api():
    if 'image_urls' not in request.json:
        return jsonify({"error": "image_urls field missing in request body"}), 400

    image_urls = request.json['image_urls']

    # Generate video from image URLs
    video_path = generate_video(image_urls)

    return jsonify({"video_url": video_path}), 200

