"""
Main FastAPI Application
WhatsApp AI Bot with Knowledge Base
"""
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import PlainTextResponse
from whatsapp_handler import whatsapp_handler
from knowledge_base import knowledge_base
from conversation_manager import conversation_manager
from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp AI Bot",
    description="AI-powered WhatsApp bot with knowledge base integration",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "app": "WhatsApp AI Bot",
        "knowledge_base_documents": knowledge_base.count()
    }


@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "healthy"}


@app.post("/webhook/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(None),
    ProfileName: str = Form(None)
):
    """
    Webhook endpoint for receiving WhatsApp messages from Twilio

    Args:
        From: Sender's phone number (format: whatsapp:+1234567890)
        Body: Message text
        MessageSid: Twilio message SID
        ProfileName: Sender's WhatsApp profile name
    """
    try:
        logger.info(f"Received message from {From} ({ProfileName}): {Body}")

        # Process the message and get response
        response_text = whatsapp_handler.process_incoming_message(From, Body)

        # Create and return Twilio response
        response = whatsapp_handler.create_response(response_text)

        return str(response)

    except Exception as e:
        logger.error(f"Error in webhook: {e}", exc_info=True)
        # Return a friendly error message
        response = whatsapp_handler.create_response(
            "Sorry, I encountered an error. Please try again later."
        )
        return str(response)


@app.post("/send-message")
async def send_message(request: Request):
    """
    API endpoint to send a message to a WhatsApp number

    Body: {
        "to": "whatsapp:+1234567890",
        "message": "Your message here"
    }
    """
    try:
        data = await request.json()
        to_number = data.get("to")
        message = data.get("message")

        if not to_number or not message:
            raise HTTPException(status_code=400, detail="Missing 'to' or 'message' in request")

        success = whatsapp_handler.send_message(to_number, message)

        if success:
            return {"status": "sent", "to": to_number}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge-base/count")
async def get_knowledge_base_count():
    """Get the number of documents in the knowledge base"""
    return {"count": knowledge_base.count()}


@app.post("/knowledge-base/clear")
async def clear_knowledge_base():
    """Clear all documents from the knowledge base"""
    knowledge_base.clear()
    return {"status": "cleared", "count": knowledge_base.count()}


@app.post("/conversation/clear/{phone_number}")
async def clear_conversation(phone_number: str):
    """
    Clear conversation history for a specific phone number

    Args:
        phone_number: Phone number in format: whatsapp:+1234567890
    """
    conversation_manager.clear_history(phone_number)
    return {"status": "cleared", "phone_number": phone_number}


@app.get("/conversation/{phone_number}")
async def get_conversation(phone_number: str):
    """
    Get conversation history for a specific phone number

    Args:
        phone_number: Phone number in format: whatsapp:+1234567890
    """
    history = conversation_manager.get_history(phone_number)
    return {"phone_number": phone_number, "history": history}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
