from app.engine.increment_engine import IncrementEngine


class BidValidator:

    @staticmethod
    def validate(
        amount: float,
        current_bid: float,
        team_budget_remaining: float,
        players_owned: int,
        rule_config: dict
    ):
        increment_result = IncrementEngine.calculate(
            current_bid=current_bid,
            team_budget_remaining=team_budget_remaining,
            rule_config=rule_config
        )

        allowed_next_bids = increment_result["allowed_next_bids"]
        max_allowed_bid = increment_result["max_allowed_bid"]

        increment_config = rule_config.get("increment", {})
        mode = increment_config.get("mode", "OPEN")

        # 1️⃣ Increment Rule
        if mode != "OPEN":
            if amount not in allowed_next_bids:
                raise Exception("Invalid increment value")
        else:
            if amount <= current_bid:
                raise Exception("Bid must be greater than current bid")
            if amount > max_allowed_bid:
                raise Exception("Bid exceeds allowed maximum")

        # 2️⃣ Purse Hard Check
        if amount > team_budget_remaining:
            raise Exception("Insufficient budget")

        # 3️⃣ Roster Feasibility
        roster_config = rule_config.get("roster", {})
        minimum_squad_size = roster_config.get("minimum_squad_size")
        minimum_player_base_price = roster_config.get("minimum_player_base_price")

        if minimum_squad_size and minimum_player_base_price:

            remaining_budget_after_bid = team_budget_remaining - amount
            remaining_slots = minimum_squad_size - (players_owned + 1)

            if remaining_slots > 0:
                minimum_required_budget = remaining_slots * minimum_player_base_price

                if remaining_budget_after_bid < minimum_required_budget:
                    raise Exception(
                        "Bid would make squad completion impossible"
                    )

        return True