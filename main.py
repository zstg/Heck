import moviepy.editor as mp
import whisper
import os
from datetime import datetime, timedelta
from tabulate import tabulate
from transformers import pipeline

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

def extract_tasks(text):
    try:
        extractor = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")
        system_prompt = (
            "Extract actionable tasks from the given meeting transcription. "
            "Each task should be assigned to a person with a logical deadline. "
            "Output in the format: Person | Task | Deadline."
        )
        tasks_output = extractor(system_prompt + "\n" + text, max_length=800, do_sample=False)
        # tasks = tasks_output[0]['generated_text'].split("\n")
        print(f"TASKA: {tasks_output}")
        return [task.split('|') for task in tasks if '|' in task]
    except Exception as e:
        print(f"Error extracting tasks: {e}")
        return []

def generate_schedule(tasks):
    today = datetime.today()
    schedule = []
    for task in tasks:
        if len(task) == 3:
            person, task_desc, deadline = task
            try:
                days_offset = int(deadline.strip().replace("Day ", ""))
                deadline = (today + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            except ValueError:
                deadline = "N/A"
            schedule.append([person.strip(), task_desc.strip(), deadline])
    return schedule

def meeting_function(video_path):
    print("Step 1: Extracting audio...")
    audio_path = extract_audio_from_video(video_path)
    if not audio_path:
        return "Failed to extract audio from the video."
    
    print("Step 2: Transcribing audio to text...")
    transcription = transcribe_audio(audio_path)
    if not transcription:
        os.remove(audio_path)
        return "Failed to transcribe audio."
    
    print("Step 3: Extracting tasks...")
    tasks = extract_tasks(transcription)
    
    print("Step 4: Generating schedule...")
    schedule = generate_schedule(tasks)
    print(schedule)
    
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"Cleaned up temporary file: {audio_path}")
    
    final_output = f"""
    Title: AI-Powered Meeting Summarization and Task Assignment
    
    **Action Items & Schedule:**
    {tabulate(schedule, headers=["Assigned To", "Task", "Deadline"], tablefmt="grid")}
    """
    
    with open("meeting_summary.txt", "w") as f:
        f.write(final_output)
    print("Summary saved to 'meeting_summary.txt'")
    
    return final_output

if __name__ == "__main__":
    video_file = "recording_1.mp4"
    if not os.path.exists(video_file):
        print(f"Error: File '{video_file}' not found. Please upload it or check the path.")
    else:
        output = meeting_function(video_file)
        print("\nFinal Output:")
        print(output)
