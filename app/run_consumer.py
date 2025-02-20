from app.queue.consumer import TelegramConsumer
from app.core.config import settings
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Create and set event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    consumer = TelegramConsumer(settings.TELEGRAM_BOT_TOKEN)
    try:
        logger.info("Starting consumer...")
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping consumer gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        # Clean up in all cases
        try:
            consumer.channel.close()
            consumer.connection.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            loop.close()
            logger.info("Event loop closed")

if __name__ == "__main__":
    main()
