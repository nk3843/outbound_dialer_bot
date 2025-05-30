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
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Robust Error Handling**: Retry mechanisms and comprehensive logging
- **Secure Configuration**: Environment-based configuration management

## Prerequisites

- Python 3.8+
- Twilio Account with Voice capabilities
- A verified phone number for testing (if using trial account)
- A Twilio phone number for outbound calls
- Docker and Docker Compose (for containerized deployment)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/nk3843/outbound_dialer_bot.git
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
cp .env.example .env
# Edit .env with your Twilio credentials and other settings
```

### Docker Deployment

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

Or run in detached mode:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f
```

3. Stop the application:
```bash
docker-compose down
```

## Configuration

The application can be configured through:

1. Environment variables (see `.env.example`)
2. `config.yaml` file
3. Docker Compose environment variables

Key configuration sections:
- Twilio credentials
- Call settings
- IVR configuration
- Logging settings
- Security settings

## Project Structure

```
outbound_dialer_bot/
├── src/
│   ├── voice_api.py      # Flask server for Twilio webhooks
│   ├── watcher.py        # File watcher for new leads
│   ├── call_handler.py   # Twilio call handling logic
│   ├── trigger_call.py   # Call triggering and batch processing
│   ├── summarizer.py     # Call response summarization
│   ├── pipeline.py       # Post-call processing pipeline
│   ├── logger.py         # Centralized logging configuration
│   └── utils.py          # Utility functions
├── leads/                # Directory for lead CSV files
├── logs/                 # Call logs and recordings
├── downloads/           # Downloaded call recordings
├── tests/              # Test files
├── config.yaml         # Configuration file
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
└── README.md         # This file
```

## Lead File Format

Create CSV files in the `leads` directory with the following format:

```csv
name,phone
John Doe,+15551234567
Jane Smith,+15559876543
```

## Running the Application

### Local Development

1. Start the Flask server:
```bash
python src/voice_api.py
```

2. In a separate terminal, start the file watcher:
```bash
python run.py
```

### Docker Deployment

The application is automatically started when using Docker Compose:
```bash
docker-compose up
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

The application can be deployed to any cloud platform that supports Docker:

- AWS ECS/EKS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

## Monitoring and Logging

- Application logs are stored in the `logs` directory
- Call recordings are available through Twilio's API
- Response logs are stored in CSV format for analysis
- Docker container health checks are configured
- Rotating log files with size limits

## Security Considerations

1. **API Security**:
   - Use HTTPS in production
   - Implement rate limiting
   - Validate all incoming requests
   - Secure environment variables

2. **Data Security**:
   - Encrypt sensitive data
   - Secure storage of credentials
   - Regular security audits
   - Non-root Docker user

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
