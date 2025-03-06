import moviepy.editor as mp
import whisper
import os
import re
import nltk
import spacy
from datetime import datetime, timedelta
from tabulate import tabulate

# Download necessary NLTK data
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

# Load English NLP model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

def extract_audio_from_video(video_path, audio_output_path="output.wav"):
    """Extracts audio from video and saves it as a WAV file."""
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
    """Transcribes the extracted audio using Whisper AI."""
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        print("Transcription completed.")
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

def extract_tasks(text):
    """Extracts actionable tasks using NLP without any external API."""
    sentences = nltk.sent_tokenize(text)
    tasks = []

    for sentence in sentences:
        doc = nlp(sentence)
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        
        # Extract verbs (potential actions)
        words = nltk.word_tokenize(sentence)
        pos_tags = nltk.pos_tag(words)
        actions = [word for word, tag in pos_tags if tag.startswith("VB")]  # Verbs
        
        # Extract deadline (simple rule-based approach)
        deadline_match = re.search(r"in (\d+) days|by (\d{4}-\d{2}-\d{2})", sentence)
        deadline = "N/A"
        if deadline_match:
            if deadline_match.group(1):
                deadline = f"Day {deadline_match.group(1)}"
            elif deadline_match.group(2):
                deadline = deadline_match.group(2)

        # If a person and action are found, register as a task
        if persons and actions:
            person = persons[0]  # Assign the first detected person
            task_desc = " ".join(actions)  # Join verbs into a task description
            tasks.append([person, task_desc, deadline])

    return tasks

def generate_schedule(tasks):
    """Generates a schedule based on extracted tasks and deadlines."""
    today = datetime.today()
    schedule = []

    for task in tasks:
        if len(task) == 3:
            person, task_desc, deadline = task
            try:
                days_offset = int(deadline.strip().replace("Day ", ""))
                deadline_date = (today + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            except ValueError:
                deadline_date = "N/A"
            schedule.append([person.strip(), task_desc.strip(), deadline_date])

    return schedule

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
    
    print("Step 3: Extracting tasks...")
    tasks = extract_tasks(transcription)
    
    print("Step 4: Generating schedule...")
    schedule = generate_schedule(tasks)
    print(schedule)
    
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"Cleaned up temporary file: {audio_path}")
    
    final_output = f"""
    **AI-Powered Meeting Summarization and Task Assignment**
    
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
