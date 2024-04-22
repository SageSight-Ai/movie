from flask import Flask, request, jsonify
from moviepy.editor import ImageSequenceClip
from io import BytesIO
from datetime import datetime
import dropbox
import os

app = Flask(__name__)

DROPBOX_ACCESS_TOKEN = "sl.Bz0FBRcHokR7WYB1aW9HOPMHtQH7ArLxpRGGZz3qNAn0CS--eUBMlCXOWzP-0RDUWdnTcRohr8Xe2tWTyTltADlskJa1wlT_9CbKh3ClHO6yA3rVfJqpcRozm3Fn14qjcIchzS59zJVC"

def generate_video(image_urls):
    image_clips = []
    for url in image_urls:
        # Download image and convert it to bytes
        # image_bytes = download_image(url)
        
        # For demonstration purposes, let's create a BytesIO object with random data
        image_bytes = BytesIO(b'\x00\x01\x02\x03')
        
        # Convert image bytes to ImageClip
        image_clip = ImageClip(image_bytes)
        image_clips.append(image_clip)
    
    # Add 3-second delay between each image
    image_clips_with_delay = [clip.set_duration(3) for clip in image_clips]
    
    # Add fade in and fade out transitions
    transition_duration = 1  # 1 second transition
    transition_clips = add_transitions(image_clips_with_delay, transition_duration)
    
    # Concatenate all clips into one video
    video_clip = concatenate_videoclips(transition_clips)
    
    # Generate unique filename for the video based on current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"output_video_{timestamp}.mp4"
    
    # Write the video to a temporary file on disk
    video_clip.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    
    # Upload video to Dropbox
    with open(output_filename, 'rb') as f:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        response = dbx.files_upload(f.read(), f"/{output_filename}")
    
    # Remove temporary file
    os.remove(output_filename)
    
    # Get shared link for the uploaded video
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(f"/{output_filename}")
    video_url = shared_link_metadata.url.replace("dl=0", "raw=1")
    
    return video_url

@app.route('/generate_video', methods=['POST'])
def generate_video_api():
    request_data = request.get_json()
    image_urls = request_data.get('image_urls', [])
    video_url = generate_video(image_urls)
    return jsonify({'video_url': video_url})

