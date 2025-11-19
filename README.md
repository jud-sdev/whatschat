# WhatsApp AI Bot with Knowledge Base

An intelligent WhatsApp chatbot that automatically responds to customer messages using AI (OpenAI GPT-4 or Anthropic Claude) with context from your custom knowledge base.

## Features

- **Automatic Responses**: Instantly responds to WhatsApp messages 24/7
- **Multi-turn Conversations**: Maintains conversation context for natural interactions
- **Knowledge Base Integration**: Answers questions based on your business documents (RAG)
- **LLM Powered**: Choose between OpenAI GPT-4 or Anthropic Claude
- **Conversation Memory**: Remembers conversation history for each customer
- **Easy Deployment**: Deploy to Render with one click
- **Document Support**: Ingest PDFs, DOCX, and TXT files into knowledge base

## Architecture

```
WhatsApp Message → Twilio → FastAPI Webhook → LLM (GPT-4/Claude) → Response
                                   ↓
                            Knowledge Base (ChromaDB + RAG)
                                   ↓
                          Conversation Memory (Redis/In-Memory)
```

## Prerequisites

1. **Twilio Account** with WhatsApp Business API access
   - Sign up at [twilio.com](https://www.twilio.com/try-twilio)
   - Get WhatsApp sandbox or production access

2. **LLM API Key** (choose one):
   - OpenAI API key from [platform.openai.com](https://platform.openai.com/)
   - Anthropic API key from [console.anthropic.com](https://console.anthropic.com/)

3. **Render Account** (for deployment)
   - Sign up at [render.com](https://render.com/)

## Quick Start

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd whatschat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required variables:**
```env
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# LLM (OpenAI or Anthropic)
OPENAI_API_KEY=your_openai_key
LLM_PROVIDER=openai  # or "anthropic"
```

### 3. Add Knowledge to Your Bot

Prepare your business documents (FAQs, product info, policies, etc.) and add them to the knowledge base:

```bash
# Ingest a single file
python ingest_knowledge.py path/to/document.pdf

# Ingest all files in a directory
python ingest_knowledge.py --dir ./knowledge_base

# Add raw text
python ingest_knowledge.py --text "Your business information here"
```

### 4. Run Locally

```bash
# Start the server
python app.py

# Or with uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` to see if it's running.

### 5. Test with ngrok (Local Testing)

To test with WhatsApp before deploying:

```bash
# Install ngrok: https://ngrok.com/
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Set this as your Twilio webhook URL:
# https://abc123.ngrok.io/webhook/whatsapp
```

## Deployment to Render

### Option 1: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Render will detect `render.yaml` and set up automatically
6. Add your environment variables in the Render dashboard

### Option 2: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: whatsapp-ai-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (copy from .env)
6. Click "Create Web Service"

### Get Your Webhook URL

After deployment, Render will give you a URL like:
```
https://whatsapp-ai-bot-xyz.onrender.com
```

Your webhook URL will be:
```
https://whatsapp-ai-bot-xyz.onrender.com/webhook/whatsapp
```

## Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
3. In the **Sandbox** settings or your WhatsApp number configuration
4. Set the webhook URL:
   ```
   https://your-render-url.onrender.com/webhook/whatsapp
   ```
5. Method: **POST**
6. Save

## Usage

Once deployed and configured:

1. **Send a WhatsApp message** to your Twilio number
2. **Bot responds automatically** using your knowledge base
3. **Continue conversation** - the bot remembers context
4. **Bot answers questions** based on your uploaded documents

### Example Conversation

```
Customer: Hi, what are your business hours?
Bot: Based on our information, we're open Monday-Friday 9AM-5PM EST.
     How can I help you today?

Customer: Do you offer refunds?
Bot: Yes! We offer a 30-day money-back guarantee on all products...
```

## API Endpoints

- `GET /` - Health check
- `POST /webhook/whatsapp` - WhatsApp webhook (Twilio)
- `POST /send-message` - Send a message programmatically
- `GET /knowledge-base/count` - Get number of documents
- `POST /knowledge-base/clear` - Clear knowledge base
- `GET /conversation/{phone_number}` - Get conversation history
- `POST /conversation/clear/{phone_number}` - Clear conversation

## Knowledge Base Management

### Supported File Types

- `.txt` - Plain text files
- `.pdf` - PDF documents
- `.docx` - Word documents

### Ingestion Commands

```bash
# Add a single file
python ingest_knowledge.py document.pdf

# Add all files in a directory
python ingest_knowledge.py --dir ./my_documents

# Add text directly
python ingest_knowledge.py --text "Important business information"

# Clear knowledge base
python ingest_knowledge.py --clear
```

### Best Practices

1. **Structure your documents**: Use clear headings and sections
2. **Avoid duplicates**: Don't upload the same information multiple times
3. **Keep it relevant**: Only upload business-related documents
4. **Update regularly**: Re-upload documents when information changes

## Configuration Options

Edit these in your `.env` file:

```env
# LLM Settings
LLM_PROVIDER=openai          # "openai" or "anthropic"
OPENAI_MODEL=gpt-4-turbo-preview
ANTHROPIC_MODEL=claude-3-sonnet-20240229
MAX_TOKENS=1000              # Max response length
TEMPERATURE=0.7              # Response creativity (0-1)

# Conversation
MAX_CONVERSATION_HISTORY=10  # Messages to remember

# Knowledge Base
CHUNK_SIZE=1000             # Text chunk size for vector DB
CHUNK_OVERLAP=200           # Overlap between chunks
```

## Troubleshooting

### Bot doesn't respond
- Check Render logs for errors
- Verify Twilio webhook URL is correct
- Ensure environment variables are set in Render

### Bot gives generic responses
- Add more documents to knowledge base
- Check if documents were ingested successfully
- Verify LLM API keys are valid

### "Knowledge base is empty" warning
- Run `python ingest_knowledge.py --dir ./knowledge_base`
- Check logs to see if documents were processed

### High API costs
- Reduce `MAX_TOKENS` in .env
- Reduce `MAX_CONVERSATION_HISTORY`
- Use GPT-3.5 instead of GPT-4: `OPENAI_MODEL=gpt-3.5-turbo`

## Cost Estimation

### Twilio WhatsApp
- Free tier: 1,000 conversations/month
- After: ~$0.005-0.04 per conversation

### OpenAI GPT-4
- ~$0.03 per 1K tokens (input)
- ~$0.06 per 1K tokens (output)
- Average conversation: $0.02-0.10

### Anthropic Claude
- Similar pricing to GPT-4
- Claude Haiku is cheaper for simple use cases

### Render Hosting
- Free tier available (with sleep after inactivity)
- Starter plan: $7/month (no sleep)

**Estimated total for small business**: $10-50/month

## Advanced Features

### Using Redis for Conversation Storage

For production with multiple servers:

```env
USE_REDIS=true
REDIS_URL=redis://your-redis-url:6379
```

### Switching LLM Providers

```env
# Use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Or use Anthropic Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

## Project Structure

```
whatschat/
├── app.py                    # Main FastAPI application
├── config.py                 # Configuration management
├── llm_service.py            # LLM integration (OpenAI/Anthropic)
├── knowledge_base.py         # Vector database (ChromaDB)
├── conversation_manager.py   # Conversation history management
├── whatsapp_handler.py       # WhatsApp message processing
├── ingest_knowledge.py       # Knowledge base ingestion script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── render.yaml              # Render deployment config
├── Procfile                 # Alternative deployment config
└── README.md                # This file
```

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Render deployment logs
3. Check Twilio webhook logs

## License

MIT License - feel free to use for your business!

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

Built with FastAPI, ChromaDB, OpenAI/Anthropic, and Twilio WhatsApp API
