import os
import json
import logging
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips
import openai
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# OpenAI API key setup
openai.api_key = os.getenv("OPENAI_API_KEY")  # Replace with your API key or ensure it's set as an environment variable

# Directory configurations
RAW_VIDEO_DIR = "./raw"
OUTPUT_DIR = "./output"
TRANSCRIPTS_DIR = "./transcripts"
LOG_DIR = "./logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Padding and silence thresholds
PADDING_MS = 500
MIN_SILENCE_LEN_MS = 700
SILENCE_THRESH_DB = -40


def extract_audio_segments(video_path):
    """Extract audio segments from a video by detecting silences."""
    try:
        audio_file_path = video_path.replace(".mp4", ".wav")
        logging.info(f"Extracting audio from {video_path}")

        # Extract audio using ffmpeg
        subprocess.run([
            "ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_file_path, "-y"
        ], check=True)

        audio = AudioSegment.from_file(audio_file_path)
        segments = split_on_silence(
            audio,
            min_silence_len=MIN_SILENCE_LEN_MS,
            silence_thresh=SILENCE_THRESH_DB,
            keep_silence=PADDING_MS
        )
        logging.info(f"Found {len(segments)} audio segments.")
        return segments, audio_file_path

    except subprocess.CalledProcessError as e:
        logging.error(f"Error extracting audio: {e}")
        return [], None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return [], None


def transcribe_audio_segment(audio_segment):
    """Transcribe a single audio segment using OpenAI Whisper."""
    try:
        # Save temp audio for transcription
        temp_audio_path = "temp_segment.wav"
        audio_segment.export(temp_audio_path, format="wav")

        # Transcribe using OpenAI Whisper API
        with open(temp_audio_path, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
        return response['text']
    except Exception as e:
        logging.error(f"Error transcribing segment: {e}")
        return ""


def process_transcription(transcriptions):
    """Send transcription to LLM to clean up and remove duplicates."""
    try:
        prompt = json.dumps({"transcriptions": transcriptions})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Remove redundant transcriptions and improve clarity."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Error processing transcription: {e}")
        return ""


def process_video(video_path):
    """Main video processing workflow."""
    try:
        logging.info(f"Processing video: {video_path}")

        # Step 1: Extract audio segments
        segments, audio_file_path = extract_audio_segments(video_path)
        if not segments:
            logging.warning("No valid audio segments found.")
            return

        # Step 2: Transcribe each audio segment
        transcriptions = [transcribe_audio_segment(segment) for segment in segments]
        logging.info(f"Generated raw transcriptions: {transcriptions}")

        # Step 3: Process transcription
        clean_transcription = process_transcription(transcriptions)
        logging.info(f"Cleaned transcription: {clean_transcription}")

        # Step 4: Edit video based on clean transcription
        original_video = VideoFileClip(video_path)
        clip_segments = []
        for segment in segments:
            start_ms = segment.start_time / 1000.0
            end_ms = segment.end_time / 1000.0
            if start_ms < original_video.duration:
                clip_segments.append(original_video.subclip(max(0, start_ms), min(end_ms, original_video.duration)))

        final_clip = concatenate_videoclips(clip_segments)
        output_path = os.path.join(OUTPUT_DIR, f"edited_{os.path.basename(video_path)}")
        final_clip.write_videofile(output_path, codec="libx264")

        # Save transcription JSON
        json_path = os.path.join(TRANSCRIPTS_DIR, f"{os.path.basename(video_path)}.json")
        with open(json_path, "w") as f:
            json.dump({"transcription": clean_transcription}, f, indent=4)

        logging.info(f"Successfully processed and saved output to {output_path}")

    except Exception as e:
        logging.error(f"Error processing video {video_path}: {e}")


if __name__ == "__main__":
    video_files = [f for f in os.listdir(RAW_VIDEO_DIR) if f.endswith(".mp4")]

    if not video_files:
        logging.info("No video files found in raw directory.")
    else:
        for video_file in video_files:
            process_video(os.path.join(RAW_VIDEO_DIR, video_file))

    logging.info("Video processing completed.")
