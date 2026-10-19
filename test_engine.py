import unittest
from engine import triage, inspect_links

class TriageTests(unittest.TestCase):
    def test_code_theft(self):
        r = triage('Urgent, send your OTP verification code immediately to unlock your account')
        self.assertEqual(r['risk_level'], 'High')
        self.assertEqual(len(r['tools_called']), 3)
    def test_normal(self):
        self.assertEqual(triage('Lunch at noon tomorrow')['risk_level'], 'Low')
    def test_payment(self):
        self.assertEqual(triage('Guaranteed profit! Send USDT, keep this secret.')['risk_level'], 'High')
    def test_links(self):
        self.assertTrue(inspect_links('http://bit.ly/offer')['links'])
    def test_blank(self):
        self.assertIn('error', triage('  '))
    def test_range(self):
        self.assertLessEqual(triage('OTP urgent USDT guaranteed profit keep this secret')['risk_score'], 100)

if __name__ == '__main__':
    unittest.main()
