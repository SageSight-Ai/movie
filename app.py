from flask import Flask, request, jsonify
from moviepy.editor import ImageClip
import os
import dropbox

app = Flask(__name__)

DROPBOX_ACCESS_TOKEN = "sl.Bz0FBRcHokR7WYB1aW9HOPMHtQH7ArLxpRGGZz3qNAn0CS--eUBMlCXOWzP-0RDUWdnTcRohr8Xe2tWTyTltADlskJa1wlT_9CbKh3ClHO6yA3rVfJqpcRozm3Fn14qjcIchzS59zJVC"

@app.route("/generate_video", methods=["POST"])
def generate_video_api():
    if "image_urls" not in request.json:
        return jsonify({"error": "Image URLs not provided"}), 400
    
    image_urls = request.json["image_urls"]
    video_url = generate_video(image_urls)
    return jsonify({"video_url": video_url}), 200

def generate_video(image_urls):
    clips = []
    for url in image_urls:
        image_bytes = download_image(url)
        image_clip = create_image_clip(image_bytes)
        clips.append(image_clip)
    
    output_path = "output_videos/output_video.mp4"
    final_clip = concatenate_clips(clips)
    final_clip.write_videofile(output_path, fps=24)
    
    upload_to_dropbox(output_path)
    
    return get_dropbox_link(output_path)

def download_image(url):
    # Write code to download image from URL
    pass

def create_image_clip(image_bytes):
    return ImageClip(image_bytes)

def upload_to_dropbox(file_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), "/" + os.path.basename(file_path))

def get_dropbox_link(file_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    shared_link_metadata = dbx.sharing_create_shared_link(file_path)
    return shared_link_metadata.url
