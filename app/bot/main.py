import asyncio
import logging
from .client import APIClient
import os
from dotenv import load_dotenv
import sys
from signal import signal, SIGINT, SIGTERM, SIGABRT

load_dotenv()

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)
from telegram import Update
from .handlers.homework import HomeworkHandler, AWAITING_CONTENT, AWAITING_STUDENTS
from .handlers.submission import SubmissionHandler, AWAITING_HOMEWORK_SELECTION, AWAITING_SUBMISSION
from .handlers.feedback import FeedbackHandler, AWAITING_SUBMISSION_SELECTION, AWAITING_FEEDBACK
from .handlers.basic import BasicHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DanceEducationBot:
    def __init__(self):
        self.api_client = APIClient()
        self.application = None

    async def verify_api_connection(self):
         max_attempts = 5
         delay = 1

         for attempt in range(max_attempts):
             if await self.api_client.check_health():
                 logger.info("Successfully connected to API")
                 return True

             if attempt < max_attempts - 1:
                 logger.warning(f"API connection attempt {attempt + 1} failed, retrying in {delay}s...")
                 await asyncio.sleep(delay)
                 delay *= 2

         raise RuntimeError("Could not connect to API after multiple attempts")

    def setup(self):
        """Initialize bot and handlers"""
        # Verify API connection first
        asyncio.get_event_loop().run_until_complete(self.verify_api_connection())

        # Initialize handlers
        basic_handler = BasicHandler(self.api_client)
        homework_handler = HomeworkHandler(self.api_client)
        submission_handler = SubmissionHandler(self.api_client)
        feedback_handler = FeedbackHandler(self.api_client)

        # Build application
        self.application = Application.builder().token(
            os.getenv("TELEGRAM_BOT_TOKEN")
        ).build()

        # Add basic handlers
        self.application.add_handler(CommandHandler("start", basic_handler.start))
        self.application.add_handler(CommandHandler("help", basic_handler.help))
        self.application.add_handler(
            CallbackQueryHandler(basic_handler.role_callback, pattern="^role_")
        )

        # Add other handlers
        self.application.add_handler(CommandHandler("homework", homework_handler.list_homework))
        self.application.add_handler(
            CallbackQueryHandler(
                homework_handler.handle_submit_button,
                pattern="^submit_homework$"
            )
        )
        self.application.add_handler(ConversationHandler(
            entry_points=[CommandHandler("assign", homework_handler.start_assign)],
            states={
                AWAITING_CONTENT: [MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    homework_handler.handle_homework_content
                )],
                AWAITING_STUDENTS: [CallbackQueryHandler(
                    homework_handler.handle_student_selection,
                    pattern="^(usr_|done)"
                )]
            },
            fallbacks=[CommandHandler("cancel", homework_handler.cancel)]
        ))

        self.application.add_handler(ConversationHandler(
            entry_points=[CommandHandler("submit", submission_handler.start_submit)],
            states={
                AWAITING_HOMEWORK_SELECTION: [
                    CallbackQueryHandler(submission_handler.handle_homework_selection)
                ],
                AWAITING_SUBMISSION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        submission_handler.handle_submission
                    )
                ]
            },
            fallbacks=[CommandHandler("cancel", submission_handler.cancel)]
        ))


        self.application.add_handler(
            CommandHandler("feedback", feedback_handler.list_feedback)
        )

        # Add callback handler for main menu button
        self.application.add_handler(
            CallbackQueryHandler(
                basic_handler.return_to_main_menu,
                pattern="^main_menu$"
            )
        )

        self.application.add_handler(ConversationHandler(
            entry_points=[CommandHandler("pending_feedback", feedback_handler.list_pending_feedback)],
            states={
                AWAITING_SUBMISSION_SELECTION: [
                    CallbackQueryHandler(feedback_handler.handle_submission_selection)
                ],
                AWAITING_FEEDBACK: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        feedback_handler.handle_feedback
                    )
                ]
            },
            fallbacks=[CommandHandler("cancel", feedback_handler.cancel)]
        ))

    def start(self):
        """Start the bot"""
        # self.application.initialize()
        # await self.application.start()
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def stop(self):
        """Stop the bot"""
        if self.application:
            self.application.stop()
            # await self.application.shutdown()

        # Close API client
        # await self.api_client.close()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Signal received: {signum}")
    sys.exit(0)

def main():
    """Main function"""
    bot = DanceEducationBot()
    bot.setup()

    # Define signal handlers
    # def signal_handler(signum, frame):
    #     asyncio.create_task(bot.stop())

    # Register signal handlers
    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)
    signal(SIGABRT, signal_handler)

    try:
        bot.start()
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
    finally:
        bot.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)


# import asyncio
# import logging
# import os
# from dotenv import load_dotenv
# import sys
# from signal import signal, SIGINT, SIGTERM, SIGABRT

# load_dotenv()

# from telegram.ext import Application
# from telegram import Update

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# class DanceEducationBot:
#     def __init__(self):
#         self.application = None

#     async def setup(self):
#         """Initialize bot and handlers"""
#         self.application = Application.builder().token(
#             os.getenv("TELEGRAM_BOT_TOKEN")
#         ).build()

#     async def start(self):
#         """Start the bot"""
#         # Just run polling without separate initialize/start calls
#         await self.application.run_polling(allowed_updates=Update.ALL_TYPES)

#     async def stop(self):
#         """Stop the bot"""
#         if self.application:
#             await self.application.stop()

# def signal_handler(signum, frame):
#     """Handle shutdown signals"""
#     logger.info(f"Signal received: {signum}")
#     sys.exit(0)

# async def main():
#     """Main function"""
#     bot = DanceEducationBot()
#     await bot.setup()

#     signal(SIGINT, signal_handler)
#     signal(SIGTERM, signal_handler)
#     signal(SIGABRT, signal_handler)

#     try:
#         await bot.start()
#     except Exception as e:
#         logger.error(f"Error running bot: {e}", exc_info=True)
#     finally:
#         await bot.stop()

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Process interrupted by user")
#     except Exception as e:
#         logger.error(f"Error running bot: {e}", exc_info=True)
