from fastapi import FastAPI, HTTPException, Request
from moviepy.editor import ImageClip, concatenate_videoclips
import requests
from PIL import Image
import numpy as np
from io import BytesIO
from datetime import datetime
import tempfile
import dropbox

app = FastAPI()

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

    # Write the video file to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        video_clip.write_videofile(temp_file.name, fps=24, codec="libx264", audio_codec="aac")

    return temp_file.name

# Function to upload video to Dropbox
def upload_to_dropbox(file_path):
    ACCESS_TOKEN = 'your_dropbox_access_token_here'  # Your Dropbox access token
    dbx = dropbox.Dropbox(ACCESS_TOKEN)

    with open(file_path, 'rb') as f:
        dbx.files_upload(f.read(), f"/videos/{file_path}", mode=dropbox.files.WriteMode("overwrite"))

    # Get shared link for the uploaded file
    shared_link = dbx.sharing_create_shared_link(f"/videos/{file_path}").url
    return shared_link

@app.get('/')
async def root():
    return 'Welcome to the video generation API!'

@app.post('/generate_video')
async def generate_video_api(request: Request):
    try:
        data = await request.json()
        # Read image URLs from request
        image_urls = data.get('image_urls', [])

        # Generate video
        video_path = generate_video(image_urls)

        # Upload video to Dropbox
        dropbox_url = upload_to_dropbox(video_path)

        # Return the Dropbox URL as a response
        return {"dropbox_url": dropbox_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
