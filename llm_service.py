"""
LLM Service - Handles interactions with OpenAI and Anthropic
"""
from typing import List, Dict
from config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating responses using LLMs"""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER

        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: str = ""
    ) -> str:
        """
        Generate a response based on user message, conversation history, and knowledge base context

        Args:
            user_message: The current user message
            conversation_history: List of previous messages [{"role": "user|assistant", "content": "..."}]
            context: Relevant context from knowledge base

        Returns:
            Generated response string
        """
        try:
            if self.provider == "openai":
                return self._generate_openai(user_message, conversation_history, context)
            elif self.provider == "anthropic":
                return self._generate_anthropic(user_message, conversation_history, context)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble processing your message right now. Please try again later."

    def _generate_openai(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: str
    ) -> str:
        """Generate response using OpenAI"""

        # Build system prompt with context
        system_prompt = self._build_system_prompt(context)

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Generate response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE
        )

        return response.choices[0].message.content

    def _generate_anthropic(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: str
    ) -> str:
        """Generate response using Anthropic Claude"""

        # Build system prompt with context
        system_prompt = self._build_system_prompt(context)

        # Build messages array (Claude doesn't use system role in messages)
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": user_message})

        # Generate response
        response = self.client.messages.create(
            model=self.model,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    def _build_system_prompt(self, context: str) -> str:
        """Build system prompt with knowledge base context"""

        base_prompt = """You are a helpful AI assistant for a business. Your role is to answer customer questions accurately and professionally based on the provided knowledge base.

Guidelines:
- Be friendly, professional, and concise
- Use the knowledge base context to answer questions accurately
- If you don't know something or it's not in the knowledge base, admit it politely
- Stay on topic and relevant to the business
- Keep responses brief and to the point (WhatsApp messages should be concise)
- If a customer needs human assistance, politely suggest they wait for a human representative
"""

        if context:
            base_prompt += f"\n\nKnowledge Base Context:\n{context}"

        return base_prompt


# Global LLM service instance
llm_service = LLMService()
