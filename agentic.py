"""FraudShield Voice: transparent, deterministic tool-using agent.

This is a *custom agentic tool orchestrator*, not an LLM, Amazon Alexa
integration, official Alexa skill, or Amazon-hosted service.
No external network or credentials are required.

Drop alongside app.py and engine.py; in app.py replace:
    from engine import EXAMPLES, triage
with:
    from engine import EXAMPLES
    from agentic import triage
"""

from __future__ import annotations

import re
from typing import Callable

from engine import triage as _baseline_triage


class FraudShieldAgent:
    """Chooses and calls specialized tools depending on a message's context."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable] = {
            "context_router": self._context_router,
            "baseline_fraud_analysis": self._baseline_fraud_analysis,
            "credential_safety_check": self._credential_safety_check,
            "investment_safety_check": self._investment_safety_check,
            "final_safety_review": self._final_safety_review,
        }

    @staticmethod
    def _context_router(message: str) -> str:
        if re.search(r"\b(otp|verification code|one.time password|passcode|password|pin)\b", message, re.I):
            return "credential_request"
        if re.search(r"\b(invest|investment|profit|guaranteed returns?|crypto|usdt|commission)\b", message, re.I):
            return "investment_offer"
        return "general_message"

    @staticmethod
    def _baseline_fraud_analysis(message: str) -> dict:
        return _baseline_triage(message)

    @staticmethod
    def _credential_safety_check(message: str, report: dict) -> dict:
        danger = bool(re.search(r"\b(send|share|provide|reply|give|forward)\b", message, re.I))
        if danger and re.search(r"\b(otp|verification code|one.time password|passcode|password|pin)\b", message, re.I):
            report.setdefault("actions", [])
            advice = "Never share verification codes or passwords; contact the provider using its official app or website."
            if advice not in report["actions"]:
                report["actions"].append(advice)
        return report

    @staticmethod
    def _investment_safety_check(message: str, report: dict) -> dict:
        if re.search(r"\b(guaranteed|double your|risk.free|urgent|deposit|pay now|withdrawal fee)\b", message, re.I):
            report.setdefault("actions", [])
            advice = "Do not transfer money based on promises of guaranteed profits; independently verify the counterparty."
            if advice not in report["actions"]:
                report["actions"].append(advice)
        return report

    @staticmethod
    def _final_safety_review(report: dict) -> dict:
        # Keep the original engine's risk score and risk level unchanged.
        # The agent adds explanations, not unsupported numerical predictions.
        report.setdefault("actions", [])
        if not report["actions"]:
            report["actions"].append("Verify unexpected requests through a trusted independent channel.")
        return report

    @staticmethod
    def _follow_up(route: str, level: str) -> dict:
        """Generate transparent, safety-oriented conversation choices, never request secrets."""
        if route == "credential_request":
            return {
                "question": "Did you already share a code or password with the sender? Do not enter the code here.",
                "choices": ["No, I did not share it", "Yes, I shared it", "I'm not sure"],
            }
        if route == "investment_offer":
            return {
                "question": "Have you already sent money to this person or platform? Do not enter financial details.",
                "choices": ["No money sent", "Yes, I sent money", "I'm not sure"],
            }
        return {
            "question": "Would you like safer next steps for this message?",
            "choices": ["Show verification steps", "Show warning signs"],
        }

    def run(self, message: str) -> dict:
        if not isinstance(message, str) or not message.strip():
            return {"error": "Please enter a message to inspect."}

        calls: list[str] = []

        route = self._tools["context_router"](message)
        calls.append(f"context_router -> {route}")

        report = self._tools["baseline_fraud_analysis"](message)
        calls.append("baseline_fraud_analysis -> engine.triage")
        if not isinstance(report, dict) or "error" in report:
            return report

        if route == "credential_request":
            report = self._tools["credential_safety_check"](message, report)
            calls.append("credential_safety_check -> advice reviewed")
        elif route == "investment_offer":
            report = self._tools["investment_safety_check"](message, report)
            calls.append("investment_safety_check -> advice reviewed")

        report = self._tools["final_safety_review"](report)
        calls.append("final_safety_review -> response validated")

        # Preserve the existing Streamlit interface's tool-trace field.
        previous = report.get("tools_called", [])
        if not isinstance(previous, list):
            previous = [str(previous)]
        report["tools_called"] = calls + [str(x) for x in previous]
        report["agent_route"] = route
        report["follow_up"] = self._follow_up(route, report.get("risk_level", "Low"))
        return report


def triage(message: str) -> dict:
    """Drop-in, backward-compatible replacement for engine.triage."""
    return FraudShieldAgent().run(message)


def follow_up_advice(report: dict, selection: str) -> str:
    """Handle limited follow-ups without collecting private identifiers or secrets."""
    route = report.get("agent_route")
    if route == "credential_request":
        if selection == "Yes, I shared it":
            return "Immediately change the affected password through the official site, revoke active sessions if available, enable MFA, and contact the provider's fraud team. Never share another code."
        if selection == "No, I did not share it":
            return "Do not reply or share any code. Open the provider's official app independently to check alerts and report the message."
        return "Review account activity in the official app and contact the provider using a verified support channel. Never paste codes here."
    if route == "investment_offer":
        if selection == "Yes, I sent money":
            return "Stop all additional payments, preserve transaction records and messages, and promptly contact your bank, exchange, or payment provider and appropriate authorities. Avoid anyone demanding upfront recovery fees."
        if selection == "No money sent":
            return "Do not transfer funds or pay withdrawal fees. Verify the company and claims independently; guaranteed returns are a warning sign."
        return "Check bank or exchange history through official channels and preserve any relevant evidence. Avoid further payments until verified."
    if selection == "Show warning signs":
        return "Review unsolicited urgency, requests for codes or money, unusual links, secrecy, and guaranteed returns. Absence of these patterns does not establish safety."
    return "Check the request independently using contact details from the official app or website. Do not use links or numbers supplied in the suspicious message."
