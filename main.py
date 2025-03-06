import moviepy.editor as mp
import whisper
from transformers import pipeline
import os
from tabulate import tabulate

def extract_audio_from_video(video_path, audio_output_path="output.wav"):
    try:
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_output_path)
        print(f"Audio extracted to {audio_output_path}")
        return audio_output_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        print("Transcription completed.")
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

def summarize_text(text):
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
        print("Summary generated.")
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return ""

def extract_tasks(text):
    try:
        task_extractor = pipeline("summarization", model="facebook/bart-large-cnn")
        tasks_summary = task_extractor(text, max_length=200, min_length=50, do_sample=False)
        extracted_tasks = tasks_summary[0]['summary_text'].split(".")
        return [task.strip() for task in extracted_tasks if task.strip()]
    except Exception as e:
        print(f"Error extracting tasks: {e}")
        return []

def format_schedule(tasks):
    schedule = []
    for i, task in enumerate(tasks, 1):
        assigned_person = f"Person {i}"  # Placeholder for actual assignments
        deadline = f"Day {i + 1}"  # Placeholder for actual deadlines
        schedule.append([assigned_person, task, deadline])
    return schedule

def summarize_meeting(video_path):
    print("Step 1: Extracting audio...")
    audio_path = extract_audio_from_video(video_path)
    if not audio_path:
        return "Failed to extract audio from the video."
    
    print("Step 2: Transcribing audio to text...")
    transcription = transcribe_audio(audio_path)
    if not transcription:
        os.remove(audio_path)
        return "Failed to transcribe audio."
    print("Transcription:", transcription)
    
    print("Step 3: Generating summary...")
    summary = summarize_text(transcription)
    if not summary:
        os.remove(audio_path)
        return "Failed to generate summary."
    print("Summary:", summary)
    
    print("Step 4: Extracting tasks...")
    tasks = extract_tasks(transcription)
    
    print("Step 5: Generating schedule...")
    schedule = format_schedule(tasks)
    
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"Cleaned up temporary file: {audio_path}")
    
    final_output = f"""
    Title: AI-Powered Meeting Summarization and Task Assignment
    
    As a project manager,
    I want to automatically generate summaries and extract action items from my meetings,
    So that I can ensure follow-ups and track decisions without manually reviewing long conversations.
    
    **Meeting Summary:**
    {summary}
    
    **Action Items & Schedule:**
    {tabulate(schedule, headers=["Assigned To", "Task", "Deadline"], tablefmt="grid")}
    """
    
    with open("meeting_summary.txt", "w") as f:
        f.write(final_output)
    print("Summary saved to 'meeting_summary.txt'")
    
    return final_output

if __name__ == "__main__":
    video_file = "recording1.mp4"
    if not os.path.exists(video_file):
        print(f"Error: File '{video_file}' not found. Please upload it or check the path.")
    else:
        output = summarize_meeting(video_file)
        print("\nFinal Output:")
        print(output)