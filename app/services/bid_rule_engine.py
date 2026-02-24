from app.models.auction_config import AuctionConfig
from app.engine.increment_engine import IncrementEngine


class BidRuleEngine:

    def __init__(self, config: AuctionConfig):
        self.config = config
        self.rule_config = config.rule_config or {}

    # -------------------------------------------------
    # PUBLIC: Validate Bid
    # -------------------------------------------------
    def validate_bid(
        self,
        current_highest_bid: float,
        new_amount: float,
        team_budget_remaining: float,
        players_owned: int,
    ) -> None:
        """
        Raises Exception if invalid.
        """

        increment_result = IncrementEngine.calculate(
            current_bid=current_highest_bid,
            team_budget_remaining=team_budget_remaining,
            rule_config=self.rule_config,
        )

        allowed_next_bids = increment_result["allowed_next_bids"]
        max_allowed_bid = increment_result["max_allowed_bid"]

        increment_config = self.rule_config.get("increment", {})
        mode = increment_config.get("mode", "OPEN")

        # --------------------------------------------
        # 1️⃣ Basic > current check
        # --------------------------------------------
        if new_amount <= current_highest_bid:
            raise Exception("Bid too low")

        # --------------------------------------------
        # 2️⃣ Increment validation
        # --------------------------------------------
        if mode != "OPEN":
            if new_amount not in allowed_next_bids:
                raise Exception("Invalid increment value")
        else:
            if new_amount > max_allowed_bid:
                raise Exception("Bid exceeds allowed maximum")

        # --------------------------------------------
        # 3️⃣ Hard purse check
        # --------------------------------------------
        if new_amount > team_budget_remaining:
            raise Exception("Insufficient budget")

        # --------------------------------------------
        # 4️⃣ Roster feasibility validation
        # --------------------------------------------
        roster_config = self.rule_config.get("roster", {})
        minimum_squad_size = roster_config.get("minimum_squad_size")
        minimum_player_base_price = roster_config.get("minimum_player_base_price")

        if minimum_squad_size and minimum_player_base_price:

            remaining_budget_after_bid = team_budget_remaining - new_amount
            remaining_slots = minimum_squad_size - (players_owned + 1)

            if remaining_slots > 0:
                minimum_required_budget = (
                    remaining_slots * minimum_player_base_price
                )

                if remaining_budget_after_bid < minimum_required_budget:
                    raise Exception(
                        "Bid would make squad completion impossible"
                    )

        return