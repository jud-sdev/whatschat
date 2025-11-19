"""
WhatsApp Handler - Processes incoming messages and sends responses
"""
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from config import settings
from llm_service import llm_service
from knowledge_base import knowledge_base
from conversation_manager import conversation_manager
import logging

logger = logging.getLogger(__name__)


class WhatsAppHandler:
    """Handles WhatsApp message processing and responses"""

    def __init__(self):
        self.twilio_client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        logger.info("WhatsApp handler initialized")

    def process_incoming_message(self, from_number: str, message_body: str) -> str:
        """
        Process an incoming WhatsApp message and generate a response

        Args:
            from_number: Sender's phone number (format: whatsapp:+1234567890)
            message_body: The message text

        Returns:
            Response message to send back
        """
        try:
            logger.info(f"Processing message from {from_number}: {message_body}")

            # Query knowledge base for relevant context
            context = knowledge_base.query(message_body)

            # Get conversation history
            history = conversation_manager.get_history(
                from_number,
                limit=settings.MAX_CONVERSATION_HISTORY
            )

            # Generate response using LLM
            response = llm_service.generate_response(
                user_message=message_body,
                conversation_history=history,
                context=context
            )

            # Save user message and assistant response to conversation history
            conversation_manager.add_message(from_number, "user", message_body)
            conversation_manager.add_message(from_number, "assistant", response)

            logger.info(f"Generated response for {from_number}")
            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "I apologize, but I'm having trouble processing your message. Please try again later or contact our support team."

    def send_message(self, to_number: str, message: str) -> bool:
        """
        Send a WhatsApp message

        Args:
            to_number: Recipient's phone number (format: whatsapp:+1234567890)
            message: Message to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = self.twilio_client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                body=message,
                to=to_number
            )
            logger.info(f"Sent message to {to_number}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def create_response(self, message: str) -> MessagingResponse:
        """
        Create a Twilio MessagingResponse object

        Args:
            message: Response message

        Returns:
            MessagingResponse object for Twilio webhook
        """
        response = MessagingResponse()
        response.message(message)
        return response


# Global WhatsApp handler instance
whatsapp_handler = WhatsAppHandler()
