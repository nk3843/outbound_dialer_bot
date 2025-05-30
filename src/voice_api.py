from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import logging
import os
import csv
from summarizer import summarize_responses
from datetime import datetime
from pipeline import process_call_pipeline
from flask import send_from_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'responses.csv')

def log_response(phone_number, question, answer, call_sid=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    fieldnames = ['phone_number', 'question', 'answer', 'timestamp', 'call_sid']
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
        'phone_number': phone_number,
        'question': question,
        'answer': answer,
        'timestamp': timestamp,
        'call_sid': call_sid or ""
    })

# Map steps to questions
QUESTIONS = {
    1: "Have you visited a dentist in the last 6 months?",
    2: "Do you currently have dental insurance?",
    3: "Would you like to be connected with a dental care specialist now?"
}

AGENT_NUMBER = "+15856859955"  # Replace with your agent number

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    try:
        step_raw = request.args.get("step", "1")
        try:
            step = int(step_raw)
        except ValueError:
            step = 1

        digits = request.form.get("Digits")
        from_number = request.form.get("From", "Unknown")
        call_sid = request.form.get("CallSid")

        # Log any user input
        if digits and (step - 1) in QUESTIONS:
            log_response(from_number, QUESTIONS[step - 1], digits, call_sid)
            logger.info(f"📞 Logged response from {from_number}: {QUESTIONS[step - 1]} -> {digits}")

        response = VoiceResponse()

        if step in QUESTIONS:
            gather = Gather(
                num_digits=1,
                action=f"/voice?step={step + 1}",
                method="POST",
                timeout=10
            )
            gather.say(QUESTIONS[step])
            response.append(gather)
        else:
            summary_result = summarize_responses(from_number)
            if summary_result:
                logger.info(f"Generated summary for {from_number}:\n{summary_result}")

            response.say("Thank you. Please hold while I transfer you to a live agent.")
            response.dial(
                AGENT_NUMBER,
                record="record-from-answer-dual",
                action="/call-complete",
                method="POST"
            )

            logger.info(f"📞 Final CallSid for agent transfer (to fetch recording later): {call_sid}")

        twiml_response = str(response)
        logger.info("Generated TwiML: %s", twiml_response)
        return Response(twiml_response, mimetype="text/xml")

    except Exception as e:
        logger.error("Error in voice endpoint: %s", str(e))
        response = VoiceResponse()
        response.say("We're sorry, but we encountered an error. Please try your call again later.")
        return Response(str(response), mimetype="text/xml")

@app.route("/call-complete", methods=["POST"])
def call_complete():
    call_sid = request.form.get("CallSid")
    from_number = request.form.get("From")
    logger.info(f"📞 Call complete! CallSid: {call_sid}, From: {from_number}")

    # Kick off the pipeline
    process_call_pipeline(call_sid, from_number)

    return "OK", 200


@app.route("/logs/<path:filename>")
def serve_logs(filename):
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    return send_from_directory(logs_dir, filename)



@app.route("/", methods=["GET"])
def home():
    return "Flask Twilio Voice Server is running. POST to /voice for TwiML."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
