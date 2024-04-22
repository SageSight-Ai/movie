from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips
import requests
from PIL import Image
import numpy as np
from io import BytesIO
import os
from datetime import datetime
import dropbox

app = Flask(__name__)

# Dropbox access token
DROPBOX_ACCESS_TOKEN = 'sl.Bz0FBRcHokR7WYB1aW9HOPMHtQH7ArLxpRGGZz3qNAn0CS--eUBMlCXOWzP-0RDUWdnTcRohr8Xe2tWTyTltADlskJa1wlT_9CbKh3ClHO6yA3rVfJqpcRozm3Fn14qjcIchzS59zJVC'

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
    output_filename = f"output_video_{timestamp}.mp4"

    # Write the video file to a BytesIO object
    video_buffer = BytesIO()
    video_clip.write_videofile(video_buffer, fps=24, codec="libx264", audio_codec="aac")

    # Upload video to Dropbox
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    response = dbx.files_upload(video_buffer.getvalue(), f"/{output_filename}")

    # Get shared link for the uploaded video
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(f"/{output_filename}")
    video_url = shared_link_metadata.url.replace("dl=0", "raw=1")

    return video_url

@app.route('/generate_video', methods=['POST'])
def generate_video_api():
    # Read image URLs from request
    image_urls = request.json.get('image_urls', [])

    # Generate video and get Dropbox URL
    video_url = generate_video(image_urls)

    return jsonify({'video_url': video_url})
