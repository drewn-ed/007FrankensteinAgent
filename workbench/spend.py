"""Trusted pre-dispatch monetary admission. Estimates are not provider invoices.

Unknown-price routes fail closed in strict mode. Plan mode is explicitly NOT a
USD guarantee: ChatGPT SIWC exposes no per-request USD ceiling and rejects
max_output_tokens (official preview limitations, checked 2026-10-09).
"""
from decimal import Decimal, InvalidOperation


class SpendError(ValueError):
    pass


def money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise SpendError("The run budget must be a finite, non-negative USD amount.") from None
    if not amount.is_finite() or amount < 0 or amount > 100:
        raise SpendError("The run budget must be between 0 and 100 USD.")
    return amount


class SpendLedger:
    """Retain the entire preauthorized upper bound, even on transport failure.

    Deliberately no refund: missing/late usage cannot reopen a spent reservation.
    Fixed-price/zero-price routes need no tokenizer assumptions. Future priced
    routes must supply a verified provider-enforced upper bound, not an estimate.
    """
    def __init__(self, max_usd="0", policy="strict"):
        self.limit = money(max_usd)
        if policy not in ("strict", "existing_plan"):
            raise SpendError("Unknown spend policy. Choose strict or existing_plan.")
        self.policy = policy
        self.reserved = Decimal("0")
        self.reservations = []
        self.blocked = []

    def reserve(self, upper_bound_usd, *, provider, basis):
        entry = {"provider": provider, "basis": basis}
        if upper_bound_usd is None:
            entry.update(upper_bound_usd=None, admitted=False)
            if self.policy == "existing_plan" and provider == "chatgpt":
                entry.update(admitted=True, guarantee="none; externally managed ChatGPT plan and credits")
                self.reservations.append(entry)
                return entry
            self.blocked.append(entry)
            raise SpendError("Financial limit blocked the request before inference: this provider has no verified per-request USD upper bound. Use a confirmed Gemini Free project or explicitly choose existing_plan mode, which has no local USD guarantee.")
        amount = money(upper_bound_usd)
        entry["upper_bound_usd"] = str(amount)
        if self.reserved + amount > self.limit:
            entry["admitted"] = False
            self.blocked.append(entry)
            raise SpendError("The next model request would exceed the run's financial limit. No request was sent.")
        self.reserved += amount
        entry["admitted"] = True
        self.reservations.append(entry)
        return entry

    def authorize(self, config):
        if config.provider == "gemini" and config.free_confirmed:
            # The operator must keep billing disabled. This is not inferred from
            # an API key, and must not be claimed as a provider billing check.
            from .model import Gemini
            if config.model in Gemini.FREE_MODELS:
                return self.reserve("0", provider="gemini", basis="Operator-confirmed Free tier; billing must remain disabled; no paid fallback")
        return self.reserve(None, provider=config.provider, basis="No verified provider-enforced per-request USD upper bound")

    def snapshot(self):
        return {"policy": self.policy, "max_usd": str(self.limit),
                "reserved_upper_bound_usd": str(self.reserved),
                "guaranteed": not any(x["upper_bound_usd"] is None for x in self.reservations),
                "billing_verified": False,
                "reservations": list(self.reservations), "blocked": list(self.blocked)}


def policy_status(config):
    """Read-only policy preview for UI/admission; never reserves a run or sends HTTP."""
    ledger = None
    try:
        ledger = SpendLedger(config.max_run_usd, config.spend_policy)
        admission = ledger.authorize(config)
        return {"allowed": True, "error": None, "policy": config.spend_policy,
                "max_usd": str(ledger.limit),
                "usd_guarantee": admission['upper_bound_usd'] is not None,
                "billing_verified": False, "basis": admission['basis']}
    except SpendError as error:
        return {"allowed": False, "error": str(error), "policy": config.spend_policy,
                "max_usd": str(ledger.limit) if ledger else None,
                "usd_guarantee": False, "billing_verified": False}
