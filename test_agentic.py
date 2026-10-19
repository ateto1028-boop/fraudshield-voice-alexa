"""Run with: python -m unittest test_agentic.py"""
import unittest
from unittest.mock import patch

import agentic

SAMPLE_REPORT = {"risk_score": 10, "risk_level": "Low", "signals": [], "actions": [], "tools_called": []}


class AgentTests(unittest.TestCase):
    def run_agent(self, text):
        with patch.object(agentic, '_baseline_triage', return_value={**SAMPLE_REPORT, 'actions': [], 'tools_called': []}):
            return agentic.triage(text)

    def test_otp(self):
        result = self.run_agent('Send your OTP verification code now')
        self.assertEqual(result['agent_route'], 'credential_request')
        self.assertGreaterEqual(len(result['tools_called']), 4)
        self.assertIn('Never share', ' '.join(result['actions']))

    def test_investment(self):
        result = self.run_agent('Guaranteed investment profit: deposit now')
        self.assertEqual(result['agent_route'], 'investment_offer')
        self.assertIn('Do not transfer', ' '.join(result['actions']))

    def test_normal(self):
        result = self.run_agent('Meeting reminder for 3 PM tomorrow')
        self.assertEqual(result['agent_route'], 'general_message')
        self.assertEqual(result['risk_score'], 10)

    def test_empty(self):
        self.assertIn('error', agentic.triage(''))


if __name__ == '__main__':
    unittest.main()
