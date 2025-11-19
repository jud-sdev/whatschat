"""
Conversation Manager - Handles conversation history and context
"""
from typing import List, Dict, Optional
from collections import defaultdict
import logging
from config import settings

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation history for each user"""

    def __init__(self):
        # In-memory storage: {phone_number: [{"role": "user|assistant", "content": "..."}]}
        self.conversations: Dict[str, List[Dict[str, str]]] = defaultdict(list)

        # If Redis is enabled, we could use it for persistence
        if settings.USE_REDIS:
            try:
                import redis
                self.redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("Connected to Redis for conversation storage")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using in-memory storage.")
                self.redis_client = None
        else:
            self.redis_client = None

    def add_message(self, phone_number: str, role: str, content: str):
        """
        Add a message to the conversation history

        Args:
            phone_number: User's phone number
            role: Either "user" or "assistant"
            content: Message content
        """
        message = {"role": role, "content": content}

        if self.redis_client:
            # Store in Redis (implement serialization)
            self._add_to_redis(phone_number, message)
        else:
            # Store in memory
            self.conversations[phone_number].append(message)

            # Keep only the last N messages to prevent context overflow
            if len(self.conversations[phone_number]) > settings.MAX_CONVERSATION_HISTORY * 2:
                self.conversations[phone_number] = self.conversations[phone_number][-(settings.MAX_CONVERSATION_HISTORY * 2):]

        logger.debug(f"Added {role} message for {phone_number}")

    def get_history(self, phone_number: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation history for a user

        Args:
            phone_number: User's phone number
            limit: Maximum number of messages to return (None = all)

        Returns:
            List of messages in format [{"role": "user|assistant", "content": "..."}]
        """
        if self.redis_client:
            history = self._get_from_redis(phone_number)
        else:
            history = self.conversations.get(phone_number, [])

        if limit:
            return history[-limit:]

        return history

    def clear_history(self, phone_number: str):
        """
        Clear conversation history for a user

        Args:
            phone_number: User's phone number
        """
        if self.redis_client:
            self._clear_from_redis(phone_number)
        else:
            if phone_number in self.conversations:
                del self.conversations[phone_number]

        logger.info(f"Cleared conversation history for {phone_number}")

    def _add_to_redis(self, phone_number: str, message: Dict[str, str]):
        """Add message to Redis (implement if using Redis)"""
        import json

        key = f"conversation:{phone_number}"
        self.redis_client.rpush(key, json.dumps(message))

        # Set expiration (e.g., 24 hours)
        self.redis_client.expire(key, 86400)

    def _get_from_redis(self, phone_number: str) -> List[Dict[str, str]]:
        """Get conversation from Redis (implement if using Redis)"""
        import json

        key = f"conversation:{phone_number}"
        messages = self.redis_client.lrange(key, 0, -1)

        return [json.loads(msg) for msg in messages]

    def _clear_from_redis(self, phone_number: str):
        """Clear conversation from Redis"""
        key = f"conversation:{phone_number}"
        self.redis_client.delete(key)


# Global conversation manager instance
conversation_manager = ConversationManager()
