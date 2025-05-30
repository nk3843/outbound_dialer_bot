from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas as pd
import time
import os
import logging
from typing import List, Dict, Any
from .trigger_call import trigger_call_batch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

WATCH_DIR = "leads"

class LeadHandler(FileSystemEventHandler):
    def __init__(self):
        """Initialize the lead handler."""
        # Ensure the watch directory exists
        if not os.path.exists(WATCH_DIR):
            os.makedirs(WATCH_DIR)
            logger.info(f"Created watch directory: {WATCH_DIR}")

    def _validate_csv(self, file_path: str) -> bool:
        """Validate that the CSV file has the required columns."""
        try:
            df = pd.read_csv(file_path)
            required_columns = ['name', 'phone']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"CSV file {file_path} missing required columns: {required_columns}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error validating CSV file {file_path}: {str(e)}")
            return False

    def _process_leads(self, file_path: str) -> List[Dict[str, Any]]:
        """Process leads from a CSV file."""
        try:
            if not self._validate_csv(file_path):
                return []

            df = pd.read_csv(file_path)
            leads = df.to_dict(orient='records')
            logger.info(f"Successfully loaded {len(leads)} leads from {file_path}")
            return leads
        except Exception as e:
            logger.error(f"Error processing leads from {file_path}: {str(e)}")
            return []

    def on_created(self, event):
        """Handle new file creation events."""
        if event.src_path.endswith(".csv"):
            logger.info(f"📁 New lead file detected: {event.src_path}")
            
            # Wait a moment to ensure file is completely written
            time.sleep(1)
            
            leads = self._process_leads(event.src_path)
            if leads:
                logger.info(f"Processing {len(leads)} leads from {event.src_path}")
                trigger_call_batch(leads)
            else:
                logger.warning(f"No valid leads found in {event.src_path}")

def run():
    """Run the file watcher."""
    event_handler = LeadHandler()
    observer = Observer()
    
    try:
        observer.schedule(event_handler, WATCH_DIR, recursive=False)
        observer.start()
        logger.info(f"🟢 Watching {WATCH_DIR} for new leads...")
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, stopping watcher...")
        observer.stop()
    except Exception as e:
        logger.error(f"Error in watcher: {str(e)}")
        observer.stop()
    finally:
        observer.join()
        logger.info("Watcher stopped.")
