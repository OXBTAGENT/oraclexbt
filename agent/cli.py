#!/usr/bin/env python3
"""Interactive CLI for the Prediction Market Agent."""

from __future__ import annotations

import sys
import argparse
from typing import Optional

from agent import PredictionMarketAgent, AgentConfig
from agent.config import LLMProvider
from agent.branding import LOGO_RAINBOW_NEON, STATUS_ICONS, PLATFORM_ICONS


# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    PURPLE = '\033[35m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;208m'


BANNER = f"""
{Colors.RED}    ╭────────────────────────────────────────────────────────────────────────╮{Colors.END}
{Colors.RED}    │{Colors.END}                                                                        {Colors.RED}│{Colors.END}
{Colors.RED}    │  {Colors.RED}█▀▀█ {Colors.ORANGE}█▀▀█ {Colors.YELLOW}█▀▀█ {Colors.GREEN}█▀▀▀ {Colors.CYAN}█    {Colors.BLUE}█▀▀▀ {Colors.PURPLE}█ █ {Colors.WHITE}█▀▀▄ {Colors.RED}▀▀█▀▀{Colors.END}                        {Colors.RED}│{Colors.END}
{Colors.ORANGE}    │  {Colors.RED}█  █ {Colors.ORANGE}█▄▄▀ {Colors.YELLOW}█▀▀█ {Colors.GREEN}█    {Colors.CYAN}█    {Colors.BLUE}█▀▀▀ {Colors.PURPLE} █  {Colors.WHITE}█▀▀▄ {Colors.RED}  █  {Colors.END}                        {Colors.ORANGE}│{Colors.END}
{Colors.YELLOW}    │  {Colors.RED}▀▀▀▀ {Colors.ORANGE}▀  ▀ {Colors.YELLOW}▀  ▀ {Colors.GREEN}▀▀▀▀ {Colors.CYAN}▀▀▀▀ {Colors.BLUE}▀▀▀▀ {Colors.PURPLE}▀ ▀ {Colors.WHITE}▀▀▀  {Colors.RED}  ▀  {Colors.END}                        {Colors.YELLOW}│{Colors.END}
{Colors.GREEN}    │{Colors.END}                                                                        {Colors.GREEN}│{Colors.END}
{Colors.CYAN}    │  {Colors.WHITE}◆ Real-time data    ◆ Cross-platform arbitrage    ◆ AI analysis{Colors.END}    {Colors.CYAN}│{Colors.END}
{Colors.BLUE}    │  {Colors.WHITE}◆ Polymarket        ◆ Kalshi        ◆ Limitless   ◆ 𝕏 Social{Colors.END}       {Colors.BLUE}│{Colors.END}
{Colors.PURPLE}    │{Colors.END}                                                                        {Colors.PURPLE}│{Colors.END}
{Colors.RED}    ╰────────────────────────────────────────────────────────────────────────╯{Colors.END}
"""

HELP_TEXT = f"""
{Colors.BOLD}Commands:{Colors.END}
  /help      - Show this help message
  /clear     - Clear conversation history  
  /markets   - Show recently discussed markets
  /twitter   - Show Twitter integration status
  /logo      - Display the OracleXBT logo
  /quit      - Exit the agent

{Colors.BOLD}Example questions:{Colors.END}
  • "What are the most active political markets right now?"
  • "Find markets about Bitcoin"
  • "Analyze market pm-551963"
  • "Are there any arbitrage opportunities?"
  • "Compare prices for the same event across platforms"
  • "What markets are expiring this week?"

{Colors.BOLD}Twitter/X commands:{Colors.END}
  • "Search Twitter for discussions about Polymarket"
  • "Compose a tweet about an interesting market"
  • "What is @Polymarket tweeting about?"
  • "Post a thread about the top 3 markets"
"""


def print_colored(text: str, color: str = "") -> None:
    """Print with optional color."""
    if color:
        print(f"{color}{text}{Colors.END}")
    else:
        print(text)


