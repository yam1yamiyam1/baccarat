import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import config


# ---------------------------------------------------------------------------
# Config & Enums
# ---------------------------------------------------------------------------

@dataclass
class SimulatorConfig:
    """Holds all tunable parameters for the simulation. Sourced from config.py."""

    starting_capital: float = config.SIM_STARTING_CAPITAL
    base_bet: float = config.SIM_BASE_BET
    daily_profit_target: float = config.SIM_DAILY_PROFIT_TARGET
    daily_stop_loss: float = config.SIM_DAILY_STOP_LOSS
    num_days: int = config.SIM_NUM_DAYS
    max_shoes_per_day: int = config.SIM_MAX_SHOES_PER_DAY
    streak_trigger: int = config.SIM_STREAK_TRIGGER
    banker_weight: float = config.SIM_BANKER_WEIGHT
    player_weight: float = config.SIM_PLAYER_WEIGHT
    tie_weight: float = config.SIM_TIE_WEIGHT
    max_bet_limit: float = config.SIM_MAX_BET_LIMIT


class HandResult(Enum):
    """Possible outcomes of a single baccarat hand."""

    BANKER = "BANKER"
    PLAYER = "PLAYER"
    TIE = "TIE"


# ---------------------------------------------------------------------------
# Typed data transfer objects (no plain dicts or raw tuples)
# ---------------------------------------------------------------------------

@dataclass
class GeneratedShoe:
    """A sequence of hand results representing one shoe. Output of ShoeGenerator."""

    hands: list[HandResult]


@dataclass
class BetOutcome:
    """Result of processing a single hand through the strategy engine."""

    bet_amount: float = 0.0
    won: bool = False
    profit: float = 0.0
    abandoned: bool = False


@dataclass
class ShoeStats:
    """Aggregated statistics produced after running one full shoe."""

    net_profit: float
    closing_balance: float
    total_bets: int
    wins: int
    losses: int
    abandonments: int


@dataclass
class DayStats:
    """Aggregated statistics produced after running one full day."""

    total_bets: int
    wins: int
    losses: int
    abandonments: int
    max_drawdown: float


@dataclass
class DayResult:
    """High-level outcome record for a single simulated day."""

    day_number: int
    shoes_played: int
    profit: float
    hit_target: bool
    hit_stop_loss: bool


@dataclass
class SimulationSummary:
    """Complete summary returned after all days of simulation have run."""

    config: SimulatorConfig
    starting_capital: float
    final_balance: float
    total_profit: float
    total_bets: int
    wins: int
    losses: int
    total_abandonments: int
    day_results: list[DayResult]
    winning_days: int
    losing_days: int
    breakeven_days: int
    avg_shoes_per_day: float
    avg_profit_per_day: float
    total_days: int
    max_capital_needed: float


# ---------------------------------------------------------------------------
# Shoe Generator
# ---------------------------------------------------------------------------

class ShoeGenerator:
    """Generates a random shoe of baccarat hands using weighted probabilities."""

    def __init__(self, sim_config: SimulatorConfig) -> None:
        """Takes a SimulatorConfig to read outcome weights from."""
        self.sim_config = sim_config

    def generate(self) -> GeneratedShoe:
        """Returns a GeneratedShoe with 80 randomly weighted HandResult values."""
        outcome_choices = [HandResult.BANKER, HandResult.PLAYER, HandResult.TIE]
        outcome_weights = [
            self.sim_config.banker_weight,
            self.sim_config.player_weight,
            self.sim_config.tie_weight,
        ]
        hands = random.choices(outcome_choices, weights=outcome_weights, k=80)
        return GeneratedShoe(hands=hands)


# ---------------------------------------------------------------------------
# Strategy Engine
# ---------------------------------------------------------------------------

