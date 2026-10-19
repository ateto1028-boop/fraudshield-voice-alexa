FraudShield Voice - tool-using agent upgrade

1. Upload agentic.py and test_agentic.py to the root of the existing GitHub repository.
2. In app.py change the original import:
     from engine import EXAMPLES, triage
   to these two lines:
     from engine import EXAMPLES
     from agentic import triage
3. Commit changes to branch main. Streamlit should redeploy automatically.
4. Test all three demos and verify that the Tool Trace now includes:
     context_router -> ...
     baseline_fraud_analysis -> engine.triage
     credential_safety_check OR investment_safety_check (depending on route)
     final_safety_review -> response validated
5. Confirm report JSON still exports.
6. Add this description to the GitHub README and Devpost project description:
   "FraudShield Voice now uses a custom deterministic, tool-using agent
   orchestrator. It autonomously routes messages to a fraud-analysis tool,
   invokes a context-specific credential or investment safety tool when
   relevant, and performs a final safety review. Execution steps appear in
   the tool trace. It is not an LLM and does not connect to Alexa or AWS."
7. Record/revise the demo video to visibly show the updated tool calls, and
   update the YouTube/Devpost description before Oct 23 deadline.

IMPORTANT: This is a tool-using deterministic agent architecture. The
competition organizers alone decide whether it satisfies their definition of
'an AI or agentic tool'. Do not claim formal eligibility is confirmed.