def run_cli(config: Optional[AgentConfig] = None, stream: bool = True) -> None:
    """Run the interactive CLI."""
    print(BANNER)
    
    try:
        agent = PredictionMarketAgent(config=config)
    except ValueError as e:
        print_colored(f"Error initializing agent: {e}", Colors.RED)
        print_colored("\nMake sure you have set your API key:", Colors.YELLOW)
        print("  export ANTHROPIC_API_KEY=your-key-here")
        print("  # or")
        print("  export OPENAI_API_KEY=your-key-here")
        sys.exit(1)
    
    provider = config.llm_provider.value if config else "anthropic"
    model = config.llm_model if config else "claude-sonnet-4-20250514"
    print_colored(f"Using: {provider} / {model}", Colors.CYAN)
    
    # Show Twitter status
    if agent.twitter_enabled:
        print_colored("Twitter: ✅ Connected", Colors.GREEN)
    else:
        print_colored("Twitter: ⚠️  Not configured (set TWITTER_* env vars)", Colors.YELLOW)
    
    print_colored("Type /help for commands, /quit to exit\n", Colors.CYAN)
    
    try:
        while True:
            try:
                # Get user input
                user_input = input(f"{Colors.GREEN}You:{Colors.END} ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    command = user_input.lower()
                    
                    if command == "/quit" or command == "/exit":
                        print_colored("\nGoodbye! 👋", Colors.CYAN)
                        break
                    
                    elif command == "/help":
                        print(HELP_TEXT)
                        continue
                    
                    elif command == "/clear":
                        agent.reset_memory()
                        print_colored("Conversation cleared.", Colors.YELLOW)
                        continue
                    
                    elif command == "/markets":
                        recent = agent.memory.get_recent_markets()
                        if recent:
                            print_colored("\n📊 Recently discussed markets:", Colors.BOLD)
                            for m in recent:
                                price = f" ({m.last_price:.1%} Yes)" if m.last_price else ""
                                print(f"  • {m.title}{price}")
                                print(f"    ID: {m.market_id}")
                            print()
                        else:
                            print_colored("No markets discussed yet.", Colors.YELLOW)
                        continue
                    
                    elif command == "/twitter":
                        print_colored("\n𝕏 Twitter Integration Status:", Colors.BOLD)
                        if agent.twitter_enabled:
                            print_colored("  ✅ Connected and ready to post", Colors.GREEN)
                        else:
                            print_colored("  ⚠️  Not configured", Colors.YELLOW)
                            print("\n  To enable Twitter, set these environment variables:")
                            print("    export TWITTER_API_KEY=your-key")
                            print("    export TWITTER_API_SECRET=your-secret")
                            print("    export TWITTER_ACCESS_TOKEN=your-token")
                            print("    export TWITTER_ACCESS_TOKEN_SECRET=your-token-secret")
                        print()
                        continue
                    
                    elif command == "/logo":
                        from agent.branding import LOGO_PIXEL_PERFECT, LOGO_RAINBOW, Colors as BColors
                        print(f"\n{BColors.BOLD}    ═══════════════════════════════════════════════════════════════{BColors.END}")
                        print(LOGO_PIXEL_PERFECT)
                        print(f"{BColors.WHITE}                    ⟨ PREDICTION MARKET INTELLIGENCE ⟩{BColors.END}")
                        print(f"{BColors.BOLD}    ═══════════════════════════════════════════════════════════════{BColors.END}\n")
                        continue
                    
                    else:
                        print_colored(f"Unknown command: {command}", Colors.RED)
                        print("Type /help for available commands.")
                        continue
                
                # Get agent response
                print(f"\n{Colors.PURPLE}🔮 OracleXBT:{Colors.END} ", end="", flush=True)
                
                if stream:
                    for chunk in agent.chat_stream(user_input):
                        print(chunk, end="", flush=True)
                    print("\n")
                else:
                    response = agent.chat(user_input)
                    print(f"{response}\n")
                    
            except KeyboardInterrupt:
                print("\n")
                continue
                
    except KeyboardInterrupt:
        print_colored("\n\nGoodbye! 👋", Colors.CYAN)
    finally:
        agent.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive Prediction Market Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m agent.cli                          # Use default (Anthropic)
  python -m agent.cli --provider openai        # Use OpenAI
  python -m agent.cli --model gpt-4o          # Specific model
  python -m agent.cli --no-stream              # Disable streaming
        """
    )
    
    parser.add_argument(
        "--provider", "-p",
        choices=["anthropic", "openai"],
        default="anthropic",
        help="LLM provider to use (default: anthropic)"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="Model name (default: claude-sonnet-4-20250514 for Anthropic, gpt-4o for OpenAI)"
    )
    
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming responses"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Build config
    provider = LLMProvider(args.provider)
    model = args.model
    if model is None:
        model = "claude-sonnet-4-20250514" if provider == LLMProvider.ANTHROPIC else "gpt-4o"
    
    try:
        config = AgentConfig(
            llm_provider=provider,
            llm_model=model,
            verbose=args.verbose
        )
    except ValueError as e:
        print_colored(f"Configuration error: {e}", Colors.RED)
        sys.exit(1)
    
    run_cli(config=config, stream=not args.no_stream)


if __name__ == "__main__":
    main()
