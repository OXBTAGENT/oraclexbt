"""Conversation memory and context management for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from collections import deque
import json


@dataclass
class Message:
    """A single message in the conversation."""
    role: str  # "user", "assistant", or "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_calls: Optional[list[dict]] = None
    tool_results: Optional[list[dict]] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for LLM API."""
        msg = {"role": self.role, "content": self.content}
        if self.tool_calls:
            msg["tool_calls"] = self.tool_calls
        return msg


@dataclass 
class MarketContext:
    """Context about a market the user has discussed."""
    market_id: str
    title: str
    last_price: Optional[float] = None
    last_accessed: datetime = field(default_factory=datetime.now)
    notes: list[str] = field(default_factory=list)


class ConversationMemory:
    """
    Manages conversation history and context for the agent.
    
    Features:
    - Rolling message history with configurable limit
    - Market context tracking (remembers markets discussed)
    - Summary generation for long conversations
    """
    
    def __init__(self, max_messages: int = 50, max_market_context: int = 20):
        self.max_messages = max_messages
        self.max_market_context = max_market_context
        
        self._messages: deque[Message] = deque(maxlen=max_messages)
        self._market_context: dict[str, MarketContext] = {}
        self._user_preferences: dict[str, Any] = {}
        self._session_start = datetime.now()
    
    def add_user_message(self, content: str) -> Message:
        """Add a user message to history."""
        msg = Message(role="user", content=content)
        self._messages.append(msg)
        return msg
    
    def add_assistant_message(
        self, 
        content: str, 
        tool_calls: Optional[list[dict]] = None
    ) -> Message:
        """Add an assistant message to history."""
        msg = Message(role="assistant", content=content, tool_calls=tool_calls)
        self._messages.append(msg)
        return msg
    
    def add_tool_result(self, tool_name: str, result: Any) -> None:
        """Record a tool result (attached to last assistant message)."""
        if self._messages and self._messages[-1].role == "assistant":
            if self._messages[-1].tool_results is None:
                self._messages[-1].tool_results = []
            self._messages[-1].tool_results.append({
                "tool": tool_name,
                "result": result
            })
    
    def track_market(self, market_id: str, title: str, price: Optional[float] = None) -> None:
        """Track a market that was discussed."""
        if market_id in self._market_context:
            ctx = self._market_context[market_id]
            ctx.last_price = price or ctx.last_price
            ctx.last_accessed = datetime.now()
        else:
            # Evict oldest if at capacity
            if len(self._market_context) >= self.max_market_context:
                oldest_id = min(
                    self._market_context.keys(),
                    key=lambda k: self._market_context[k].last_accessed
                )
                del self._market_context[oldest_id]
            
            self._market_context[market_id] = MarketContext(
                market_id=market_id,
                title=title,
                last_price=price
            )
    
    def get_market_context(self, market_id: str) -> Optional[MarketContext]:
        """Get context for a specific market."""
        return self._market_context.get(market_id)
    
    def get_recent_markets(self, limit: int = 5) -> list[MarketContext]:
        """Get recently discussed markets."""
        sorted_markets = sorted(
            self._market_context.values(),
            key=lambda m: m.last_accessed,
            reverse=True
        )
        return sorted_markets[:limit]
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference."""
        self._user_preferences[key] = value
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        return self._user_preferences.get(key, default)
    
    def get_messages_for_llm(self, include_system: bool = False) -> list[dict]:
        """Get messages formatted for LLM API."""
        messages = []
        
        for msg in self._messages:
            messages.append(msg.to_dict())
        
        return messages
    
    def get_context_summary(self) -> str:
        """Generate a summary of current context."""
        parts = []
        
        # Recent markets
        recent = self.get_recent_markets(5)
        if recent:
            parts.append("Recently discussed markets:")
            for m in recent:
                price_str = f" (Yes: {m.last_price:.1%})" if m.last_price else ""
                parts.append(f"  - {m.title}{price_str}")
        
        # User preferences
        if self._user_preferences:
            parts.append("\nUser preferences:")
            for k, v in self._user_preferences.items():
                parts.append(f"  - {k}: {v}")
        
        return "\n".join(parts) if parts else "No prior context."
    
    def clear(self) -> None:
        """Clear all memory."""
        self._messages.clear()
        self._market_context.clear()
        self._user_preferences.clear()
        self._session_start = datetime.now()
    
    @property
    def message_count(self) -> int:
        """Number of messages in history."""
        return len(self._messages)
    
    @property
    def session_duration(self) -> float:
        """Session duration in seconds."""
        return (datetime.now() - self._session_start).total_seconds()
