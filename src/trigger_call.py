import threading
import time
import logging
from typing import List, Dict, Any
from .call_handler import call_handler

logger = logging.getLogger(__name__)

def trigger_call_batch(leads: List[Dict[str, Any]], test_mode: bool = False) -> List[str]:
    """
    Trigger calls for a batch of leads with rate limiting.
    
    Args:
        leads: List of lead dictionaries
        test_mode: If True, use test phone numbers
        
    Returns:
        List[str]: List of successful call SIDs
    """
    successful_calls = []
    threads = []
    
    for lead in leads:
        # Extract and validate phone number
        phone = lead.get('phone', '')
        if not phone:
            logger.error(f"❌ No phone number found for lead: {lead}")
            continue
            
        # Create and start thread for the call
        t = threading.Thread(
            target=lambda l: successful_calls.append(call_handler.place_call(l, test_mode)),
            args=(lead,)
        )
        t.start()
        threads.append(t)
        
        # Rate limiting - wait between calls
        time.sleep(call_handler.rate_limit_delay)
    
    # Wait for all calls to complete
    for t in threads:
        t.join()
        
    return [sid for sid in successful_calls if sid is not None]
