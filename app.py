from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips
import requests
from PIL import Image
import numpy as np
from io import BytesIO
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
        
        # Convert image array to RGB mode if necessary
        if image_array.ndim == 2:
            image_array = np.repeat(image_array[:, :, np.newaxis], 3, axis=2)
        elif image_array.shape[2] == 4:
            image_array = image_array[:, :, :3]
        
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

    # Return the BytesIO object containing the video content
    return video_buffer.getvalue()

@app.route('/generate_video', methods=['POST'])
def generate_video_api():
    try:
        # Read image URLs from request
        image_urls = request.json.get('image_urls', [])

        # Generate video
        video_content = generate_video(image_urls)

        # Return the video content as a response
        return video_content, 200, {'Content-Type': 'video/mp4'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500


