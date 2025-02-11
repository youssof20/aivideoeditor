# Video Audio Segmentation and Transcription with OpenAI Whisper

## Overview

This Python project is designed to process video files by extracting audio segments, transcribing them using OpenAI's Whisper model, cleaning the transcriptions with GPT-3.5, and then editing the video accordingly. The goal is to remove unnecessary or redundant parts of the video, creating a more focused and concise output. The final video is saved with the edits, and the cleaned transcription is also saved as a JSON file for reference.

## Features

- **Audio Extraction**: Extracts audio from video files.
- **Audio Segmentation**: Splits audio into segments based on silence.
- **Transcription**: Uses OpenAI Whisper to transcribe audio segments.
- **Transcription Cleaning**: Sends transcriptions to GPT-3.5 for cleanup and redundancy removal.
- **Video Editing**: Edits the video to include only the relevant parts based on the cleaned transcription.
- **Output**: Saves the processed video and transcription in specified directories.

## Requirements

Before running the project, make sure you have the following dependencies:

1. **Python 3.x**: Make sure you have Python 3.x installed.
2. **Libraries**: The following Python libraries are required:
   - `moviepy`: For video editing.
   - `pydub`: For audio processing.
   - `openai`: For accessing OpenAI API.
   - `ffmpeg`: For extracting audio from video files.
   
   You can install these dependencies using `pip`:
   ```bash
   pip install moviepy pydub openai
   ```

3. **FFmpeg**: This project relies on FFmpeg to extract audio from video files. Install FFmpeg on your system:
   - [FFmpeg Download](https://ffmpeg.org/download.html)
   - Ensure `ffmpeg` is available in your system’s PATH.

4. **OpenAI API Key**: You need to have an OpenAI API key. Set it as an environment variable (`OPENAI_API_KEY`).

## Setup

1. **Directory Structure**:
   The project expects the following directory structure:
   ```
   ├── raw/               # Folder where raw video files are located
   ├── output/            # Folder where processed videos are saved
   ├── transcripts/       # Folder where transcriptions are saved
   ├── logs/              # Folder for logs
   ```

   The script will automatically create the required directories if they do not exist.

2. **Environment Variables**:
   Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

## How It Works

### 1. **Audio Extraction**
   The script uses `ffmpeg` to extract the audio from each video file in the `raw/` folder. It saves the audio as a `.wav` file and proceeds to segment it based on silence. The silence threshold, minimum silence duration, and padding around silence segments are configurable.

### 2. **Audio Segmentation**
   After extracting the audio, the script uses the `pydub` library to split the audio into segments by detecting silences. The silence length and threshold are configurable, and these segments are used to determine the relevant parts of the video.

### 3. **Transcription**
   Each audio segment is transcribed using OpenAI's Whisper API. The transcription results are stored temporarily.

### 4. **Transcription Cleanup**
   The raw transcriptions are sent to GPT-3.5 for cleaning. GPT-3.5 removes redundant transcriptions and improves the clarity of the text, which is essential for generating accurate results.

### 5. **Video Editing**
   Based on the cleaned transcription, the script selects the relevant video segments and concatenates them into a new video. This removes sections of the video that are either silent or irrelevant based on the audio content.

### 6. **Saving the Output**
   - **Video**: The final edited video is saved in the `output/` folder.
   - **Transcription**: The cleaned transcription is saved as a `.json` file in the `transcripts/` folder.

## Configuration

- **Padding (ms)**: Controls the padding around audio segments when splitting based on silence. Default: 500ms.
- **Minimum Silence Length (ms)**: Controls the minimum length of silence to detect. Default: 700ms.
- **Silence Threshold (dB)**: Controls the volume threshold for silence detection. Default: -40dB.

## Running the Script

To run the script, simply execute it with Python:
```bash
python process_video.py
```

The script will process all `.mp4` files in the `raw/` directory, extract and transcribe the audio, clean the transcription, and create a new video with relevant content only.

## Example

Given a raw video like `raw/sample_video.mp4`, the script will:
- Extract the audio.
- Split it into segments based on silence.
- Transcribe and clean the transcription.
- Edit the video based on the cleaned transcription.
- Save the processed video as `output/edited_sample_video.mp4`.
- Save the transcription as `transcripts/sample_video.json`.

## Logging

Logs are stored in the `logs/` directory. The logging level can be adjusted to debug or change the verbosity of the messages.

## Troubleshooting

- **No Video Files Found**: If the script doesn’t find any video files in the `raw/` directory, make sure you have `.mp4` files in the folder.
- **API Key Error**: Ensure that your OpenAI API key is set correctly in your environment variables.
- **Missing FFmpeg**: If the script fails to extract audio, make sure FFmpeg is installed and accessible via the command line.

## License

This project is open-source under the MIT License. Feel free to modify and contribute.
