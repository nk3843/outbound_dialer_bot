# Outbound Dialer Bot

An automated outbound calling system built with Python, Twilio, and Flask. This system watches for new lead files, processes them, and makes automated calls with an interactive voice response (IVR) system.

## Features

- **Automated Lead Processing**: Watches a directory for new CSV files containing leads
- **Interactive Voice Response**: Multi-step IVR system for gathering information
- **Call Recording**: Records calls for quality assurance and training
- **Response Logging**: Logs all call responses for analysis
- **Live Agent Transfer**: Seamless transfer to live agents when needed
- **Call Pipeline**: Post-call processing and analysis
- **Production-Ready**: Built with Flask for reliability and ease of deployment

## Prerequisites

- Python 3.8+
- Twilio Account with Voice capabilities
- A verified phone number for testing (if using trial account)
- A Twilio phone number for outbound calls

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/outbound_dialer_bot.git
cd outbound_dialer_bot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_NUMBER="your_twilio_number"
```

## Configuration

Create a `config.yaml` file in the root directory:

```yaml
twilio:
  account_sid: "your_account_sid"
  auth_token: "your_auth_token"
  phone_number: "+1234567890"  # Your Twilio number
  test_number: "+1987654321"   # For testing

call_settings:
  concurrency_limit: 10
  delay_between_calls: 2  # in seconds

knowledge_base:
  source: "vector_db"  # or "static_file"

transfer:
  live_agent_number: "+1234567890"  # Your agent's number
```

## Project Structure

```
outbound_dialer_bot/
├── src/
│   ├── voice_api.py      # Flask server for Twilio webhooks
│   ├── watcher.py        # File watcher for new leads
│   ├── call_handler.py   # Twilio call handling logic
│   ├── trigger_call.py   # Call triggering and batch processing
│   ├── summarizer.py     # Call response summarization
│   └── pipeline.py       # Post-call processing pipeline
├── leads/                # Directory for lead CSV files
├── logs/                 # Call logs and recordings
├── tests/               # Test files
├── config.yaml          # Configuration file
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Lead File Format

Create CSV files in the `leads` directory with the following format:

```csv
name,phone
John Doe,+15551234567
Jane Smith,+15559876543
```

## Running the Application

1. Start the Flask server:
```bash
python src/voice_api.py
```

2. In a separate terminal, start the file watcher:
```bash
python run.py
```

The server will be available at:
- Main endpoint: `http://localhost:5001/voice`
- Health check: `http://localhost:5001/`

## Development

### Setting up ngrok for local development

1. Install ngrok:
```bash
brew install ngrok  # macOS
# or download from https://ngrok.com/download
```

2. Start ngrok:
```bash
ngrok http 5001
```

3. Update your Twilio webhook URL with the ngrok URL:
```
https://your-ngrok-url.ngrok.io/voice
```

### Running Tests

```bash
pytest tests/
```

## Production Deployment

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t outbound-dialer-bot .
```

2. Run the container:
```bash
docker run -p 5001:5001 \
  -e TWILIO_ACCOUNT_SID=your_sid \
  -e TWILIO_AUTH_TOKEN=your_token \
  -e TWILIO_PHONE_NUMBER=your_number \
  outbound-dialer-bot
```

### Cloud Deployment

The application can be deployed to any cloud platform that supports Python applications:

- AWS Elastic Beanstalk
- Google Cloud Run
- Heroku
- DigitalOcean App Platform

## Monitoring and Logging

- Application logs are stored in the `logs` directory
- Call recordings are available through Twilio's API
- Response logs are stored in CSV format for analysis

## Security Considerations

1. **API Security**:
   - Use HTTPS in production
   - Implement rate limiting
   - Validate all incoming requests

2. **Data Security**:
   - Encrypt sensitive data
   - Secure storage of credentials
   - Regular security audits

3. **Compliance**:
   - TCPA compliance for outbound calls
   - Data privacy regulations
   - Call recording consent

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Open an issue in the repository
3. Contact the maintainers

## Acknowledgments

- Twilio for the voice API
- Flask for the web framework
- All contributors to the project
