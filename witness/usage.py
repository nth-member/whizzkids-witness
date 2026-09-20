"""What a run actually cost.

Estimates are for planning; this is for the record.  Every response carries its
own token counts, so a run reports what it spent rather than what it was
expected to spend.  Rates are declared here and stamped onto each run, so a
figure recorded last year is still readable after the rates change.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

# US dollars per million tokens, and per web search.
RATES = {
    "claude-opus-5": {"in": 5.00, "out": 25.00},
    "claude-sonnet-5": {"in": 2.00, "out": 10.00},
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00},
}
CACHE_WRITE_MULTIPLIER = 1.25
CACHE_READ_MULTIPLIER = 0.10
SEARCH_COST = 10.00 / 1000


@dataclass
class Usage:
    """Token counts for one run, and what they cost at the declared rates."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    searches: int = 0
    calls: int = 0
    model: str = ""

    def add_response(self, response, searches: int = 0) -> "Usage":
        """Fold in one API response's reported usage."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return self
        self.input_tokens += getattr(usage, "input_tokens", 0) or 0
        self.output_tokens += getattr(usage, "output_tokens", 0) or 0
        self.cache_write_tokens += getattr(usage, "cache_creation_input_tokens", 0) or 0
        self.cache_read_tokens += getattr(usage, "cache_read_input_tokens", 0) or 0
        self.searches += searches
        self.calls += 1
        if not self.model:
            self.model = getattr(response, "model", "") or ""
        return self

    def merge(self, other: "Usage") -> "Usage":
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cache_write_tokens += other.cache_write_tokens
        self.cache_read_tokens += other.cache_read_tokens
        self.searches += other.searches
        self.calls += other.calls
        self.model = self.model or other.model
        return self

    def cost(self, model: str | None = None) -> float | None:
        """Dollars, or None when the model's rates are not declared here."""
        rates = RATES.get(model or self.model)
        if rates is None:
            return None
        million = 1_000_000
        return (
            self.input_tokens * rates["in"] / million
            + self.cache_write_tokens * rates["in"] * CACHE_WRITE_MULTIPLIER / million
            + self.cache_read_tokens * rates["in"] * CACHE_READ_MULTIPLIER / million
            + self.output_tokens * rates["out"] / million
            + self.searches * SEARCH_COST
        )

    def describe(self, model: str | None = None) -> str:
        spend = self.cost(model)
        money = f"${spend:0.2f}" if spend is not None else "cost unknown for this model"
        return (
            f"{self.calls} calls, {self.searches} searches, "
            f"{self.input_tokens:,} in "
            f"(+{self.cache_read_tokens:,} cached read, {self.cache_write_tokens:,} written), "
            f"{self.output_tokens:,} out — {money}"
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["cost_usd"] = self.cost()
        return data
