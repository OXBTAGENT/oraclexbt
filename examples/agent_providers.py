#!/usr/bin/env python3
"""
Example: Using the agent with different LLM providers.

Shows how to configure the agent for OpenAI vs Anthropic.
"""

import os
from agent import PredictionMarketAgent, AgentConfig
from agent.config import LLMProvider


def run_with_anthropic():
    """Run with Anthropic Claude."""
    print("\n🟣 Using Anthropic Claude")
    print("=" * 40)
    
    config = AgentConfig(
        llm_provider=LLMProvider.ANTHROPIC,
        llm_model="claude-sonnet-4-20250514",
        temperature=0.7,
    )
    
    with PredictionMarketAgent(config=config) as agent:
        response = agent.chat("What's the most interesting prediction market you can find?")
        print(response)


def run_with_openai():
    """Run with OpenAI GPT-4."""
    print("\n🟢 Using OpenAI GPT-4")
    print("=" * 40)
    
    config = AgentConfig(
        llm_provider=LLMProvider.OPENAI,
        llm_model="gpt-4o",
        temperature=0.7,
    )
    
    with PredictionMarketAgent(config=config) as agent:
        response = agent.chat("What's the most interesting prediction market you can find?")
        print(response)


def main():
    # Check which API keys are available
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    
    if not has_anthropic and not has_openai:
        print("Please set at least one API key:")
        print("  export ANTHROPIC_API_KEY=your-key")
        print("  export OPENAI_API_KEY=your-key")
        return
    
    if has_anthropic:
        run_with_anthropic()
    
    if has_openai:
        run_with_openai()
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
