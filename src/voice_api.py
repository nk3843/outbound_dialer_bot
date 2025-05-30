from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from twilio.twiml.voice_response import VoiceResponse, Gather
import logging
import os
import csv
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from summarizer import summarize_responses
from pipeline import process_call_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'responses.csv')
AGENT_NUMBER = "+15856859955"  # Replace with your agent number

# Map steps to questions
QUESTIONS = {
    1: "Have you visited a dentist in the last 6 months?",
    2: "Do you currently have dental insurance?",
    3: "Would you like to be connected with a dental care specialist now?"
}

# Pydantic models for request/response validation
class CallResponse(BaseModel):
    phone_number: str
    question: str
    answer: str
    timestamp: str
    call_sid: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(title="Twilio Voice API", description="IVR system for dental appointments")

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_response(phone_number: str, question: str, answer: str, call_sid: Optional[str] = None) -> None:
    """Log call responses to CSV file."""
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

@app.post("/voice")
async def voice(request: Request) -> Response:
    """Handle incoming voice calls and IVR logic."""
    try:
        # Parse form data
        form_data = await request.form()
        step_raw = request.query_params.get("step", "1")
        
        try:
            step = int(step_raw)
        except ValueError:
            step = 1

        digits = form_data.get("Digits")
        from_number = form_data.get("From", "Unknown")
        call_sid = form_data.get("CallSid")

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
        
        return Response(content=twiml_response, media_type="text/xml")

    except Exception as e:
        logger.error("Error in voice endpoint: %s", str(e))
        response = VoiceResponse()
        response.say("We're sorry, but we encountered an error. Please try your call again later.")
        return Response(content=str(response), media_type="text/xml")

@app.post("/call-complete")
async def call_complete(request: Request) -> PlainTextResponse:
    """Handle call completion and trigger pipeline processing."""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        from_number = form_data.get("From")
        logger.info(f"📞 Call complete! CallSid: {call_sid}, From: {from_number}")

        # Kick off the pipeline
        process_call_pipeline(call_sid, from_number)

        return PlainTextResponse("OK")
    except Exception as e:
        logger.error(f"Error in call-complete endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/logs/{filename}")
async def serve_logs(filename: str) -> FileResponse:
    """Serve log files."""
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    file_path = os.path.join(logs_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Log file not found")
        
    return FileResponse(file_path)

@app.get("/")
async def home() -> PlainTextResponse:
    """Health check endpoint."""
    return PlainTextResponse("FastAPI Twilio Voice Server is running. POST to /voice for TwiML.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
