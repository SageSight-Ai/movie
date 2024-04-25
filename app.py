import dropbox
import requests
from PIL import Image
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips
from datetime import datetime
import tempfile
from fastapi import FastAPI, HTTPException, Request

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
        # Write the image content to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_name = temp_file.name
        # Open the temporary image file with PIL
        image = Image.open(temp_file_name)
        # Resize image to reduce memory usage
        image = image.resize((640, 480))  # Adjust dimensions as needed
        image_array = np.array(image)
        # Convert image array to RGB mode if necessary
        if image_array.ndim == 2:
            image_array = np.repeat(image_array[:, :, np.newaxis], 3, axis=2)
        elif image_array.shape[2] == 4:
            image_array = image_array[:, :, :3]
        # Create ImageClip and set duration
        image_clip = ImageClip(image_array).set_duration(3)
        # Append to list of image clips
        image_clips.append(image_clip)
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
        video_path = temp_file.name
    return video_path

# Function to upload video to Dropbox
def upload_to_dropbox(video_path):
    ACCESS_TOKEN = 'sl.B0A6D0wexLC__8Ig736QSuOSFCV2SdHA7O3MBEJBMnudzfMwCPP-8ftUdrmIqMLpuzC5uOM-xZdBA9U_0bnLD01DVP9KZNLo83XryICp5WlkMro8SMuhnTpf4BzY31x5NlYn6gSzp1jhXNV54SIQj5E'  # Your Dropbox access token
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    # Upload video to Dropbox
    try:
        with open(video_path, 'rb') as f:
            response = dbx.files_upload(f.read(), f"/videos/output_video.mp4", mode=dropbox.files.WriteMode("overwrite"))
        # Get shared link for the uploaded file
        shared_link = dbx.sharing_create_shared_link(response.path_display).url
        return shared_link
    except dropbox.exceptions.ApiError as err:
        print(f"Dropbox API error: {err}")
        return None

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
    
