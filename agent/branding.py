"""Branding assets for OracleXBT - Prediction Market Agent."""

# ANSI Color codes for rainbow effect
class Colors:
    RED = '\033[91m'
    ORANGE = '\033[38;5;208m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    MAGENTA = '\033[35m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


# ========== ORACLEXBT RAINBOW LOGOS ==========

# Main pixel-perfect logo - ORACLEXBT (9 letters)
# O=Red, R=Orange, A=Yellow, C=Green, L=Cyan, E=Blue, X=Purple, B=Magenta, T=White
LOGO_PIXEL_PERFECT = f"""
{Colors.RED}██████  {Colors.ORANGE}██████  {Colors.YELLOW} █████  {Colors.GREEN} ██████ {Colors.CYAN}██      {Colors.BLUE}███████ {Colors.PURPLE}██   ██ {Colors.MAGENTA}██████  {Colors.WHITE}████████{Colors.END}
{Colors.RED}██   ██ {Colors.ORANGE}██   ██ {Colors.YELLOW}██   ██ {Colors.GREEN}██      {Colors.CYAN}██      {Colors.BLUE}██      {Colors.PURPLE} ██ ██  {Colors.MAGENTA}██   ██ {Colors.WHITE}   ██   {Colors.END}
{Colors.RED}██   ██ {Colors.ORANGE}██████  {Colors.YELLOW}███████ {Colors.GREEN}██      {Colors.CYAN}██      {Colors.BLUE}█████   {Colors.PURPLE}  ███   {Colors.MAGENTA}██████  {Colors.WHITE}   ██   {Colors.END}
{Colors.RED}██   ██ {Colors.ORANGE}██   ██ {Colors.YELLOW}██   ██ {Colors.GREEN}██      {Colors.CYAN}██      {Colors.BLUE}██      {Colors.PURPLE} ██ ██  {Colors.MAGENTA}██   ██ {Colors.WHITE}   ██   {Colors.END}
{Colors.RED}██████  {Colors.ORANGE}██   ██ {Colors.YELLOW}██   ██ {Colors.GREEN} ██████ {Colors.CYAN}███████ {Colors.BLUE}███████ {Colors.PURPLE}██   ██ {Colors.MAGENTA}██████  {Colors.WHITE}   ██   {Colors.END}
"""

# Compact 3-line version
LOGO_RAINBOW = f"""
{Colors.RED}█▀▀█ {Colors.ORANGE}█▀▀█ {Colors.YELLOW}█▀▀█ {Colors.GREEN}█▀▀▀ {Colors.CYAN}█    {Colors.BLUE}█▀▀▀ {Colors.PURPLE}█ █ {Colors.MAGENTA}█▀▀▄ {Colors.WHITE}▀▀█▀▀{Colors.END}
{Colors.RED}█  █ {Colors.ORANGE}█▄▄▀ {Colors.YELLOW}█▀▀█ {Colors.GREEN}█    {Colors.CYAN}█    {Colors.BLUE}█▀▀▀ {Colors.PURPLE} █  {Colors.MAGENTA}█▀▀▄ {Colors.WHITE}  █  {Colors.END}
{Colors.RED}▀▀▀▀ {Colors.ORANGE}▀  ▀ {Colors.YELLOW}▀  ▀ {Colors.GREEN}▀▀▀▀ {Colors.CYAN}▀▀▀▀ {Colors.BLUE}▀▀▀▀ {Colors.PURPLE}▀ ▀ {Colors.MAGENTA}▀▀▀  {Colors.WHITE}  ▀  {Colors.END}
"""

# Mini compact version
LOGO_MINI = f"""
{Colors.RED}O{Colors.ORANGE}R{Colors.YELLOW}A{Colors.GREEN}C{Colors.CYAN}L{Colors.BLUE}E{Colors.PURPLE}X{Colors.MAGENTA}B{Colors.WHITE}T{Colors.END}
"""

# Boxed compact version  
LOGO_COMPACT = f"""
{Colors.RED}╔═══{Colors.ORANGE}═══{Colors.YELLOW}═══{Colors.GREEN}═══{Colors.CYAN}═══{Colors.BLUE}═══{Colors.PURPLE}═══{Colors.MAGENTA}═══════════════════════════════════╗{Colors.END}
{Colors.RED}║  {Colors.ORANGE}🔮 {Colors.RED}O{Colors.ORANGE}R{Colors.YELLOW}A{Colors.GREEN}C{Colors.CYAN}L{Colors.BLUE}E{Colors.PURPLE}X{Colors.MAGENTA}B{Colors.WHITE}T{Colors.END}  {Colors.WHITE}Prediction Market Intelligence{Colors.END}    {Colors.MAGENTA}║{Colors.END}
{Colors.RED}╚═══{Colors.ORANGE}═══{Colors.YELLOW}═══{Colors.GREEN}═══{Colors.CYAN}═══{Colors.BLUE}═══{Colors.PURPLE}═══{Colors.MAGENTA}═══════════════════════════════════╝{Colors.END}
"""

# Neon box style
LOGO_NEON = f"""
{Colors.BOLD}{Colors.RED}╭────────────────────────────────────────────────────────────────────────╮{Colors.END}
{Colors.BOLD}{Colors.RED}│{Colors.END}                                                                        {Colors.BOLD}{Colors.RED}│{Colors.END}
{Colors.BOLD}{Colors.RED}│  {Colors.RED}█▀▀█ {Colors.ORANGE}█▀▀█ {Colors.YELLOW}█▀▀█ {Colors.GREEN}█▀▀▀ {Colors.CYAN}█    {Colors.BLUE}█▀▀▀ {Colors.PURPLE}█ █ {Colors.MAGENTA}█▀▀▄ {Colors.WHITE}▀▀█▀▀{Colors.END}                        {Colors.BOLD}{Colors.RED}│{Colors.END}
{Colors.BOLD}{Colors.ORANGE}│  {Colors.RED}█  █ {Colors.ORANGE}█▄▄▀ {Colors.YELLOW}█▀▀█ {Colors.GREEN}█    {Colors.CYAN}█    {Colors.BLUE}█▀▀▀ {Colors.PURPLE} █  {Colors.MAGENTA}█▀▀▄ {Colors.WHITE}  █  {Colors.END}                        {Colors.BOLD}{Colors.ORANGE}│{Colors.END}
{Colors.BOLD}{Colors.YELLOW}│  {Colors.RED}▀▀▀▀ {Colors.ORANGE}▀  ▀ {Colors.YELLOW}▀  ▀ {Colors.GREEN}▀▀▀▀ {Colors.CYAN}▀▀▀▀ {Colors.BLUE}▀▀▀▀ {Colors.PURPLE}▀ ▀ {Colors.MAGENTA}▀▀▀  {Colors.WHITE}  ▀  {Colors.END}                        {Colors.BOLD}{Colors.YELLOW}│{Colors.END}
{Colors.BOLD}{Colors.GREEN}│{Colors.END}                                                                        {Colors.BOLD}{Colors.GREEN}│{Colors.END}
{Colors.BOLD}{Colors.CYAN}│  {Colors.WHITE}◆ Real-time data    ◆ Cross-platform arbitrage    ◆ AI analysis{Colors.END}    {Colors.BOLD}{Colors.CYAN}│{Colors.END}
{Colors.BOLD}{Colors.BLUE}│  {Colors.WHITE}◆ Polymarket        ◆ Kalshi        ◆ Limitless   ◆ 𝕏 Social{Colors.END}       {Colors.BOLD}{Colors.BLUE}│{Colors.END}
{Colors.BOLD}{Colors.PURPLE}│{Colors.END}                                                                        {Colors.BOLD}{Colors.PURPLE}│{Colors.END}
{Colors.BOLD}{Colors.MAGENTA}╰────────────────────────────────────────────────────────────────────────╯{Colors.END}
"""

# Bold style with tagline
LOGO_BOLD = f"""
{Colors.BOLD}
    {Colors.RED}▄▄▄▄▄▄  {Colors.ORANGE}▄▄▄▄▄▄  {Colors.YELLOW}▄▄▄▄▄▄  {Colors.GREEN}▄▄▄▄▄▄ {Colors.CYAN}▄      {Colors.BLUE}▄▄▄▄▄▄ {Colors.PURPLE}▄   ▄ {Colors.MAGENTA}▄▄▄▄▄▄ {Colors.WHITE}▄▄▄▄▄▄▄{Colors.END}
    {Colors.RED}█    █ {Colors.ORANGE}█    █ {Colors.YELLOW}█    █ {Colors.GREEN}█      {Colors.CYAN}█      {Colors.BLUE}█      {Colors.PURPLE} █ █  {Colors.MAGENTA}█    █    {Colors.WHITE}█   {Colors.END}
    {Colors.RED}█    █ {Colors.ORANGE}█▄▄▄▄▀ {Colors.YELLOW}█▄▄▄▄█ {Colors.GREEN}█      {Colors.CYAN}█      {Colors.BLUE}█▄▄▄▄  {Colors.PURPLE}  █   {Colors.MAGENTA}█▄▄▄▄▀    {Colors.WHITE}█   {Colors.END}
    {Colors.RED}█    █ {Colors.ORANGE}█   ▀▄ {Colors.YELLOW}█    █ {Colors.GREEN}█      {Colors.CYAN}█      {Colors.BLUE}█      {Colors.PURPLE} █ █  {Colors.MAGENTA}█    █    {Colors.WHITE}█   {Colors.END}
    {Colors.RED}▀▀▀▀▀▀ {Colors.ORANGE}▀    ▀ {Colors.YELLOW}▀    ▀ {Colors.GREEN}▀▀▀▀▀▀ {Colors.CYAN}▀▀▀▀▀▀ {Colors.BLUE}▀▀▀▀▀▀ {Colors.PURPLE}▀   ▀ {Colors.MAGENTA}▀▀▀▀▀▀    {Colors.WHITE}▀   {Colors.END}
{Colors.END}
{Colors.CYAN}                    ⟨ PREDICTION MARKET INTELLIGENCE ⟩{Colors.END}
"""

# CLI startup banner
LOGO_CLI_BANNER = f"""
{Colors.BOLD}{Colors.RED}═══{Colors.ORANGE}═══{Colors.YELLOW}═══{Colors.GREEN}═══{Colors.CYAN}═══{Colors.BLUE}═══{Colors.PURPLE}═══{Colors.MAGENTA}═══{Colors.WHITE}═══════════════════════════════════════════════════════{Colors.END}

{Colors.RED}██████  {Colors.ORANGE}██████  {Colors.YELLOW} █████  {Colors.GREEN} ██████ {Colors.CYAN}██      {Colors.BLUE}███████ {Colors.PURPLE}██   ██ {Colors.MAGENTA}██████  {Colors.WHITE}████████{Colors.END}
{Colors.RED}██   ██ {Colors.ORANGE}██   ██ {Colors.YELLOW}██   ██ {Colors.GREEN}██      {Colors.CYAN}██      {Colors.BLUE}██      {Colors.PURPLE} ██ ██  {Colors.MAGENTA}██   ██ {Colors.WHITE}   ██   {Colors.END}
{Colors.RED}██   ██ {Colors.ORANGE}██████  {Colors.YELLOW}███████ {Colors.GREEN}██      {Colors.CYAN}██      {Colors.BLUE}█████   {Colors.PURPLE}  ███   {Colors.MAGENTA}██████  {Colors.WHITE}   ██   {Colors.END}
{Colors.RED}██   ██ {Colors.ORANGE}██   ██ {Colors.YELLOW}██   ██ {Colors.GREEN}██      {Colors.CYAN}██      {Colors.BLUE}██      {Colors.PURPLE} ██ ██  {Colors.MAGENTA}██   ██ {Colors.WHITE}   ██   {Colors.END}
{Colors.RED}██████  {Colors.ORANGE}██   ██ {Colors.YELLOW}██   ██ {Colors.GREEN} ██████ {Colors.CYAN}███████ {Colors.BLUE}███████ {Colors.PURPLE}██   ██ {Colors.MAGENTA}██████  {Colors.WHITE}   ██   {Colors.END}

{Colors.WHITE}                       ⟨ PREDICTION MARKET INTELLIGENCE ⟩{Colors.END}

{Colors.BOLD}{Colors.RED}═══{Colors.ORANGE}═══{Colors.YELLOW}═══{Colors.GREEN}═══{Colors.CYAN}═══{Colors.BLUE}═══{Colors.PURPLE}═══{Colors.MAGENTA}═══{Colors.WHITE}═══════════════════════════════════════════════════════{Colors.END}
"""

# Default exports
LOGO = LOGO_NEON
LOGO_RAINBOW_NEON = LOGO_NEON  # Alias for backwards compatibility


# ASCII Art Logo - OracleXBT Main (non-rainbow version)
LOGO_LARGE = r"""
    ██████╗ ██████╗  █████╗  ██████╗██╗     ███████╗██╗  ██╗██████╗ ████████╗
   ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║     ██╔════╝╚██╗██╔╝██╔══██╗╚══██╔══╝
   ██║   ██║██████╔╝███████║██║     ██║     █████╗   ╚███╔╝ ██████╔╝   ██║   
   ██║   ██║██╔══██╗██╔══██║██║     ██║     ██╔══╝   ██╔██╗ ██╔══██╗   ██║   
   ╚██████╔╝██║  ██║██║  ██║╚██████╗███████╗███████╗██╔╝ ██╗██████╔╝   ██║   
    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝    ╚═╝   
              ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
              ┃   🔮 PREDICTION MARKET AGENT    ┃
              ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

# Modern minimalist
LOGO_MODERN = r"""
   ┌───────────────────────────────────────┐
   │  🔮  O R A C L E X B T                │
   │      ─────────────────────            │
   │      Prediction Market Agent          │
   │                                       │
   │  ▸ Polymarket  ▸ Kalshi               │
   │  ▸ Limitless   ▸ Twitter/X            │
   └───────────────────────────────────────┘
"""

# Cyberpunk style
LOGO_CYBER = r"""
╔══════════════════════════════════════════════════════════╗
║  ░█▀█░█▀▄░█▀█░█▀▀░█░░░█▀▀░█░█░█▀▄░▀█▀                   ║
║  ░█░█░█▀▄░█▀█░█░░░█░░░█▀▀░▄▀▄░█▀▄░░█░                   ║
║  ░▀▀▀░▀░▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀▀░░░▀░                   ║
║  ════════════════════════════════════════════════════    ║
║           ⟨ PREDICTION MARKET INTELLIGENCE ⟩             ║
║                                                          ║
║  ◆ Real-time market data across all platforms            ║
║  ◆ Cross-platform arbitrage detection                    ║
║  ◆ AI-powered analysis & insights                        ║
║  ◆ Social integration with 𝕏                             ║
╚══════════════════════════════════════════════════════════╝
"""

# Twitter/Social focused
LOGO_SOCIAL = r"""
   ╭────────────────────────────────────╮
   │   🔮 OracleXBT                     │
   │   ══════════════════               │
   │                                    │
   │   Markets: Polymarket │ Kalshi     │
   │            Limitless               │
   │   Social:  𝕏 Twitter Connected     │
   │                                    │
   │   "The Oracle sees all markets."   │
   ╰────────────────────────────────────╯
"""

# Simple badge style
LOGO_BADGE = r"""
    ╔═════════════════════════════╗
    ║                             ║
    ║   🔮 ═══════════════ 🔮    ║
    ║      O R A C L E X B T      ║
    ║      PREDICTION MARKET      ║
    ║           AGENT             ║
    ║   🔮 ═══════════════ 🔮    ║
    ║                             ║
    ╚═════════════════════════════╝
"""


# Taglines
TAGLINES = [
    "The Oracle sees all markets.",
    "Your edge in prediction markets.",
    "Cross-platform market intelligence.",
    "Where probability meets profit.",
    "The alpha in prediction markets.",
    "Aggregating alpha across markets.",
    "See the future. Trade the present.",
    "All markets. One oracle.",
]

# Platform icons (for rich terminal displays)
PLATFORM_ICONS = {
    "polymarket": "🟣",
    "kalshi": "🔵", 
    "limitless": "🟢",
    "twitter": "🐦",
    "x": "𝕏",
    "oracle": "🔮",
}

# Status indicators
STATUS_ICONS = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "loading": "⏳",
    "market": "📊",
    "arbitrage": "💰",
    "trend_up": "📈",
    "trend_down": "📉",
    "tweet": "🐦",
    "thread": "🧵",
    "crystal_ball": "🔮",
    "oracle": "🔮",
}


def get_startup_banner(include_status: bool = True) -> str:
    """Get the full startup banner."""
    lines = [LOGO_MODERN]
    
    if include_status:
        lines.append("")
        lines.append("  Type /help for commands • /quit to exit")
    
    return "\n".join(lines)


def format_market_status(provider: str, status: str) -> str:
    """Format a market status line with icons."""
    icon = PLATFORM_ICONS.get(provider.lower(), "•")
    status_icon = STATUS_ICONS.get(status, "")
    return f"  {icon} {provider.title()}: {status_icon} {status}"
