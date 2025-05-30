import os
import logging
import time
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import yaml

# Configure logging

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'calls.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class TwilioCallHandler:
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the Twilio call handler with configuration."""
        self.config = self._load_config(config_path)
        self.client = self._initialize_twilio_client()
        self.rate_limit_delay = self.config.get('call_settings', {}).get('delay_between_calls', 2)
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {str(e)}")
            raise

    def _initialize_twilio_client(self) -> Client:
        """Initialize Twilio client with credentials."""
        try:
            account_sid = os.getenv("TWILIO_ACCOUNT_SID", self.config['twilio']['account_sid'])
            auth_token = os.getenv("TWILIO_AUTH_TOKEN", self.config['twilio']['auth_token'])
            return Client(account_sid, auth_token)
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            raise

    def _format_phone_number(self, phone: str) -> str:
        """Ensure phone number is in E.164 format."""
        if not phone:
            return ""
        # Convert to string if it's an integer
        phone_str = str(phone)
        # Remove any spaces or special characters
        phone_str = ''.join(filter(str.isdigit, phone_str))
        # Add + if not present
        return phone_str if phone_str.startswith('+') else f"+{phone_str}"

    def _get_twiml(self, lead: Dict[str, Any]) -> str:
        """Generate TwiML for the call."""
        # You can customize this based on your needs
        return f'''<Response>
            <Say>Hello {lead.get('name', 'there')}! This is Rexy, your AI agent. 
            I have a few quick questions for you.</Say>
        </Response>'''

    def place_call(self, lead: Dict[str, Any], test_mode: bool = False) -> Optional[str]:
        """
        Place a call using Twilio's REST API.
        
        Args:
            lead: Dictionary containing lead information
            test_mode: If True, use test phone number instead of lead's number
            
        Returns:
            Optional[str]: Call SID if successful, None if failed
        """
        to_number = self._format_phone_number(
            self.config['twilio']['test_number'] if test_mode else lead.get('phone', '')
        )
        
        if not to_number:
            logger.error(f"No valid phone number found for lead: {lead}")
            return None

        from_number = self._format_phone_number(self.config['twilio']['phone_number'])
        
        logger.info(f"📞 Initiating call to {lead.get('name', 'Unknown')} at {to_number}")
        
        for attempt in range(self.max_retries):
            try:
                call = self.client.calls.create(
                    to=to_number,
                    from_=from_number,
                    url=self.config['twilio']['twiml_url']  # e.g., ngrok/Flask endpoint
)
                logger.info(f"✅ Call initiated to {lead.get('name', 'Unknown')} (SID: {call.sid})")
                return call.sid
                
            except TwilioRestException as e:
                if e.code == 21211:  # Invalid phone number
                    logger.error(f"Invalid phone number format: {to_number}")
                    return None
                elif e.code == 21214:  # Phone number not verified
                    logger.error(f"Phone number not verified: {to_number}")
                    return None
                elif attempt < self.max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"❌ Failed to call {lead.get('name', 'Unknown')}: {str(e)}")
                    return None
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error calling {lead.get('name', 'Unknown')}: {str(e)}")
                return None

   
# Create a singleton instance
call_handler = TwilioCallHandler()

if __name__ == "__main__":
    # Test the call handler
    test_lead = {"name": "John Doe", "phone": "+15555555555"}
    call_handler.place_call(test_lead, test_mode=True)
