import time
import os
import sys
import logging
import schedule
import yaml

# Add backend directory to Python path for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.amazon.pipeline import AmazonPipeline

# Configure separate logger for scheduler
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "scheduler.log")),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("amazon.scheduler")

def job():
    logger.info("Executing scheduled Amazon SP-API job...")
    pipeline = AmazonPipeline()
    pipeline.run()

def get_run_time() -> str:
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "amazon_config.yaml")
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            return config.get("scheduler", {}).get("run_time", "02:00")
    except Exception as e:
        logger.error(f"Failed to load scheduler config: {e}. Defaulting to 02:00.")
        return "02:00"

if __name__ == "__main__":
    run_time = get_run_time()
    logger.info(f"Amazon SP-API Scheduler initialized. Job will run daily at {run_time}.")
    
    schedule.every().day.at(run_time).do(job)
    
    # Optional: Run it immediately once on startup for debugging/testing
    if os.getenv("RUN_ON_STARTUP", "false").lower() == "true":
        logger.info("RUN_ON_STARTUP is enabled. Running job now...")
        job()

    while True:
        schedule.run_pending()
        time.sleep(60) # Sleep for a minute to save CPU
