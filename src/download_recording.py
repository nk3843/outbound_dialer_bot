import os
import time
import yaml
import requests
from twilio.rest import Client

# Load credentials from config.yaml
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

account_sid = config['twilio']['account_sid']
auth_token = config['twilio']['auth_token']
client = Client(account_sid, auth_token)

def download_recordings(call_sid, save_dir=None, retries=5, delay=5, min_file_size=2000):
    if save_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_dir = os.path.join(project_root, 'downloads')

    os.makedirs(save_dir, exist_ok=True)

    for attempt in range(retries):
        print(f"⏳ Checking for recordings (Attempt {attempt+1}/{retries})...")
        recordings = client.recordings.list(call_sid=call_sid)

        if recordings:
            print(f"✅ Found {len(recordings)} recording(s).")
            downloaded_files = []
            for recording in recordings:
                media_url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
                print(f"🔗 Downloading from: {media_url}")

                response = requests.get(media_url, auth=(account_sid, auth_token))
                filename = os.path.join(save_dir, f"recording_{recording.sid}.mp3")

                with open(filename, "wb") as f:
                    f.write(response.content)

                file_size = os.path.getsize(filename)
                if file_size < min_file_size:
                    print(f"⚠️ Warning: File {filename} is too small ({file_size} bytes). Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue  # Try again in the next iteration
                else:
                    print(f"✅ Downloaded {filename} ({file_size} bytes)")
                    downloaded_files.append(filename)

            if downloaded_files:
                return downloaded_files  # Return list of downloaded file paths
            else:
                print(f"⚠️ No valid recordings downloaded yet. Retrying in {delay} seconds...")

        else:
            print(f"❌ No recordings found for CallSid: {call_sid}. Retrying in {delay} seconds...")

        time.sleep(delay)

    print(f"❌ No valid recordings found after {retries} attempts for CallSid: {call_sid}")
    return None

if __name__ == "__main__":
    call_sid = input("Enter the CallSid: ").strip()
    files = download_recordings(call_sid)
    if files:
        print(f"✅ All recordings downloaded: {files}")
    else:
        print("❌ No recordings available for this CallSid.")
