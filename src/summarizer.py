from transformers import pipeline
import os
import csv

import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

RESPONSES_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'responses.csv')

def map_answer(answer):
    answer = answer.strip()
    if answer == "1":
        return "Yes"
    elif answer == "2":
        return "No"
    else:
        return answer

def read_responses(phone_number):
    responses = []
    with open(RESPONSES_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['phone_number'] == phone_number:
                responses.append(row)
    return responses

SUMMARIES_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'summaries.csv')


def save_summary(phone_number, summary_text, action_items_list):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    file_exists = os.path.isfile(SUMMARIES_FILE)
    with open(SUMMARIES_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['phone_number', 'summary', 'action_items', 'timestamp'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'phone_number': phone_number,
            'summary': summary_text,
            'action_items': "; ".join(action_items_list),
            'timestamp': timestamp
        })

def summarize_text(transcript_text):
    # Your existing pipeline call:
    summary = summarizer(transcript_text, max_length=60, min_length=20, do_sample=False)[0]['summary_text']
    action_items = "- Transfer the call to an agent.; - Schedule a follow-up appointment.; - Send a summary email."
    return summary, action_items


def summarize_responses(phone_number):
    responses = read_responses(phone_number)
    if not responses:
        return None

    context = "The customer has provided the following information: "
    statements = []
    for r in responses:
        q = r['question'].rstrip("?").capitalize()
        a = map_answer(r['answer'])
        if q.startswith("Have you") and a.lower() == "yes":
            statements.append(f"The customer has {q[9:].lower()}")
        elif q.startswith("Do you") and a.lower() == "yes":
            statements.append(f"The customer does {q[6:].lower()}")
        elif q.startswith("Would you like") and a.lower() == "yes":
            statements.append(f"The customer would like to {q[16:].lower()}")
        else:
            statements.append(f"{q}: {a}")

    context += ". ".join(statements) + "."


    max_len = min(60, len(context.split()) + 20)
    summary_raw = summarizer(context, max_length=max_len, min_length=20, do_sample=False)[0]['summary_text']
    summary = summary_raw.replace("The customer provided the following information:", "").strip().capitalize()

    action_items = [
        "- Transfer the call to an agent.",
        "- Schedule a follow-up appointment.",
        "- Send a summary email."
    ]

    save_summary(phone_number, summary, action_items)
    result = f"Summary: {summary}\nAction Items:\n" + "\n".join(action_items)
    return result

if __name__ == "__main__":
    phone = input("Enter phone number (E.164 format): ")
    summary = summarize_responses(phone)
    print(summary or "No responses found.")
