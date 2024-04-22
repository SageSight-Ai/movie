from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips
import requests
from PIL import Image
import numpy as np
from io import BytesIO
import os

app = Flask(__name__)

# Function to add fade-in and fade-out transition to each clip
def add_transitions(clip_list):
    transition_duration = 1  # Duration of fade-in and fade-out transitions in seconds
    transition_clips = [clip.fadein(transition_duration).fadeout(transition_duration) for clip in clip_list]
    return transition_clips

# Function to generate video from image URLs and return video output URL
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

    # Write the video file
    output_file = "output_video.mp4"
    video_clip.write_videofile(output_file, fps=24)

    return output_file

@app.route('/generate_video', methods=['POST'])
def handle_generate_video():
    data = request.json
    image_urls = data.get('image_urls', [])
    if not image_urls:
        return jsonify({"error": "No image URLs provided"}), 400
    
    # Generate video
    output_file = generate_video(image_urls)
    
    # Construct absolute URL for the video output file
    output_url = request.host_url + output_file

    return jsonify({"output_url": output_url}), 200

