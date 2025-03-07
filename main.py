# -*- coding: utf-8 -*-

# Commented out IPython magic to ensure Python compatibility.
# %pip install git+https://github.com/openai/whisper.git speechrecognition transformers nltk moviepy==1.0.3 tabulate ollama

# !curl -fsSL https://ollama.com/install.sh | sh

# from subprocess import Popen
# process = Popen("ollama serve", shell=True)
# !ollama pull mistral

import moviepy.editor as mp
import whisper
import ollama
import os
import json
from datetime import datetime
from tabulate import tabulate

def extract_audio_from_video(video_path, audio_output_path="output.wav"):
    """Extracts audio from video and saves it as a WAV file."""
    try:
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_output_path, logger=None)
        print(f"Audio extracted to {audio_output_path}")
        return audio_output_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path):
    """Transcribes the extracted audio using Whisper AI."""
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        print("Transcription completed.")
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

def extract_tasks_with_llm(transcription):
    """Uses a local LLM (via Ollama) to extract structured tasks from a meeting transcript."""

    system_prompt = """
    You are an AI assistant extracting actionable tasks from meeting transcripts.
    - Identify tasks assigned to real people only (ignore 'it', 'we', 'someone', etc.).
    - Rewrite tasks in clear English.
    - Extract deadlines if mentioned in YYYY-MM-DD format; otherwise, use 'N/A'.
    - Output the result as a valid JSON array with "assigned_to", "task", and "deadline".
    - Output the user tasks in bullet points.
    - Ensure that the language is brief, formal and professional.
    - Output in valid Markdown format.
    """

    user_prompt = f"Meeting transcript:\n\n{transcription}\n\nExtract tasks as JSON."

    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    try:
        tasks = json.loads(response["message"]["content"])
        return tasks
    except json.JSONDecodeError:
        print("Error: LLM returned invalid JSON.")
        return []

def meeting_function(video_path):
    """Main function to process a meeting video and generate a task summary."""
    print("Step 1: Extracting audio...")
    audio_path = extract_audio_from_video(video_path)
    if not audio_path:
        return "Failed to extract audio from the video."

    print("Step 2: Transcribing audio to text...")
    transcription = transcribe_audio(audio_path)
    if not transcription:
        os.remove(audio_path)
        return "Failed to transcribe audio."

    print("Step 3: Extracting tasks with LLM...")
    tasks = extract_tasks_with_llm(transcription)  # This returns JSON data btw

    table_data = []
    for task in tasks:
        table_data.append([task['assigned_to'], task['task'], task['deadline']])

    table_output = tabulate(table_data, headers=["Assigned To", "Task", "Deadline"], tablefmt="pipe")

    if os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"Cleaned up temporary file: {audio_path}")

    final_output = f"""
    **AI-Powered Meeting Summarization and Task Assignment**

    **Full Meeting Transcript:**
    {transcription}

    **Action Items & Schedule:**
    {table_output}
    """

    with open("meeting_summary.txt", "w", encoding="utf-8") as f:
        f.write(final_output)

    print("Summary saved to 'meeting_summary.txt'")
    #return final_output

import ipywidgets as widgets
from IPython.display import display

# Create file upload widget
upload_button = widgets.FileUpload(
    accept='.mp4',  # Accept only MP4 files
    multiple=False  # Allow only single file upload
)

# Create a button to trigger processing
process_button = widgets.Button(description="Process Video")

# Function to handle file upload and processing
def on_upload_change(change):
    if upload_button.value:
        uploaded_file = list(upload_button.value.values())[0]
        file_name = uploaded_file['metadata']['name']
        with open(file_name, 'wb') as f:
            print("FIle being uploaded")
            f.write(uploaded_file['content'])
        print(f"File '{file_name}' uploaded successfully.")
        process_button.disabled = False

def on_process_button_clicked(b):
    uploaded_file = list(upload_button.value.values())[0]
    file_name = uploaded_file['metadata']['name']
    meeting_function(file_name)
    os.remove(file_name)

upload_button.observe(on_upload_change, names='value')
process_button.on_click(on_process_button_clicked)

# Initially disable the process button
process_button.disabled = True

display(upload_button)
display(process_button)

from IPython.display import Markdown, display
import re

def unindent_file(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return

    unindented_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        unindented_line = re.sub(r'^ {2,}|^\t', '', line)
        unindented_lines.append(unindented_line)

        if line.endswith("**"):
            unindented_lines.append("") #add empty line
        i += 1

    try:
        with open(output_file, 'w') as f:
            f.write('\n'.join(unindented_lines))
        print(f"Successfully unindented content and saved to '{output_file}'")
        # display(Markdown(f"## unindented_meeting_summary.txt"))
        with open(output_file, 'r') as f:
          display(Markdown(f.read()))
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")

unindent_file('meeting_summary.txt', 'unindented_meeting_summary.txt')

