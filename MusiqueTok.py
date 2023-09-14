import streamlit as st
import yt_dlp as youtube_dl
from io import BytesIO
import os
from moviepy.editor import *
import random
import time


def download(url, video_paths):
    # Extract information about the video from the given URL
    video_info = youtube_dl.YoutubeDL().extract_info(url=url, download=False)

    # Format the filename to include the video's title
    filename = f"{video_info['title']}"

    # Options for downloading
    options = {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': filename,
    }

    # Download the video with the given options
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])
    
    time.sleep(3)
    # Read the file into a BytesIO buffer
    with open(f"{filename}.mp3", 'rb') as f:
        mp3_bytes = BytesIO(f.read())

    # Optionally, remove the file after reading it into memory
    os.remove(f"{filename}.mp3")

    # Convert MP3 BytesIO to AudioFileClip
    mp3_filename = "/tmp/temp_song.mp3"
    with open(mp3_filename, "wb") as f:
        f.write(mp3_bytes.getvalue())
    audio = AudioFileClip(mp3_filename)

     # Create a list of VideoFileClip objects for all videos
    videos = [VideoFileClip(f"{path}") for path in video_paths]
    
    # Shuffle the list
    random.shuffle(videos)
    
    # Concatenate all the video clips
    concatenated_video = concatenate_videoclips(videos)

    # Resize audio or concatenated_video to match each other's duration
    if audio.duration > concatenated_video.duration:
        audio = audio.subclip(0, concatenated_video.duration)
    else:
        concatenated_video = concatenated_video.subclip(0, audio.duration)

    # Set the audio of the concatenated_video to the given MP3
    final_clip = concatenated_video.set_audio(audio)

    # Export to BytesIO
    result_video = BytesIO()
    # Temporary output file
    temp_output_file = "/tmp/temp_output_video.mp4"

    # Write the final clip to the temporary output file
    final_clip.write_videofile(temp_output_file, codec="libx264", audio_codec="aac")

    # Read the temporary output file into the BytesIO object
    with open(temp_output_file, "rb") as f:
        result_video.write(f.read())

    # Optionally, remove the temporary output file
    os.remove(temp_output_file)

    # Close the clips
    audio.close()
    for video in videos:
        video.close()
    concatenated_video.close()
    final_clip.close()

    # Reset BytesIO pointer to the start
    result_video.seek(0)

    return result_video



st.title('Musique Tiktok Maker')

# Input URL
url = st.text_input('Enter the YouTube URL:')

# File uploader for multiple videos
uploaded_files = st.file_uploader("Choose videos", type=['mp4', 'mov', 'avi'], accept_multiple_files=True)

# Create the 'vids' directory if it doesn't exist
if not os.path.exists('vids'):
    os.mkdir('vids')

video_paths = [os.path.join("vids", filename) for filename in os.listdir("vids") if os.path.isfile(os.path.join("vids", filename))]
print(video_paths)

for file in uploaded_files:
    # Save the Streamlit's uploaded file objects to the 'vids' directory.
    tmp_path = f"vids/{file.name}"
    video_paths.append(tmp_path)
    with open(tmp_path, 'wb') as f:
        f.write(file.getvalue())

if len(video_paths) > 36:
    video_paths = random.sample(video_paths, 36)
print(video_paths)
if st.button('Download and Process'):
    try:
        result = download(url, video_paths)
        
        # Offer the processed video for download
        st.video(result.getvalue())
        st.download_button(label="Download Video", data=result.getvalue(), file_name='output.mp4', mime='video/mp4')
        
    except Exception as e:
        st.error(f"An error occurred: {e}")