class StrategyEngine:
    """
    Stateful engine that tracks streaks and manages a contrarian Martingale sequence.

    Persists across shoes within a day so streak state is not lost at shoe boundaries.
    """

    def __init__(self, sim_config: SimulatorConfig) -> None:
        """Takes a SimulatorConfig; initialises all betting and streak state."""
        self.sim_config = sim_config
        self.balance: float = 0.0

        # Streak tracking
        self.current_streak_length: int = 0
        self.current_streak_type: Optional[HandResult] = None
        self.streak_already_triggered: bool = False

        # Betting sequence state
        self.betting_is_active: bool = False
        self.current_bet_side: Optional[str] = None
        self.current_bet_amount: float = self.sim_config.base_bet

    def get_suggestion(self) -> str:
        """
        Returns the bet side to play ('BANKER', 'PLAYER') or 'WAIT'.

        Triggers a bet once a qualifying streak is detected; stays on the same
        side until the sequence is won, abandoned, or reset by a new streak.
        """
        if self.betting_is_active and self.current_bet_side:
            return self.current_bet_side

        streak_is_long_enough = self.current_streak_length >= self.sim_config.streak_trigger
        streak_is_valid = self.current_streak_type is not None

        if not self.streak_already_triggered and streak_is_long_enough and streak_is_valid:
            self._activate_contrarian_bet()
            return self.current_bet_side  # type: ignore[return-value]

        return "WAIT"

    def process_hand(self, hand_result: HandResult, bet_suggestion: str) -> BetOutcome:
        """
        Resolves a hand against the active bet suggestion and updates balance.

        Streak update is deferred until after bet resolution so that a streak-
        ending hand does not cancel the bet that was already in flight for
        that same hand.
        """
        outcome = BetOutcome()

        if bet_suggestion == "WAIT":
            # No bet placed — update streak and move on
            self._update_streak(hand_result)
            return outcome

        # Check table limit before committing the bet
        if self.current_bet_amount > self.sim_config.max_bet_limit:
            self._reset_betting_sequence()
            outcome.abandoned = True
            # Still update streak so observation continues correctly
            self._update_streak(hand_result)
            return outcome

        outcome.bet_amount = self.current_bet_amount

        if hand_result == HandResult.TIE:
            # Ties are a push — no money changes hands, sequence continues
            self._update_streak(hand_result)
            return outcome

        bet_won = self._resolve_bet(bet_suggestion, hand_result)

        if bet_won:
            self.balance += self.current_bet_amount
            outcome.won = True
            outcome.profit = self.current_bet_amount
            self._reset_betting_sequence()
        else:
            self.balance -= self.current_bet_amount
            outcome.profit = -self.current_bet_amount
            # Double the stake for next hand (Martingale)
            self.current_bet_amount *= 2

        # Streak is updated AFTER bet resolution so the losing hand that ends
        # a streak cannot retroactively cancel the bet already placed on it
        self._update_streak(hand_result)
        return outcome

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _activate_contrarian_bet(self) -> None:
        """Sets the bet side to the opposite of the current streak type."""
        self.streak_already_triggered = True
        self.betting_is_active = True

        if self.current_streak_type == HandResult.BANKER:
            self.current_bet_side = "PLAYER"
        else:
            self.current_bet_side = "BANKER"

    def _resolve_bet(self, bet_suggestion: str, hand_result: HandResult) -> bool:
        """Returns True if bet_suggestion matches the hand_result outcome."""
        banker_win = bet_suggestion == "BANKER" and hand_result == HandResult.BANKER
        player_win = bet_suggestion == "PLAYER" and hand_result == HandResult.PLAYER
        return banker_win or player_win

    def _update_streak(self, hand_result: HandResult) -> None:
        """
        Maintains the current streak counter.

        Ties are ignored. A streak-break only resets the betting sequence if
        no active bet is in flight (i.e. we are in the WAIT phase between
        sequences). During an active Martingale sequence the betting engine
        itself controls resets via _reset_betting_sequence.
        """
        if hand_result == HandResult.TIE:
            return

        streak_continues = hand_result == self.current_streak_type

        if streak_continues:
            self.current_streak_length += 1
        else:
            self.current_streak_type = hand_result
            self.current_streak_length = 1
            self.streak_already_triggered = False

            # Only reset the betting sequence when we are NOT actively
            # mid-Martingale. If a bet is in flight, the sequence manages
            # its own lifecycle and must not be interrupted here.
            if not self.betting_is_active:
                self._reset_betting_sequence()

    def _reset_betting_sequence(self) -> None:
        """Clears all active betting state and reverts bet amount to base."""
        self.betting_is_active = False
        self.current_bet_side = None
        self.current_bet_amount = self.sim_config.base_bet


# ---------------------------------------------------------------------------
# Baccarat Simulator
# ---------------------------------------------------------------------------

