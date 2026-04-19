import os
import sys
import requests
from dotenv import load_dotenv

# Try importing rich
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.layout import Layout
    from rich.text import Text
    from rich.align import Align
    from rich import box
except ImportError:
    print("Error: The 'rich' library is not installed. Run 'uv pip install rich python-dotenv'")
    sys.exit(1)

# Initialize console
console = Console()

# Cost constant
# OpenRouter Gemini 2.0 Flash is roughly $0.075 / 1 Million Tokens (Input/Output blended roughly)
COST_PER_MILLION_TOKENS = 0.075

def main():
    with console.status("[bold green]Querying OpenRouter Financial Endpoints...[/bold green]", spinner="dots"):
        # Load environment directly
        env_path = os.path.join(os.path.dirname(__file__), "hermes-agent", ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            load_dotenv()
            
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            api_key = "REDACTED_USE_ENV_VAR" # Fallback mapped specifically for user

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Query APIs
        try:
            credits_res = requests.get("https://openrouter.ai/api/v1/credits", headers=headers).json()
            key_res = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers).json()
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]Connection Error:[/bold red] {str(e)}")
            sys.exit(1)

    # Process Data
    c_data = credits_res.get("data", {})
    k_data = key_res.get("data", {})

    total_credits = c_data.get("total_credits", 0.0)
    total_usage = c_data.get("total_usage", 0.0)
    remaining_balance = total_credits - total_usage

    usage_daily = k_data.get("usage_daily", 0.0)
    usage_weekly = k_data.get("usage_weekly", 0.0)
    usage_monthly = k_data.get("usage_monthly", 0.0)

    # Calculate Runway Based on Gemini 2.0 Flash
    purchasable_millions = remaining_balance / COST_PER_MILLION_TOKENS if remaining_balance > 0 else 0
    total_runway_tokens = purchasable_millions * 1_000_000

    # Build the Layout Arrays
    
    # 1. Financial Ledger
    ledger_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    ledger_table.add_column("Metric", style="cyan", justify="right")
    ledger_table.add_column("Value", style="bold white")
    
    ledger_table.add_row("Gross Deposit:", f"[green]${total_credits:,.2f}[/green]")
    ledger_table.add_row("Total Spend:", f"[red]-${total_usage:,.4f}[/red]")
    ledger_table.add_row("Available Balance:", f"[bold green]${remaining_balance:,.3f}[/bold green]")

    # 2. Burn Rates
    burn_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    burn_table.add_column("Timeframe", style="magenta", justify="right")
    burn_table.add_column("Burn", style="bold white")
    
    burn_table.add_row("Today:", f"${usage_daily:,.5f}")
    burn_table.add_row("This Week:", f"${usage_weekly:,.5f}")
    burn_table.add_row("This Month:", f"${usage_monthly:,.5f}")

    # 3. Runway Math
    runway_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    runway_table.add_column("Stat", style="yellow", justify="right")
    runway_table.add_column("Projection", style="bold white")
    
    runway_table.add_row("Model Mapping:", "Gemini 2.0 Flash (~$0.075 / 1M)")
    runway_table.add_row("Purchasing Power:", f"[bold cyan]{purchasable_millions:,.2f} Million Tokens[/bold cyan]")
    runway_table.add_row("Absolute Runway:", f"{total_runway_tokens:,.0f} Total Tokens")

    # Final Render
    console.print("\n")
    console.print(Align.center(Text("⚕ INTERSTELLAR TOKEN MONITOR ⚕", style="bold reverse cyan", justify="center")))
    console.print(Align.center(Text("powered by OpenRouter", style="dim italic")))
    console.print("\n")

    console.print(Panel(ledger_table, title="[bold]Ledger[/bold]", border_style="green", padding=(1, 5), expand=False))
    console.print()
    console.print(Panel(burn_table, title="[bold]Key Burn Rate[/bold]", border_style="magenta", padding=(1, 5), expand=False))
    console.print()
    console.print(Panel(runway_table, title="[bold]Dynamic Runway[/bold]", border_style="yellow", padding=(1, 5), expand=False))
    console.print("\n")

if __name__ == "__main__":
    main()
