import os
from download_recording import download_recordings
from transcribe import transcribe_audio
from summarizer import summarize_text
from datetime import datetime
import csv

SUMMARY_CSV = os.path.join(os.path.dirname(__file__), '..', 'logs', 'summaries.csv')

def save_summary(phone_number, call_sid, transcript, summary, action_items):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fieldnames = ['phone_number', 'call_sid', 'transcript', 'summary', 'action_items', 'timestamp']
    file_exists = os.path.isfile(SUMMARY_CSV)

    with open(SUMMARY_CSV, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'phone_number': phone_number,
            'call_sid': call_sid,
            'transcript': transcript,
            'summary': summary,
            'action_items': action_items,
            'timestamp': timestamp
        })

def process_call_pipeline(call_sid, phone_number):
    print(f"🚀 Processing call: {call_sid} / {phone_number}")

    # Step 1: Download recording
    mp3_file = download_recordings(call_sid)

    # Step 2: Transcribe
    transcript = transcribe_audio(mp3_file)

    # Step 3: Summarize
    summary, action_items = summarize_text(transcript)

    # Step 4: Save
    save_summary(phone_number, call_sid, transcript, summary, action_items)

    print(f"✅ Processed call {call_sid}")
