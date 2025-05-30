import os
import csv
from datetime import datetime
from transformers import pipeline
import torch
from summarizer import summarize_text  # Reuse your summarizer function

# Load Whisper model
print("⏳ Loading Whisper model (openai/whisper-base)...")
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base", return_timestamps=True, device=0 if torch.cuda.is_available() else "mps")

# CSV file path
SUMMARY_CSV = os.path.join(os.path.dirname(__file__), '..', 'logs', 'summaries.csv')

# Transcribe audio
def transcribe_audio(audio_file):
    print(f"🎧 Transcribing {audio_file}...")
    result = transcriber(audio_file, return_timestamps=True)
    return result['text']

# Append results to CSV
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
    print(f"✅ Saved summary for {phone_number} / {call_sid}")

# Main
if __name__ == "__main__":
    mp3_file = input("Enter path to MP3 file: ").strip()
    phone_number = input("Enter phone number (E.164 format): ").strip()
    call_sid = input("Enter CallSid: ").strip()

    transcript = transcribe_audio(mp3_file)
    print("\n📝 Transcript:\n", transcript)

    summary, action_items = summarize_text(transcript)
    print("\n📋 Summary:\n", summary)
    print("\n✅ Action Items:\n", action_items)

    save_summary(phone_number, call_sid, transcript, summary, action_items)
