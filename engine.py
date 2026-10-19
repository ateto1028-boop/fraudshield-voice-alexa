"""FraudShield Voice: explainable, offline-safe tool-using scam triage agent.
All checks are heuristic educational signals, not definitive fraud findings.
"""
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import re

RULES = [
    (r'\b(otp|one.time password|verification code|2fa|security code|pin)\b', 26, 'Requests a security or verification code'),
    (r'\b(urgent|immediately|within (?:one|1|24) hour|act now|last chance|account suspended)\b', 14, 'Creates artificial urgency'),
    (r'\b(gift card|crypto|usdt|bitcoin|wire transfer|send money|advance fee)\b', 25, 'Requests a hard-to-reverse payment'),
    (r'\b(guaranteed profit|double your money|risk.free return|guaranteed returns)\b', 25, 'Promises unrealistic financial returns'),
    (r'\b(click (?:this |the )?link|verify your account|confirm your identity|unlock your account)\b', 12, 'Pushes an unsolicited verification action'),
    (r'\b(keep (?:this |it )?secret|do not tell|don.t tell|confidential payment)\b', 18, 'Pressures secrecy'),
]
URL_PATTERN = re.compile(r'https?://[^\s<>"\']+|\b(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?', re.I)
SHORTENERS = {'bit.ly', 'tinyurl.com', 't.co', 'is.gd', 'cutt.ly'}


def inspect_message(message: str):
    """Tool #1: find explicitly stated behavioral risk signals."""
    hits = []
    score = 0
    for pattern, weight, description in RULES:
        if re.search(pattern, message, re.I):
            hits.append(description)
            score += weight
    return {'score': score, 'signals': hits}


def inspect_links(message: str):
    """Tool #2: lexical-only link inspection, without visiting the URL."""
    links, signals, score = [], [], 0
    for match in URL_PATTERN.finditer(message):
        raw = match.group(0).rstrip('.,;)')
        parsed = urlparse(raw if raw.startswith(('http://', 'https://')) else 'https://' + raw)
        host = (parsed.hostname or '').lower()
        if not host:
            continue
        links.append(raw)
        if host in SHORTENERS:
            signals.append('Shortened link hides destination')
            score += 22
        if host.startswith('xn--') or '.xn--' in host:
            signals.append('Internationalized/punycode domain warrants scrutiny')
            score += 15
        if parsed.scheme == 'http':
            signals.append('Unencrypted HTTP link')
            score += 8
        if host.count('-') >= 3:
            signals.append('Unusually hyphenated hostname')
            score += 10
    return {'score': score, 'signals': list(dict.fromkeys(signals)), 'links': links}


def recommend_actions(level: str):
    """Tool #3: safe next-step recommendations."""
    advice = ['Verify the request using a known official contact channel, not the message link.']
    if level in ('High', 'Medium'):
        advice.insert(0, 'Do not pay, reveal passwords, or share one-time codes.')
    advice.append('If money or credentials were shared, contact your bank/provider promptly and preserve evidence.')
    return advice


def triage(message: str) -> dict:
    """Local agent chooses and invokes three explicit tools in sequence."""
    message = (message or '').strip()[:8000]
    if not message:
        return {'error': 'Enter a message or link to analyze.'}
    m = inspect_message(message)
    u = inspect_links(message)
    score = min(100, m['score'] + u['score'])
    level = 'High' if score >= 50 else 'Medium' if score >= 20 else 'Low'
    signals = list(dict.fromkeys(m['signals'] + u['signals']))
    if not signals:
        signals = ['No predefined warning pattern detected; this does not establish safety.']
    return {
        'risk_score': score, 'risk_level': level, 'signals': signals,
        'links_detected': u['links'], 'actions': recommend_actions(level),
        'tools_called': ['inspect_message', 'inspect_links', 'recommend_actions'],
        'scope': 'Local heuristic analysis only; no live URL reputation checks or Alexa service connection.',
    }


EXAMPLES = {
    'Suspicious delivery message': 'Urgent: Your parcel is on hold. Verify your account immediately at http://track-parcel-check.example/verify',
    'Investment scam': 'Guaranteed profit! Double your money with USDT. Send money now and keep this secret.',
    'Code theft attempt': 'Your account is suspended. Send your OTP verification code immediately to unlock your account.',
    'Normal reminder': 'Hi, our appointment is tomorrow at 10 AM. Please call the office if you need to reschedule.',
}
