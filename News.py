from moviepy.editor import AudioFileClip, concatenate_videoclips, ImageClip, ColorClip, CompositeVideoClip, clips_array, VideoFileClip, TextClip
import moviepy.video.fx.all as vfx
from pydub import AudioSegment
import cv2
import numpy as np
from textwrap import wrap
import glob
import shutil
import os
import sys

source = './Wav2Lip/output/result.mp4'
destination = './result_voice_sync.mp4'
shutil.move(source, destination)

def delete_files_in_current_directory(files):
    current_directory = os.getcwd()
    for file in files:
        file_path = os.path.join(current_directory, file)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Đã xoá file {file_path}")
        else:
            print(f"File {file_path} không tồn tại")

def speed_up_video(input_path, output_path, speed):
    clip = VideoFileClip(input_path)
    clip = clip.set_fps(clip.fps * speed)
    clip = clip.fx(vfx.speedx, speed)

    audio = AudioFileClip(input_path)
    audio = audio.fx(vfx.speedx, speed)

    final = clip.set_audio(audio)
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")

def merge_audio_with_video(input_path, output_path):
    # Load the video clip
    video_clip = VideoFileClip(input_path)

    # Load the audio segments
    audio1 = AudioSegment.from_file(input_path)
    audio2 = AudioSegment.from_file('./elements/backgroundsound.wav')

    while audio2.duration_seconds < audio1.duration_seconds:
        audio2 = audio2 + audio2
    audio2 = audio2[:int(audio1.duration_seconds * 1000)]  # Convert duration to milliseconds

    merged_audio = audio1.overlay(audio2)
    merged_audio.export("merged_audio.wav", format="wav")

    # Load the merged audio clip
    merged_audio_clip = AudioFileClip("merged_audio.wav")

    # Set the audio of the video clip to the merged audio clip
    final_clip = video_clip.set_audio(merged_audio_clip)

    # Export the final video
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

def change_background(video_path, image_path, output_path):
    # Load the image
    background_image = cv2.imread(image_path)

    # Open the video
    cap = cv2.VideoCapture(video_path)

    # Get video details
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get fps of the original video
    size = (frame_width, frame_height)

    # Resize the image to match the video
    background_image = cv2.resize(background_image, size)

    # Create the writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
    out = cv2.VideoWriter(output_path, fourcc, fps, size)  # Use original fps

    # Read until end of video
    while cap.isOpened():
        # Read the frame
        ret, frame = cap.read()

        if not ret:
            break

        # Convert the image from BGR to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define range of green color in HSV
        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])

        # Threshold the HSV image to get only green colors
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Bitwise-AND mask and original image
        mask_inv = cv2.bitwise_not(mask)

        # Replace the green background with the image
        bg = cv2.bitwise_and(background_image, background_image, mask=mask)
        fg = cv2.bitwise_and(frame, frame, mask=mask_inv)

        # Combine the foreground and background
        combined = cv2.add(bg, fg)

        # Write the frame
        out.write(combined)

    # After the loop release the cap and out objects
    cap.release()
    out.release()

    # Destroy all the windows
    cv2.destroyAllWindows()

def create_video_with_images_and_text():
    with open('./vietTTS/assets/transcript.txt', 'r') as file:
        title_text = file.readline().strip()

    result_voice_sync = VideoFileClip("MC_final_video.mp4")
    audio = result_voice_sync.audio

    image_files = sorted(glob.glob('./vietTTS/assets/images/' + '/*.jpg'))
    num_images = len(image_files)
    image_duration = audio.duration / num_images

    image_clips = []
    for img in image_files:
        image_clip = ImageClip(img).resize(width=1080).set_duration(image_duration)
        image_clips.append(image_clip)

    final_clip = concatenate_videoclips(image_clips)
    final_clip = final_clip.set_audio(result_voice_sync.audio)

    # Đọc file video của MC
    mc_video = VideoFileClip('MC_final_video.mp4')
    mc_video = mc_video.resize(height=409.0)
    mc_video = mc_video.set_duration(audio.duration)

    # Tạo một lớp ghép nối giữa ảnh minh hoạ và video của MC
    second_bg = ImageClip("./elements/2nd-bg.png")
    second_bg = second_bg.resize(width=1080)

    # layer1
    bg_clip1 = ColorClip((1080, 1920), col=(0, 0, 0)).set_duration(audio.duration)
    bg_clip3 = ColorClip((1080, 1390), col=(255, 0, 0)).set_duration(audio.duration)
    bg_clip4 = ColorClip((600, 650), col=(0, 0, 0)).set_duration(audio.duration).set_position((115, 1200))

    # Tạo CompositeVideoClip bao gồm ColorClip (như là nền) và final_clip
    layer3 = CompositeVideoClip([bg_clip3, final_clip.set_position((0, 0))])
    layer3 = layer3.set_duration(audio.duration)

    layer1 = CompositeVideoClip([bg_clip1, layer3.set_position((0, 0))])
    layer1 = layer1.set_duration(audio.duration)

    # layer2
    layer2 = CompositeVideoClip([second_bg.set_position((0, layer1.size[1] - second_bg.size[1])),
                                 mc_video.set_position((layer1.size[0]*0.7, layer1.size[1] - mc_video.size[1]))],
                                size=(layer1.size[0], layer1.size[1]))
    layer2 = layer2.set_duration(audio.duration)

    # Create a TextClip for the title
    lines = wrap(title_text, 15)
    clips = [TextClip(line, font="Barlow-Bold", color='white', align='West', fontsize=80) for line in lines]
    title_clip = clips_array([[clip] for clip in clips])
    title_clip = title_clip.set_duration(audio.duration)
    title_pos = ("center", "center")

    # layer4
    layer4 = CompositeVideoClip([bg_clip4, title_clip.set_position(title_pos)])
    layer4 = layer4.set_duration(audio.duration)

    # Tạo video cuối cùng với ảnh minh hoạ ở trên, video của MC ở dưới và tiêu đề ở giữa
    final_video = CompositeVideoClip([layer1, layer2, layer4.set_position((115, 1200))])
    final_video = final_video.set_duration(audio.duration)  # Set the duration of the final_video clip
    final_video.write_videofile("FINAL.mp4", fps=24, codec="libx264", audio_codec="aac")

def main():
    video = VideoFileClip('result_voice_sync.mp4')
    video.audio.write_audiofile('original_audio.mp3')
    change_background('result_voice_sync.mp4', './elements/3rd-bg.png', 'newMC.mp4')
    video_without_audio = VideoFileClip('newMC.mp4')
    audio = AudioFileClip('original_audio.mp3')
    MC_video = video_without_audio.set_audio(audio)
    MC_video.write_videofile('MC_final_video.mp4', codec='libx264', audio_codec='aac')
    create_video_with_images_and_text()

    speed_up_video("FINAL.mp4", "FINALL.mp4", 1.25)
    merge_audio_with_video("FINALL.mp4", sys.argv[1])

    files = ["result_voice_sync.mp4", "newMC.mp4", "MC_final_video.mp4", "merged_audio.wav", "original_audio.mp3", "FINAL.mp4", "./vietTTS/assets/transcript.txt"]
    delete_files_in_current_directory(files)

if __name__ == "__main__":
    main()



