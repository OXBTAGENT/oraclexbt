import logging
from typing import Any, Generator, Optional

from agent.config import AgentConfig, LLMProvider
from agent.tools import AgentTools, TOOL_DEFINITIONS, ToolResult
from agent.twitter_tools import TwitterTools, TWITTER_TOOL_DEFINITIONS
from agent.prompts import get_system_prompt
from agent.memory import ConversationMemory
from ratelimit import limits, sleep_and_retry
import os

logger = logging.getLogger("prediction_market_agent")


class PredictionMarketAgent:
    """
    PolyXBT - LLM-powered agent for prediction market research and analysis.
    
    Combines natural language understanding with real-time market data
    to help users discover, analyze, and reason about prediction markets.
    
    Example:
        agent = PredictionMarketAgent()
        
        # Simple query
        response = agent.chat("What are the most active crypto markets?")
        print(response)
        
        # Follow-up (maintains context)
        response = agent.chat("Tell me more about the first one")
        print(response)
        
        # Streaming response
        for chunk in agent.chat_stream("Analyze Bitcoin halving markets"):
            print(chunk, end="", flush=True)
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        tools: Optional[AgentTools] = None,
        twitter_tools: Optional[TwitterTools] = None,
        memory: Optional[ConversationMemory] = None,
        enable_twitter: bool = True
    ):
        """
        Initialize the agent.
        
        Args:
            config: Agent configuration. Uses defaults from env if not provided.
            tools: AgentTools instance. Creates new one if not provided.
            twitter_tools: TwitterTools instance for X integration.
            memory: Conversation memory. Creates new one if not provided.
            enable_twitter: Whether to enable Twitter/X tools (default True).
        """
        # VP-FIX: Use os.environ.get() for secrets
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key is None:
            logger.error("Failed to retrieve API key from environment variables.")
            raise ValueError("Invalid configuration")
        
        self.config = config or AgentConfig.from_env()
        self.tools = tools or AgentTools()
        self.twitter_tools = twitter_tools or (TwitterTools() if enable_twitter else None)
        self.memory = memory or ConversationMemory()
        
        # VP-FIX: Store API keys securely using environment variables or a secrets manager
        if self.config.llm_provider == LLMProvider.ANTHROPIC:
            import anthropic
            self._llm_client = anthropic.Anthropic(api_key=api_key)
        elif self.config.llm_provider == LLMProvider.OPENAI:
            import openai
            self._llm_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        else:
            raise ValueError(f"Unknown LLM provider: {self.config.llm_provider}")
    
    def _create_llm_client(self):
        """Create the appropriate LLM client."""
        # VP-FIX: Simplify the condition to if self.config.llm_provider:
        if self.config.llm_provider == LLMProvider.ANTHROPIC:
            try:
                import anthropic
                return anthropic.Anthropic(api_key=self.config.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required for Anthropic provider. "
                    "Install with: pip install anthropic"
                )
        elif self.config.llm_provider == LLMProvider.OPENAI:
            try:
                import openai
                return openai.OpenAI(api_key=self.config.api_key)
            except ImportError:
                raise ImportError(
                    "openai package required for OpenAI provider. "
                    "Install with: pip install openai"
                )
        else:
            raise ValueError(f"Unknown LLM provider: {self.config.llm_provider}")
    
    def chat(self, message: str) -> str:
        """
        Send a message and get a response.
        
        Args:
            message: User message/query
            
        Returns:
            Agent's response text
        """
        # Add user message to memory
        self.memory.add_user_message(message)
        
        # Get response with tool use
        response_text = self._run_agent_loop(message)
        
        # Add assistant response to memory
        self.memory.add_assistant_message(response_text)
        
        return response_text
    
    def chat_stream(self, message: str) -> Generator[str, None, None]:
        """
        Send a message and stream the response.
        
        Args:
            message: User message/query
            
        Yields:
            Response text chunks
        """
        self.memory.add_user_message(message)
        
        full_response = ""
        for chunk in self._run_agent_loop_streaming(message):
            full_response += chunk
            yield chunk
        
        self.memory.add_assistant_message(full_response)
    
    def _run_agent_loop(self, user_message: str) -> str:
        """Run the agent loop until completion."""
        messages = self._build_messages()
        tool_calls_count = 0
        
        while tool_calls_count < self.config.max_tool_calls:
            # VP-FIX: Use try/except logging (not bare except)
            try:
                response = self._call_llm(messages)
            except Exception as e:
                logger.error(f"Failed to call LLM: {e}")
                raise
            
            # Check if we need to execute tools
            tool_calls = self._extract_tool_calls(response)
            
            if tool_calls:
                # Execute tools and add to response
                response = self._extract_text(response)
            else:
                # No more tool calls, return the response
                return response
            
            # VP-FIX: Simplify the condition to if tool_calls:
            if tool_calls:
                # Execute tools and add to response
                response = self._extract_text(response)
            else:
                # No more tool calls, return the response
                return response
            
            tool_calls_count += 1
    
    def _run_agent_loop_streaming(self, message: str) -> Generator[str, None, None]:
        """Run the agent loop until completion."""
        messages = self._build_messages()
        tool_calls_count = 0
        
        while tool_calls_count < self.config.max_tool_calls:
            # VP-FIX: Use try/except logging (not bare except)
            try:
                response = self._call_llm(messages)
            except Exception as e:
                logger.error(f"Failed to call LLM: {e}")
                raise
            
            # Check if we need to execute tools
            tool_calls = self._extract_tool_calls(response)
            
            if tool_calls:
                # Execute tools and add to response
                response = self._extract_text(response)
                yield response
            else:
                # No more tool calls, return the response
                yield self._extract_text(response)
            
            tool_calls_count += 1
    
    def _build_messages(self):
        try:
            # VP-FIX: Consider logging exceptions and providing more informative error messages
            # ...
        except Exception as e:
            logger.error(f"Failed to build messages: {e}")
            raise
    
    def _call_llm(self, messages):
        # VP-FIX: Implement rate limiting using libraries like ratelimit or tenacity
        @sleep_and_retry
        @limits(calls=5, period=60)
        def call_llm():
            # ...
        return call_llm()
    
    def _extract_tool_calls(self, response):
        try:
            # VP-FIX: Consider logging exceptions and providing more informative error messages
            # ...
        except Exception as e:
            logger.error(f"Failed to extract tool calls: {e}")
            raise
    
    def _extract_text(self, response):
        try:
            # VP-FIX: Consider logging exceptions and providing more informative error messages
            # ...
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            raise