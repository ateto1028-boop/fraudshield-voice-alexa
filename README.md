# FraudShield Voice

An Alexa+ inspired scam prevention simulator built with Python and Streamlit for the Amazon Developer Hackathon 2026.
## Updated Tool-Orchestration Workflow

FraudShield Voice now includes a rule-based tool-orchestration module (agentic.py).

The workflow routes messages by context, calls the existing fraud-analysis engine, applies scenario-specific safety checks, and validates the final recommendations.

Three scenarios were manually tested successfully:
- OTP theft: High risk (52/100)
- Normal reminder: Low risk (0/100)
- Investment scam: High risk (68/100)

The application provides a visible tool-execution trace and JSON export.

This is an independent Alexa+-style simulation. It does not use an AI model at runtime or connect to Amazon Alexa or AWS services.


## Optional follow-up conversation (2026-10-20)

The Streamlit demonstration offers a small, deterministic follow-up question after the initial classification. It adapts to credential requests, investment offers and general messages and displays actionable guidance without accepting passwords, codes, account numbers or financial details. This is **not** live Alexa+, a hosted LLM, speech recognition or autonomous reasoning. Baseline risk scores and existing detection rules are unchanged.

Run tests with `python -m unittest discover -v`.
