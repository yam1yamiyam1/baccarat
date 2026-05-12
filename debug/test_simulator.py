import sys

# Force UTF-8 so emojis render correctly in the Windows console
sys.stdout.reconfigure(encoding="utf-8")

from simulator import BaccaratSimulator, SimulatorConfig, SimulationSummary


def _print_config_block(sim_config: SimulatorConfig) -> None:
    """Prints the simulation configuration parameters."""
    print("Config:")
    print(f"  Base Bet           : PHP {sim_config.base_bet:,.2f}")
    print(f"  Streak Trigger     : {sim_config.streak_trigger} consecutive")
    print(f"  Daily Profit Target: PHP {sim_config.daily_profit_target:,.2f}")
    print(f"  Daily Stop Loss    : PHP {sim_config.daily_stop_loss:,.2f}")
    print(f"  Days Simulated     : {sim_config.num_days}")
    print(f"  Max Shoes/Day      : {sim_config.max_shoes_per_day}")


def _print_capital_block(summary: SimulationSummary) -> None:
    """Prints starting capital, final balance, total profit, and max drawdown."""
    profit_sign = "+" if summary.total_profit >= 0 else ""
    print(f"Starting Capital   : PHP {summary.starting_capital:,.2f}")
    print(f"Final Balance      : PHP {summary.final_balance:,.2f}")
    print(f"Total Profit       : PHP {profit_sign}{summary.total_profit:,.2f}")
    print(f"Max Capital Needed : PHP {summary.max_capital_needed:,.2f}")


def _print_day_summary_block(summary: SimulationSummary) -> None:
    """Prints day-level win/loss/breakeven counts and averages."""
    avg_profit_sign = "+" if summary.avg_profit_per_day >= 0 else ""
    print(f"Total Days         : {summary.total_days}")
    print(f"Winning Days       : {summary.winning_days:<3} ✅")
    print(f"Losing Days        : {summary.losing_days:<3} ❌")
    print(f"Breakeven Days     : {summary.breakeven_days:<3} ➖")
    print(f"Avg Shoes/Day      : {summary.avg_shoes_per_day:.1f}")
    print(f"Avg Profit/Day     : PHP {avg_profit_sign}{summary.avg_profit_per_day:,.2f}")


def _print_bet_stats_block(summary: SimulationSummary, win_rate: float) -> None:
    """Prints total bets placed, wins, losses, win rate, and table limit hits."""
    print(f"Total Bets Placed  : {summary.total_bets:,}")
    print(f"Wins               : {summary.wins:,}")
    print(f"Losses             : {summary.losses:,}")
    print(f"Win Rate           : {win_rate:.1f}%")
    print(f"Table Limit Hits   : {summary.total_abandonments:,}")


def _print_day_by_day_log(summary: SimulationSummary) -> None:
    """Prints a row-per-day table showing shoes played, profit, and exit reason."""
    print("Day-by-Day Log:")
    print("Day | Shoes | Profit      | Result")
    print("----|-------|-------------|-------")

    for day in summary.day_results:
        profit_sign = "+" if day.profit >= 0 else ""
        profit_str = f"PHP {profit_sign}{day.profit:,.2f}"

        if day.hit_target:
            result_label = "✅ Target Hit"
        elif day.hit_stop_loss:
            result_label = "❌ Stop Loss"
        else:
            result_label = "➖ Max Shoes"

        print(f"{day.day_number:>3} | {day.shoes_played:>5} | {profit_str:<11} | {result_label}")


def _calculate_win_rate(summary: SimulationSummary) -> float:
    """Returns win rate as a percentage, or 0.0 if no bets were placed."""
    if summary.total_bets == 0:
        return 0.0
    return summary.wins / summary.total_bets * 100


def main() -> None:
    """Entry point. Runs the simulation and prints a full formatted report."""
    sim_config = SimulatorConfig()
    simulator = BaccaratSimulator(sim_config=sim_config)
    summary = simulator.run_simulation()
    win_rate = _calculate_win_rate(summary)

    divider = "============================================"
    separator = "--------------------------------------------"

    print(divider)
    print("         BACCARAT STRATEGY SIMULATOR")
    print(divider)
    _print_config_block(sim_config)
    print(separator)
    _print_capital_block(summary)
    print(separator)
    _print_day_summary_block(summary)
    print(separator)
    _print_bet_stats_block(summary, win_rate)
    print(divider)
    print()
    _print_day_by_day_log(summary)


if __name__ == "__main__":
    main()