class BaccaratSimulator:
    """Orchestrates the full multi-day simulation using ShoeGenerator and StrategyEngine."""

    def __init__(self, sim_config: SimulatorConfig) -> None:
        """Takes a SimulatorConfig and wires up a ShoeGenerator."""
        self.sim_config = sim_config
        self.shoe_generator = ShoeGenerator(sim_config)

    def run_simulation(self) -> SimulationSummary:
        """Runs all days and returns a complete SimulationSummary."""
        day_results: list[DayResult] = []
        current_capital = self.sim_config.starting_capital
        total_bets, total_wins, total_losses, total_abandonments = 0, 0, 0, 0
        peak_drawdown = 0.0

        for day_number in range(1, self.sim_config.num_days + 1):
            day_result, day_stats = self._run_day(day_number, current_capital)

            day_results.append(day_result)
            current_capital += day_result.profit

            total_bets += day_stats.total_bets
            total_wins += day_stats.wins
            total_losses += day_stats.losses
            total_abandonments += day_stats.abandonments
            peak_drawdown = max(peak_drawdown, day_stats.max_drawdown)

        total_profit = current_capital - self.sim_config.starting_capital
        return self._compile_summary(
            day_results, total_profit, total_bets,
            total_wins, total_losses, total_abandonments, peak_drawdown,
        )

    def _run_day(self, day_number: int, starting_capital: float) -> tuple[DayResult, DayStats]:
        """
        Runs one full day, playing up to max_shoes_per_day shoes.

        Stops early if the daily profit target or stop-loss is reached.
        A single StrategyEngine instance is shared across all shoes in the day
        so that streak state is preserved between shoe boundaries.
        """
        balance = starting_capital
        min_balance_seen = starting_capital
        day_bets, day_wins, day_losses, day_abandonments = 0, 0, 0, 0

        # One engine per day — streak state must survive across shoes
        day_engine = StrategyEngine(self.sim_config)
        day_engine.balance = balance

        for shoe_index in range(self.sim_config.max_shoes_per_day):
            shoe_stats = self._run_shoe(day_engine)

            balance = day_engine.balance
            min_balance_seen = min(min_balance_seen, balance)

            day_bets += shoe_stats.total_bets
            day_wins += shoe_stats.wins
            day_losses += shoe_stats.losses
            day_abandonments += shoe_stats.abandonments

            shoes_played = shoe_index + 1
            day_profit = balance - starting_capital
            max_drawdown = starting_capital - min_balance_seen

            if balance >= starting_capital + self.sim_config.daily_profit_target:
                day_result = DayResult(day_number, shoes_played, day_profit, True, False)
                day_stats = DayStats(day_bets, day_wins, day_losses, day_abandonments, max_drawdown)
                return day_result, day_stats

            if balance <= starting_capital - self.sim_config.daily_stop_loss:
                day_result = DayResult(day_number, shoes_played, day_profit, False, True)
                day_stats = DayStats(day_bets, day_wins, day_losses, day_abandonments, max_drawdown)
                return day_result, day_stats

        final_profit = balance - starting_capital
        final_drawdown = starting_capital - min_balance_seen
        day_result = DayResult(day_number, self.sim_config.max_shoes_per_day, final_profit, False, False)
        day_stats = DayStats(day_bets, day_wins, day_losses, day_abandonments, final_drawdown)
        return day_result, day_stats

    def _run_shoe(self, engine: StrategyEngine) -> ShoeStats:
        """
        Plays one shoe of hands through the provided StrategyEngine.

        Accepts an existing engine so that streak state is preserved across
        shoe boundaries within the same day.
        """
        balance_before_shoe = engine.balance
        generated_shoe = self.shoe_generator.generate()

        shoe_bets, shoe_wins, shoe_losses, shoe_abandonments = 0, 0, 0, 0

        for hand_result in generated_shoe.hands:
            suggestion = engine.get_suggestion()
            bet_outcome = engine.process_hand(hand_result, suggestion)

            bet_was_placed = bet_outcome.bet_amount > 0 and not bet_outcome.abandoned
            hand_was_decisive = hand_result != HandResult.TIE

            if bet_was_placed and hand_was_decisive:
                shoe_bets += 1
                if bet_outcome.won:
                    shoe_wins += 1
                else:
                    shoe_losses += 1

            if bet_outcome.abandoned:
                shoe_abandonments += 1

        net_profit = engine.balance - balance_before_shoe
        return ShoeStats(net_profit, engine.balance, shoe_bets, shoe_wins, shoe_losses, shoe_abandonments)

    def _compile_summary(
        self,
        day_results: list[DayResult],
        total_profit: float,
        total_bets: int,
        wins: int,
        losses: int,
        total_abandonments: int,
        max_capital_needed: float,
    ) -> SimulationSummary:
        """Aggregates day results into a final SimulationSummary."""
        num_days = len(day_results)

        winning_days = sum(1 for day in day_results if day.profit > 0)
        losing_days = sum(1 for day in day_results if day.profit < 0)
        breakeven_days = sum(1 for day in day_results if day.profit == 0)

        avg_shoes_per_day = (
            sum(day.shoes_played for day in day_results) / num_days if num_days else 0.0
        )
        avg_profit_per_day = total_profit / num_days if num_days else 0.0

        return SimulationSummary(
            config=self.sim_config,
            starting_capital=self.sim_config.starting_capital,
            final_balance=self.sim_config.starting_capital + total_profit,
            total_profit=total_profit,
            total_bets=total_bets,
            wins=wins,
            losses=losses,
            total_abandonments=total_abandonments,
            day_results=day_results,
            winning_days=winning_days,
            losing_days=losing_days,
            breakeven_days=breakeven_days,
            avg_shoes_per_day=avg_shoes_per_day,
            avg_profit_per_day=avg_profit_per_day,
            total_days=self.sim_config.num_days,
            max_capital_needed=max_capital_needed,
        )
