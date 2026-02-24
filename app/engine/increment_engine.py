class IncrementEngine:

    @staticmethod
    def calculate(
        current_bid: float,
        team_budget_remaining: float,
        rule_config: dict
    ):

        increment_config = rule_config.get("increment", {})
        limit_config = rule_config.get("limit", {})

        mode = increment_config.get("mode", "OPEN")

        # Step 1 — determine base max allowed bid
        max_allowed_bid = IncrementEngine._calculate_limit(
            current_bid,
            team_budget_remaining,
            limit_config
        )

        # Step 2 — calculate allowed next bids
        if mode == "OPEN":
            # In OPEN mode, any bid above current_bid and <= max_allowed_bid
            return {
                "allowed_next_bids": [],
                "max_allowed_bid": max_allowed_bid
            }

        values = increment_config.get("values", [])

        # Handle threshold logic
        threshold = increment_config.get("threshold", {})
        if threshold.get("enabled"):
            switch_at = threshold.get("switch_at", 0)
            if current_bid >= switch_at:
                values = threshold.get("after_values", values)

        allowed = []

        for inc in values:
            next_bid = current_bid + inc
            if next_bid <= max_allowed_bid:
                allowed.append(next_bid)

        return {
            "allowed_next_bids": allowed,
            "max_allowed_bid": max_allowed_bid
        }

    @staticmethod
    def _calculate_limit(
        current_bid: float,
        team_budget_remaining: float,
        limit_config: dict
    ):

        limit_type = limit_config.get("type", "NONE")

        if limit_type == "NONE":
            return team_budget_remaining

        if limit_type == "ABSOLUTE":
            return min(limit_config.get("value", team_budget_remaining),
                       team_budget_remaining)

        if limit_type == "PERCENT_TOTAL":
            percent = limit_config.get("value", 100)
            return team_budget_remaining * (percent / 100)

        if limit_type == "PERCENT_REMAINING":
            percent = limit_config.get("value", 100)
            return team_budget_remaining * (percent / 100)

        return team_budget_remaining