import os
import torch
from transformers import pipeline
from datetime import datetime

# Load model
print("⏳ Loading Whisper model (openai/whisper-base)...")
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base", device=0 if torch.cuda.is_available() else "mps")

# Transcribe
def transcribe_audio(audio_file):
    if isinstance(audio_file, list):
        transcripts = []
        for file in audio_file:
            result = transcriber(file, return_timestamps=True)
            text = result['text']  # Extract text
            transcripts.append(text)
            print(f"✅ Transcription for {file}: {text}")
        return transcripts
    else:
        result = transcriber(audio_file, return_timestamps=True)
        text = result['text']
        print(f"✅ Transcription for {audio_file}: {text}")
        return text


# Save transcript
def save_transcript(text, output_file):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(output_file, 'w') as f:
        f.write(f"Transcription ({timestamp}):\n{text}")
    print(f"📝 Transcript saved to {output_file}")

if __name__ == "__main__":
    file_path = input("Enter path to MP3 file: ").strip()
    if not os.path.exists(file_path):
        print("❌ File not found.")
        exit(1)
    
    transcript = transcribe_audio(file_path)
    output_file = f"{os.path.splitext(file_path)[0]}_transcript.txt"
    save_transcript(transcript, output_file)
