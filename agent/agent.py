"""Main agent orchestrator for PolyXBT - Prediction Market Agent."""

from __future__ import annotations

import json
import logging
from typing import Any, Generator, Optional

from agent.config import AgentConfig, LLMProvider
from agent.tools import AgentTools, TOOL_DEFINITIONS, ToolResult
from agent.twitter_tools import TwitterTools, TWITTER_TOOL_DEFINITIONS
from agent.prompts import get_system_prompt
from agent.memory import ConversationMemory

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
        self.config = config or AgentConfig.from_env()
        self.tools = tools or AgentTools()
        self.twitter_tools = twitter_tools or (TwitterTools() if enable_twitter else None)
        self.memory = memory or ConversationMemory()
        
        self._llm_client = self._create_llm_client()
    
    def _create_llm_client(self):
        """Create the appropriate LLM client."""
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
            response = self._call_llm(messages)
            
            # Check if we need to execute tools
            tool_calls = self._extract_tool_calls(response)
            
            if not tool_calls:
                # No more tool calls, return the response
                return self._extract_text(response)
            
            # Execute tools and add results to messages
            messages.append(self._response_to_message(response))
            
            for tool_call in tool_calls:
                result = self._execute_tool(
                    tool_call["name"],
                    tool_call["arguments"]
                )
                messages.append(self._tool_result_message(tool_call, result))
                tool_calls_count += 1
                
                if self.config.verbose:
                    logger.info(f"Tool {tool_call['name']}: {result.success}")
        
        # Max tool calls reached, get final response
        response = self._call_llm(messages)
        return self._extract_text(response)
    
    def _run_agent_loop_streaming(self, user_message: str) -> Generator[str, None, None]:
        """Run agent loop with streaming output."""
        messages = self._build_messages()
        tool_calls_count = 0
        
        while tool_calls_count < self.config.max_tool_calls:
            # First check if we need tools (non-streaming)
            response = self._call_llm(messages)
            tool_calls = self._extract_tool_calls(response)
            
            if not tool_calls:
                # Stream the final response
                for chunk in self._stream_llm(messages):
                    yield chunk
                return
            
            # Execute tools
            messages.append(self._response_to_message(response))
            
            for tool_call in tool_calls:
                yield f"\n🔧 Using {tool_call['name']}...\n"
                
                result = self._execute_tool(
                    tool_call["name"],
                    tool_call["arguments"]
                )
                messages.append(self._tool_result_message(tool_call, result))
                tool_calls_count += 1
        
        # Final response
        for chunk in self._stream_llm(messages):
            yield chunk
    
    def _build_messages(self) -> list[dict]:
        """Build messages list for LLM."""
        messages = [{"role": "system", "content": get_system_prompt()}]
        
        # Add conversation history
        messages.extend(self.memory.get_messages_for_llm())
        
        return messages
    
    def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        """Execute a tool by name, routing to appropriate handler."""
        # Check if it's a Twitter tool
        twitter_tools = {
            "post_tweet", "post_thread", "reply_to_tweet", "quote_tweet",
            "search_prediction_market_tweets", "get_platform_tweets",
            "get_tweet_details", "get_mentions", "compose_market_tweet",
            "compose_arbitrage_tweet", "like_tweet", "retweet"
        }
        
        # Check if it's a trading tool
        trading_tools = {
            "execute_arbitrage_trade", "place_trade", "get_portfolio_status",
            "close_position", "check_risk_limits"
        }
        
        if tool_name in twitter_tools:
            if self.twitter_tools is None:
                return ToolResult(
                    success=False,
                    data=None,
                    error="Twitter tools not enabled"
                )
            result = self.twitter_tools.execute(tool_name, arguments)
            return ToolResult(
                success=result.get("success", True),
                data=result.get("data", result),
                error=result.get("error")
            )
        
        if tool_name in trading_tools:
            # Import trading functions dynamically
            try:
                from agent.trading_tools import (
                    execute_arbitrage_trade,
                    place_trade,
                    get_portfolio_status,
                    close_position,
                    check_risk_limits
                )
                
                tool_map = {
                    "execute_arbitrage_trade": execute_arbitrage_trade,
                    "place_trade": place_trade,
                    "get_portfolio_status": get_portfolio_status,
                    "close_position": close_position,
                    "check_risk_limits": check_risk_limits
                }
                
                result = tool_map[tool_name](**arguments)
                return ToolResult(
                    success=result.get("success", True),
                    data=result,
                    error=result.get("error")
                )
            except ImportError:
                return ToolResult(
                    success=False,
                    data=None,
                    error="Trading tools not available. Install: pip install web3 eth-account"
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Trading tool error: {str(e)}"
                )
        
        # Otherwise use market tools
        return self.tools.execute(tool_name, arguments)
    
    def _get_all_tool_definitions(self) -> list[dict]:
        """Get all available tool definitions."""
        tools = TOOL_DEFINITIONS.copy()
        
        # Add Twitter tools if enabled
        if self.twitter_tools is not None:
            tools.extend(TWITTER_TOOL_DEFINITIONS)
        
        return tools
    
    def _call_llm(self, messages: list[dict]) -> Any:
        """Call the LLM and return the response."""
        if self.config.llm_provider == LLMProvider.ANTHROPIC:
            return self._call_anthropic(messages)
        else:
            return self._call_openai(messages)
    
    def _call_anthropic(self, messages: list[dict]) -> Any:
        """Call Anthropic API."""
        # Separate system message
        system = None
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)
        
        return self._llm_client.messages.create(
            model=self.config.llm_model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=system,
            messages=chat_messages,
            tools=self._get_anthropic_tools()
        )
    
    def _call_openai(self, messages: list[dict]) -> Any:
        """Call OpenAI API."""
        return self._llm_client.chat.completions.create(
            model=self.config.llm_model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=messages,
            tools=self._get_openai_tools()
        )
    
    def _stream_llm(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response from LLM."""
        if self.config.llm_provider == LLMProvider.ANTHROPIC:
            yield from self._stream_anthropic(messages)
        else:
            yield from self._stream_openai(messages)
    
    def _stream_anthropic(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream from Anthropic."""
        system = None
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)
        
        with self._llm_client.messages.stream(
            model=self.config.llm_model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=system,
            messages=chat_messages,
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def _stream_openai(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream from OpenAI."""
        stream = self._llm_client.chat.completions.create(
            model=self.config.llm_model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=messages,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _extract_tool_calls(self, response: Any) -> list[dict]:
        """Extract tool calls from LLM response."""
        tool_calls = []
        
        if self.config.llm_provider == LLMProvider.ANTHROPIC:
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "arguments": block.input
                    })
        else:  # OpenAI
            if response.choices[0].message.tool_calls:
                for tc in response.choices[0].message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    })
        
        return tool_calls
    
    def _extract_text(self, response: Any) -> str:
        """Extract text content from LLM response."""
        if self.config.llm_provider == LLMProvider.ANTHROPIC:
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""
        else:  # OpenAI
            return response.choices[0].message.content or ""
    
    def _response_to_message(self, response: Any) -> dict:
        """Convert LLM response to message dict."""
        if self.config.llm_provider == LLMProvider.ANTHROPIC:
            return {"role": "assistant", "content": response.content}
        else:
            return {"role": "assistant", "content": None, "tool_calls": response.choices[0].message.tool_calls}
    
    def _tool_result_message(self, tool_call: dict, result: ToolResult) -> dict:
        """Create tool result message."""
        if self.config.llm_provider == LLMProvider.ANTHROPIC:
            return {
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_call["id"],
                    "content": result.to_message()
                }]
            }
        else:  # OpenAI
            return {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result.to_message()
            }
    
    def _get_anthropic_tools(self) -> list[dict]:
        """Convert tool definitions to Anthropic format."""
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["parameters"]
            }
            for t in self._get_all_tool_definitions()
        ]
    
    def _get_openai_tools(self) -> list[dict]:
        """Convert tool definitions to OpenAI format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"]
                }
            }
            for t in self._get_all_tool_definitions()
        ]
    
    @property
    def twitter_enabled(self) -> bool:
        """Check if Twitter is enabled and configured."""
        return self.twitter_tools is not None and self.twitter_tools.is_available
    
    def reset_memory(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()
    
    def close(self) -> None:
        """Clean up resources."""
        self.tools.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
