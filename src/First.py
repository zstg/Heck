#!/usr/bin/env python

import speech_recognition as sr
from transformers import pipeline
import nltk

def transcribe_audio(file_path=None):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None

audio_file = "./harvard.wav"
transcription = transcribe_audio(audio_file)

ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")

def extract_action_items(transcription):
    entities = ner_pipeline(transcription)
    action_items = [entity['word'] for entity in entities if entity['entity_group'] in ['ORG', 'PER', 'DATE']]
    return action_items

if transcription:
    action_items = extract_action_items(transcription)

nltk.download('punkt')

def summarize_conversation(text):
    sentences = nltk.sent_tokenize(text)
    sorted_sentences = sorted(sentences, key=lambda x: len(x), reverse=True)
    summary = sorted_sentences[:3]
    return summary

if transcription:
    summary = summarize_conversation(transcription)

def process_conversation(audio_file):
    transcription = transcribe_audio(audio_file)
    if not transcription:
        return None
    
    action_items = extract_action_items(transcription)
    summary = summarize_conversation(transcription)
    
    return {
        "transcription": transcription,
        "action_items": action_items,
        "summary": summary
    }

audio_file = "./harvard.wav"
result = process_conversation(audio_file)

if result:
    print(result)
