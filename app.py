from flask import Flask, request, jsonify
from moviepy.editor import ImageSequenceClip
from io import BytesIO
from datetime import datetime
import dropbox
import os

app = Flask(__name__)

DROPBOX_ACCESS_TOKEN = "sl.Bz0FBRcHokR7WYB1aW9HOPMHtQH7ArLxpRGGZz3qNAn0CS--eUBMlCXOWzP-0RDUWdnTcRohr8Xe2tWTyTltADlskJa1wlT_9CbKh3ClHO6yA3rVfJqpcRozm3Fn14qjcIchzS59zJVC"

@app.route("/generate_video", methods=["POST"])
def generate_video_api():
    image_urls = request.json.get("image_urls")
    video_url = generate_video(image_urls)
    return jsonify({"video_url": video_url})

def generate_video(image_urls):
    image_clips = []
    for image_url in image_urls:
        image_bytes = download_image(image_url)
        image_clip = create_image_clip(image_bytes)
        image_clips.append(image_clip)
    
    output_path = f"output_videos/output_video_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
    video_clip = ImageSequenceClip(image_clips, fps=24)
    video_buffer = BytesIO()
    video_clip.write_videofile(video_buffer, fps=24, codec="libx264", audio_codec="aac")
    
    upload_to_dropbox(video_buffer, output_path)
    
    return f"https://www.dropbox.com/s/{output_path}"

def download_image(image_url):
    # Implement image downloading logic here
    pass

def create_image_clip(image_bytes):
    image_clip = ImageClip(image_bytes)
    return image_clip

def upload_to_dropbox(file_buffer, output_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    file_buffer.seek(0)
    dbx.files_upload(file_buffer.read(), output_path)

